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

    # sanity checks
    if not os.path.exists(args.creds):
        sys.exit("Error: cannot find creds file '%s'" % args.creds)

    if not os.path.exists(args.encrypted_package):
        sys.exit("Error: cannot find the encrypted package")
    
    if not os.path.exists(args.commitment_file):
        sys.exit("Error: cannot find the commitment file")

    # name check
    if not re.match(r"^[0-9a-f]{8}_[0-9a-f]{64}\.ar\.enc$", args.encrypted_package):
        sys.exit("Error: Encrypted package incorrectly named")

    if not re.match(r"^[0-9a-f]{8}_[0-9a-f]{64}\.txt$", args.commitment_file):
        sys.exit("Error: Commitment file incorrectly named")

    if args.commitment_file[0:-4] != args.encrypted_package[0:-7]:
        sys.exit("Error: Commitment file and encrypted package must be named the same")

    creds = json.loads(open(args.creds, "r").read())

    print "Authenticating to Amazon S3..."
    s3 = boto.connect_s3(creds['access_id'], creds['access_key'])
    bucket = s3.get_bucket(creds['submission_bucket'])
    print "complete"

    print "Uploading commitment file..."
    k = Key(bucket)
    k.key = args.event_name + args.commitment_file
    k.set_contents_from_filename(args.commitment_file)
    print "complete"

    print "Uploading encrypted solution package..."
    k = Key(bucket)
    k.key = args.event_name + args.encrypted_package
    k.set_contents_from_filename(args.encrypted_package)
    print "complete"

