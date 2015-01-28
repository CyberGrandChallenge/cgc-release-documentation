#!/usr/bin/env python

#################################################################
# Authentication Requirements
#
# Access Key, Secret Access Key, Solution Bucket and Distribution
# Bucket information should all be provided to you by CGC
# Administration
#
# Software Requirements
#
# Python 2.7.x
# boto [0] for accessing amazon s3
# 
# [0] http://boto.readthedocs.org/en/latest/index.html
#################################################################

import boto
from boto.s3.key import Key
import argparse
import os
import json
import sys
import re
import logging

def submit(creds, encrypted_package, commitment_file, event_name):

    logger = logging.getLogger(__name__)

    # sanity checks
    if not os.path.exists(creds):
        logger.error("cannot find creds file '%s'" % creds)
        sys.exit("Error: cannot find creds file '%s'" % creds)

    if not os.path.exists(encrypted_package):
        logger.error("cannot find the encrypted package")
        sys.exit("Error: cannot find the encrypted package")
    
    if not os.path.exists(commitment_file):
        logger.error("cannot find the commitment file")
        sys.exit("Error: cannot find the commitment file")

    # name check
    if not re.match(r"^[0-9a-f]{8}_[0-9a-f]{64}\.ar\.enc$", encrypted_package):
        logger.error("Encrypted package incorrectly named")
        sys.exit("Error: Encrypted package incorrectly named")

    if not re.match(r"^[0-9a-f]{8}_[0-9a-f]{64}\.txt$", commitment_file):
        logger.error("Commitment file incorrectly named")
        sys.exit("Error: Commitment file incorrectly named")

    if commitment_file[0:-4] != encrypted_package[0:-7]:
        logger.error("Commitment file and encrypted package must be named the same")
        sys.exit("Error: Commitment file and encrypted package must be named the same")

    creds = json.loads(open(creds, "r").read())

    logger.info("Authenticating to Amazon S3...")
    s3 = boto.connect_s3(creds['access_id'], creds['access_key'])
    bucket = s3.get_bucket(creds['submission_bucket'])
    logger.info("complete")

    logger.info("Uploading commitment file...")
    k = Key(bucket)
    k.key = event_name + "/" + commitment_file
    k.set_contents_from_filename(commitment_file)
    logger.info("complete")

    logger.info("Uploading encrypted solution package...")
    k = Key(bucket)
    k.key = event_name + "/" + encrypted_package
    k.set_contents_from_filename(encrypted_package)
    logger.info("complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--creds", 
                        help="path to CGC credentials JSON file", 
                        type=str, required=True)
    parser.add_argument("-p", "--encrypted_package", 
                        help="encrypted package to submit", 
                        type=str, required=True)
    parser.add_argument("-m", "--commitment_file", 
                        help="commitment file for the encrypted package",
                        type=str, required=True)
    parser.add_argument("-e", "--event_name",
                        help="name of the event",
                        type=str, required=True)
    
    args = parser.parse_args()
    submit(args.creds, args.encrypted_package, args.commitment_file, args.event_name)
