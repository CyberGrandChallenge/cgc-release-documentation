#!/usr/bin/env python

import subprocess
import sys
import argparse
import re
import os
import json
import tempfile
import hashlib
import shutil

CSID_PATTERN = r"[0-9a-f]{8}"
HASH_PATTERN = r"[0-9a-f]{64}"
RB_NAME_PATTERN = r"RB_" + CSID_PATTERN + r"_[0-9a-f]{2}"
POV_NAME_PATTERN = r"POV_" + CSID_PATTERN + r".xml"

temp_dirs = []

class ValidationError(RuntimeError):
    pass


def extract_csid_and_hash(archive_path):
    """
    Returns the name parts or raises ValidationError.
    """
    enc_bundle_name = os.path.basename(archive_path)
    match = re.match(r"^(" + CSID_PATTERN + r")_(" + HASH_PATTERN + r").ar.enc$", enc_bundle_name)
    if not match:
        raise ValidationError("Error: bundle name is not in the correct format")
    else:
        name_csid = match.group(1)
        name_hashval = match.group(2)
        return (name_csid, name_hashval)


def decrypt_solution_bundle(enc_bundle_path, creds_file_path):
    """
    Decrypts into bundle_name using provided credentials into a temp folder or raises
    ValidationError
    Returns path to decrypted archive in a temp directory
    """
    tmpdir = tempfile.mkdtemp()
    temp_dirs.append(tmpdir)

    if not os.path.exists(creds_file_path):
        raise ValidationError("Cannot find credentials file")
    with open(creds_file_path, 'r') as f:
        creds = json.loads(f.read())

    if not os.path.exists(enc_bundle_path):
        raise ValidationError("Cannot find solution bundle %s" % enc_bundle_path)

    enc_bundle_name = os.path.basename(enc_bundle_path)
    # remove .enc
    bundle_name = enc_bundle_name[:-4]
    shutil.copy(enc_bundle_path, os.path.join(tmpdir, enc_bundle_name))

    try:
        cmd = ["openssl", "aes-256-cbc", "-d", "-pass", "pass:%s" % creds['cqe_encryption_key'], 
                "-in", os.path.join(tmpdir, enc_bundle_name), "-out", os.path.join(tmpdir, bundle_name)]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        raise ValidationError("Unexpected return code: %s returned %d" % (cpe.cmd, cpe.returncode))

    return os.path.join(tmpdir, bundle_name)


def verify_archive_hash(archive_path, expected_hashval):
    """
    Verifies that archive_path contents hash to the correct SHA-256 hash, as
    specified by expected_hash.
    Returns True or raises ValidationError
    """
    if not os.path.exists(archive_path):
        raise ValidationError("Cannot find decrypted archive, did decryption fail?")

    m = hashlib.sha256()
    with open(archive_path, 'rb') as f:
        m.update(f.read())
    actual_hashval = m.hexdigest()

    if actual_hashval == expected_hashval:
        return True
    else:
        raise ValidationError("Expected SHA256: %s, actual SHA256: %s" %
                (actual_hashval, expected_hashval))


def check_archive_filenames(bundle_path, csid):
    """
    Check that archive contains reasonably-named members (without extracting)
    Returns (pov_name, rb_name_list) or raises ValidationError
    """

    cmd = ["ar", "t", bundle_path]
    ar_t = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = ar_t.communicate()
    retcode = ar_t.wait()
    if retcode != 0:
        raise ValidationError("Unexpected return code: %s returned %d" % (cmd, retcode))

    # parse output, get rid of trailing newline
    ar_files = [x for x in out.split("\n") if len(x) > 0]
    # verify output is reasonable 
    ar_files.sort()
    
    # this list should now be [POV_, RB_, RB_, RB_...]
    if (len(ar_files) < 2):
        raise ValidationError("Expecting at least one PoV and one RB")

    # check POV first, since it's in the beginning of the sorted list
    pov_name = ar_files.pop(0)
    expected_name = "POV_%s.xml" % csid
    if pov_name != expected_name:
        raise ValidationError("PoV incorrectly named.  Expected %s, got %s" % (expected_name, pov_name))
    
    # next, check replacement binaries
    expected_num_cbs = int(csid[-2:], 16)
    # check number of replacement binaries.  len(ar_files) is OK, since we pop'd POV file already.
    num_cbs = len(ar_files)
    if num_cbs != expected_num_cbs:
        raise ValidationError("Incorrect numer of replacement binaries: expected %d, got %d" % (expected_num_cbs, num_cbs))

    # check replacement binary naming and format
    for index, f in enumerate(ar_files):
        # enumerate starts at 0
        expected_name = "RB_%s_%02x" % (csid, index+1)
        if f != expected_name:
            raise ValidationError("Replacement binary incorrectly named.  Expected %s, got %s" % (expected_name, f))

    # if we got this far, things are reasonably sane
    return (pov_name, ar_files)


def extract_archive(bundle_path, pov_name, binary_names):
    """
    Extract the archive and ensure that only the expected files were created; raises ValidationError on failure
    Returns (pov_path, rb_path_list)
    """
    try:
        tmpdir = tempfile.mkdtemp()
        temp_dirs.append(tmpdir)
        cmd = ["ar", "x", bundle_path]
        subprocess.check_call(cmd, cwd=tmpdir)
    except subprocess.CalledProcessError as cpe:
        raise ValidationError("Error: %s returned %d" % (cpe.cmd, cpe.returncode))

    expected_file_list = []
    expected_file_list.append(pov_name)
    expected_file_list = expected_file_list + binary_names
    expected_file_list.sort()

    actual_file_list = os.listdir(tmpdir)
    actual_file_list.sort()

    if expected_file_list != actual_file_list:
        raise ValidationError("Actual files exracted didn't match files from archive listing")

    pov_path = os.path.join(tmpdir, actual_file_list[0])
    rb_path_list = [os.path.join(tmpdir, x) for x in actual_file_list[1:]]
    return (pov_path, rb_path_list)


def copy_files(output_dir, pov_path, rb_path_list):
    """
    Copy files from temporary location to final output directory
    """
    if not os.path.exists(output_dir):
        raise ValidationError("Output directory not found")

    shutil.copy(pov_path, os.path.join(output_dir, os.path.basename(pov_path)))

    for rb_path in rb_path_list:
        shutil.copy(rb_path, os.path.join(output_dir, os.path.basename(rb_path)))
        
    print "The following submission has been validated:"
    print "\t POV file: ", os.path.join(output_dir, os.path.basename(pov_path))
    for rb in rb_path_list:
        print "\t RB file: ", os.path.join(output_dir, os.path.basename(rb))

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--solution", 
                        help="Solution bundle file produced by cqe-package-solution.py", required=True)
    parser.add_argument("-c", "--creds", 
                        help="JSON file with credentials to use for decrypting the bundle", required=True)
    parser.add_argument("-o", "--output_dir",
                        help="Output directory for results of unpacking", required=True)
    args = parser.parse_args()

    try:
        # 0. verify bundle name (csid_hash.ar.enc).  256 bit hash = 64 hex chars
        print "Parsing bundle name: ", args.solution
        (name_csid, name_hashval) = extract_csid_and_hash(args.solution)

        # 1. decrypt the archive
        print "Decrypting the bundle"
        bundle_path = decrypt_solution_bundle(args.solution, args.creds)

        # 2. verify bundle hash after decryption
        print "Verifying archive hash"
        verify_archive_hash(bundle_path, name_hashval)

        # 3. check files included in the achive
        print "Checking archive content: file names"
        (pov_name, rb_names) = check_archive_filenames(bundle_path, name_csid)

        # 4. extract files from archive
        print "Extracting archive"
        (pov_path, rb_path_list) = extract_archive(bundle_path, pov_name, rb_names)

        # 5. Copy files
        print "Copying files to output directory"
        copy_files(args.output_dir, pov_path, rb_path_list)

        # 6. Print CBList and POVList hashes
        print 'Result List Identifiers:'

        m = hashlib.sha256()
        with open(os.path.join(args.output_dir, os.path.basename(pov_path)), 'rb') as f:
            pov_contents = f.read()
        # FIX POV DTD path, otherwise hashes won't match
        pov_contents = pov_contents.replace("/usr/share/cgc-replay/replay.dtd", "/usr/share/cgc-docs/replay.dtd", 1) 
        if "/usr/share/cgc-docs/replay.dtd" not in pov_contents:
             pov_contents = '<?xml version="1.0" standalone="no" ?>\n' + \
                            '<!DOCTYPE pov SYSTEM "/usr/share/cgc-docs/replay.dtd">\n' + \
                            pov_contents
        m.update(pov_contents)
        print "\t POV List ID: %s, %s" % (name_csid, m.hexdigest())

        hashlist = []
        for rb in rb_path_list:
            with open(os.path.join(args.output_dir, os.path.basename(rb)), 'rb') as f:
                m = hashlib.sha256()
                m.update(f.read())
                hashlist.append(m.digest())

        cb_id = hashlist[0]
        # if we only have 1 cb, things are straightforward
        # otherwise, we need to XOR all the hashes together
        for i in range(1, len(hashlist)):
            cb_id = "".join(chr(ord(x) ^ ord(y)) for x, y in zip(cb_id, hashlist[i]))
        print "\t CB List ID:  %s, %s" % (name_csid, cb_id.encode('hex'))


    except ValidationError as ve:
        sys.exit("Validation failed: %s" % ve.message)

    finally:
        # cleanup the temp directories
        for tmpdir in temp_dirs:
            shutil.rmtree(tmpdir)

