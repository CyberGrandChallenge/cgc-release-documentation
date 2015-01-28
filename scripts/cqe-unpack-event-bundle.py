#!/usr/bin/env python

# This script will unpack an event distribution bundle.

import subprocess
import sys
import argparse
import re
import os
import json
import logging

def unpack(event_bundle, password):

    logger = logging.getLogger(__name__)

    enc_bundle_name = event_bundle
    # remove .enc
    gz_bundle_name = enc_bundle_name[:-4]
    # remove .gz
    bundle_name = gz_bundle_name[:-3]

    # 1. decrypt the archive
    if not os.path.exists(event_bundle):
        logger.error("cannot find event bundle %s", event_bundle)
        sys.exit("Error: cannot find event bundle %s", event_bundle)
    try:
        cmd = ["openssl", "aes-256-cbc", "-d", "-pass", "pass:%s" % password, 
                "-in", enc_bundle_name, "-out", gz_bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        logger.error("%s return %d" % (cpe.cmd, cpe.returncode))
        sys.exit("Error: %s return %d" % (cpe.cmd, cpe.returncode))

    # 2. decompress the archive
    if not os.path.exists(gz_bundle_name):
        logger.error("cannot find compressed archive %s; did decryption fail?" % gz_bundle_name)
        sys.exit("Error: cannot find compressed archive %s; did decryption fail?" % gz_bundle_name)
    try:
        cmd = ["gunzip", gz_bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        logger.error("%s returned %d" % (cpe.cmd, cpe.returncode))
        sys.exit("Error: %s returned %d" % (cpe.cmd, cpe.returncode))

    # 3. extract files from archive
    if not os.path.exists(bundle_name):
        logger.error("cannot find uncompressed archive %s; did decompression fail?" % bundle_name)
        sys.exit("Error: cannot find uncompressed archive %s; did decompression fail?" % bundle_name)
    try:
        cmd = ["ar", "x", bundle_name]
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as cpe:
        logger.error("%s returned %d" % (cpe.cmd, cpe.returncode))
        sys.exit("Error: %s returned %d" % (cpe.cmd, cpe.returncode))

    # 4. populate (and print?) a map from CSIDs to constituent files
    if not os.path.exists("manifest.json"):
        logger.error("cannot find the manifest.json file; did archive extraction fail?")
        sys.exit("Error:  cannot find the manifest.json file; did archive extraction fail?")

    csets = json.loads(open("manifest.json", "r").read())

    logger.info("Challenges in this bundle:")
    for csid in csets:
        logger.info("CSID: %s" % str(csid))
        logger.info("\tCBs: %s" % ", ".join(csets[csid]['cbs']))
        if csets[csid]['pcap'] != '':
            logger.info("\tpcap: %s" % csets[csid]['pcap'])
        else:
            logger.info("\tpcap: None")

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
    unpack(args.event_bundle, args.password)
