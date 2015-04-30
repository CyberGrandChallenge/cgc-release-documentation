#!/usr/bin/env python

import hashlib
import argparse
import os
from boto.s3.key import Key
import boto
import sys
import json

class CGCSubmission:
    def __init__(self, access_id, access_key, bucket, event):
        self.event = event
        self.s3 = boto.connect_s3(access_id, access_key)
        self.bucket = self.s3.get_bucket(bucket)

    def list(self, f=lambda x: x):
        return [i for i in self.bucket.list() if f(i)]

    def verify_submission_on_server(self, local_enc_file):
        if not os.path.exists(local_enc_file):
            raise IOError("Cannot find local encrypted file '%s' to verify with server" % local_enc_file)

        basename = os.path.basename(os.path.normpath(local_enc_file))
        keys = self.list(lambda x: self.event in x.name and basename in x.name)

        if len(keys) != 1:
            raise KeyError("Cannot find file '%s' in bucket for event '%s'" % (basename, self.event))

        m = hashlib.md5()
        m.update(open(local_enc_file, "r").read())
        checksum = m.hexdigest()
        
        return checksum == keys[0].etag[1:-1]
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--creds', help='JSON file with credentials to use for connecting to team submission bucket', required=True)
    parser.add_argument('-e', '--event', help='Event name', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--list_subs', action='store_true', help='List all submissions', required=False)
    group.add_argument('-f', '--enc_archive', help='Local packaged and encrypted archive to verify against submission sent', required=False)
    
    args = parser.parse_args()

    if not os.path.exists(args.creds):
        sys.exit("Error: canot find creds file'%s'" % args.creds)

    creds = json.loads(open(args.creds, 'r').read())
    s3 = CGCSubmission(creds['access_id'], creds['access_key'], creds['submission_bucket'], args.event)

    if args.list_subs:
        keys = s3.list(lambda x: args.event in x.name and '.enc' in x.name)
        for key in keys:
            print key.name, key.etag[1:-1]

    if args.enc_archive:
        try:
            if s3.verify_submission_on_server(args.enc_archive):
                print 'Verified against server:', args.enc_archive
            else:
                print 'Server hash does not match', args.enc_archive
        except Exception as e:
            print str(e)

