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
import json
import sys
import os


def download_bundle(event_name, creds_dict, dst="./"):

    # set filename based on event
    filename = event_name + ".ar.gz.enc"

    # connect to S3
    s3 = boto.connect_s3(creds_dict['access_id'], creds_dict['access_key'])
    bucket = s3.get_bucket(creds_dict['distribution_bucket'])

    # download the bundle
    k = Key(bucket)
    k.key = event_name + "/" + filename
    k.get_contents_to_filename(filename)

    return filename
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--creds", help="path to CGC credentials JSON file", type=str, required=True)
    parser.add_argument("-e", "--event_name", help="Event name", type=str, required=True)
    
    args = parser.parse_args()

    # sanity checks
    if not os.path.exists(args.creds):
        sys.exit("Error: cannot find creds file '%s'" % args.creds)

    # load credentials
    creds = json.loads(open(args.creds, "r").read())

    print "bundle downloaded to " + download_bundle(args.event_name, creds)

