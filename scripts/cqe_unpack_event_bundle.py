#!/usr/bin/env python
# This script will unpack an event distribution bundle.

import subprocess
import sys
import argparse
import os
import json

def decrypt_archive(archive_path, password):
    """
    takes an encrypted archive and password and decrypts, returning the
    path to the decrypted archive bundle
    """
    if not os.path.exists(archive_path):
        raise IOError("Cannot find event bundle: %s" % archive_path)

    # remove .enc
    gz_bundle_name = archive_path[:-4]

    cmd = ["openssl", 
           "aes-256-cbc", 
           "-d", 
           "-pass", 
           "pass:%s" % password, 
           "-in", 
           archive_path, 
           "-out", 
           gz_bundle_name]

    subprocess.check_call(cmd)

    return gz_bundle_name

def decompress_archive(archive_path):
    """
    decompresses the archive, given the archive path and returns the
    decompressed archive path
    """

    if not os.path.exists(archive_path):
        raise IOError("Cannot find archive to unpack: %s" % archive_path)

    # remove .gz
    bundle_name = archive_path[:-3]
    cmd = ['gunzip', 
           archive_path]

    subprocess.check_call(cmd)
    return bundle_name

def extract_archive(archive_path):
    """
    extract the contents of the archive file
    """
    if not os.path.exists(archive_path):
        raise IOError("Cannot find uncompressed archive %s" % archive_path)

    cmd = ['ar',
           'x',
           archive_path]

    subprocess.check_call(cmd)

def print_manifest():
    """
    print the contents of the manifest file
    """
    if not os.path.exists("manifest.json"):
        raise IOError("Error: cannot find the manifest.json file; did archive extraction fail?")

    csets = json.loads(open("manifest.json", "r").read())

    print "Challenges in this bundle:"
    for csid in csets:
        print "CSID: ", csid
        print "\tCBs: ", ", ".join(csets[csid]['cbs'])
        if csets[csid]['pcap'] != '':
            print "\tpcap: ", csets[csid]['pcap']
        else:
            print "\tpcap: None"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--event_bundle", 
        help="Event bundle file downloaded from S3", required=True)
    parser.add_argument("-p", "--password", 
        help="Event password to use for decrypting the bundle", required=True)
    args = parser.parse_args()
    
    try:
        decrypted_bundle = decrypt_archive(args.event_bundle, args.password)
        decompressed_archive = decompress_archive(decrypted_bundle)
        extract_archive(decompressed_archive)
        print_manifest()

    except subprocess.CalledProcessError as cpe:
        sys.exit("Error: %s returned %d" % (cpe.cmd, cpe.returncode))



