#!/usr/bin/env python

# This script will unpack an event distribution bundle.

import subprocess
import sys
import argparse
import re
import os
import json

if __name__ == "__main__":
    #
    # Here's what we need to do:
    #
    # 1. Decrypt the compressed archive with event password provided
    # 2. Decompress the archive
    # 3. Extract the files from the archive
    # 4. Populate (and print?) a map from CSIDs to constituent files
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--event_bundle", 
                        help="Event bundle file downloaded from S3", required=True)
    parser.add_argument("-p", "--password", 
                        help="Event password to use for decrypting the bundle", required=True)
    args = parser.parse_args()


    enc_bundle_name = args.event_bundle
    # remove .enc
    gz_bundle_name = enc_bundle_name[:-4]
    # remove .gz
    bundle_name = gz_bundle_name[:-3]

    # 1. decrypt the archive
    if not os.path.exists(args.event_bundle):
        sys.exit("Error: cannot find event bundle %s", args.event_bundle)
    try:
        cmd = ["openssl", "aes-256-cbc", "-d", "-pass", "pass:%s" % args.password, 
                "-in", enc_bundle_name, "-out", gz_bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        sys.exit("Error: %s return %d" % (cpe.cmd, cpe.returncode))

    # 2. decompress the archive
    if not os.path.exists(gz_bundle_name):
        sys.exit("Error: cannot find compressed archive %s; did decryption fail?" % gz_bundle_name)
    try:
        cmd = ["gunzip", gz_bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        sys.exit("Error: %s returned %d" % (cpe.cmd, cpe.returncode))

    # 3. extract files from archive
    if not os.path.exists(bundle_name):
        sys.exit("Error: cannot find uncompressed archive %s; did decompression fail?" % bundle_name)
    try:
        cmd = ["ar", "x", bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        sys.exit("Error: %s returned %d" % (cpe.cmd, cpe.returncode))

    # 4. populate (and print?) a map from CSIDs to constituent files
    if not os.path.exists("manifest.json"):
        sys.exit("Error:  cannot find the manifest.json file; did archive extraction fail?")

    csets = json.loads(open("manifest.json", "r").read())

    print "Challenges in this bundle:"
    for csid in csets:
        print "CSID: ", csid
        print "\tCBs: ", ", ".join(csets[csid]['cbs'])
        if csets[csid]['pcap'] != '':
            print "\tpcap: ", csets[csid]['pcap']
        else:
            print "\tpcap: None"

