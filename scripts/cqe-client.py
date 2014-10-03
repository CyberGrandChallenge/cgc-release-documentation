#!/usr/bin/env python
#
# This script serves as the reference implementation to interact with the
# Cyber Grand Challenge scored events and CQE infrastructure.
#
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
import subprocess
import argparse
import os
import hashlib

class CGCComm:
    """
    CGCComm supports communication with the CGC submission and
    distribution infrastructure. See API for details.
    """
    
    def __init__(self, access_id, access_key, bucket_name, event_folder):
        self.access_id = access_id
        self.access_key = access_key
        self.bucket_name = bucket_name
        self.event_folder = event_folder
        
        self.s3 = boto.connect_s3(self.access_id, self.access_key)
        self.bucket = self.s3.get_bucket(self.bucket_name)

    def upload(self, src, dst):
        k = Key(self.bucket)
        k.key = self.event_folder + "/" + dst
        k.set_contents_from_filename(src)

    def download(self, src, dst):
        k = Key(self.bucket)
        k.key = self.event_folder + "/" + src
        k.get_contents_to_filename(dst)

class CGCPackage:
    """
    Package, encrypt and generate solution manifest file.
    """

    @staticmethod
    def verify(solution_folder):
        """
        Placeholder. Any pre packaging verification can be done here
        """
        pass
    
    @staticmethod
    def package(solution_folder, key_path):
        CGCPackage.verify(solution_folder)
        pkg_name = os.path.basename(os.path.normpath(solution_folder))
        pkg_name_ext = "%s.tar.gz" % pkg_name
        pkg_name_ext_s = "%s.ssl" % pkg_name_ext
        
        subprocess.check_call(["tar", "--format=ustar", "-cf",
                               pkg_name_ext, solution_folder])
        subprocess.check_call(["openssl", "smime", "-encrypt",
                               "-aes256", "-binary", "-in", pkg_name_ext, "-out", "./" +
                               pkg_name_ext_s, "-outform", "DER", key_path])

        m = hashlib.sha256()
        m.update(open(pkg_name_ext_s, "rb").read())
        hash = m.hexdigest()

        ret = (pkg_name, pkg_name_ext_s, hash)
        f = open("%s.txt" % pkg_name_ext_s, "w")
        f.write("%s,%s,%s" % ret)
        f.close()
        return ret

class CGCCheck(CGCComm):
    
    def __init__(self, access_id, access_key, bucket_name, event_folder):
        CGCComm.__init__(access_id, access_key, bucket_name, event_folder)
        
    def downloadServerManifest(dst):
        self.download("manifest.json", dst)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--access_id", help="Access ID",
                        type=str, required=True)
    parser.add_argument("-p", "--access_key", help="Access Key",
                        type=str, required=True)
    parser.add_argument("-b", "--bucket", help="Bucket name",
                        type=str, required=True)
    parser.add_argument("-e", "--event_name", help="Event name",
                        type=str, required=True)
    parser.add_argument("-s", "--solution_folder", help="Solution folder path", 
                        type=str, required=True)
    parser.add_argument("-k", "--encryption_key", help="Encryption key (pem file)", 
                        type=str, required=True)
    
    args = parser.parse_args()
    
    package = CGCPackage.package(args.solution_folder, args.encryption_key)

    comm = CGCComm(args.access_id, args.access_key, args.bucket, args.event_name)
    comm.upload(package[1] + ".txt", package[1] + ".txt")
    comm.upload(package[1], package[1])
    
    
