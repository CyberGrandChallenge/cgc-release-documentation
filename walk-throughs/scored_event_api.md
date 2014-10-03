# Score Event API Release

## Purpose

This document is for the CGC competitors who are writing custom
programs to interact with CGC game during scored events and CQE.
CGC game servers use
[Amazon S3](http://aws.amazon.com/s3/) [0] for data storage and data
transfer to CGC grading engines. The purpose of this document is to
outline the usage of this system such that a competitor could build
their own tools for submission and retrieval of CGC game files.

Note: A full working script with all the examples from this document is
provided to all competitors of CGC and can be found in the [cgc-release-documentation/scripts directory](http://github.com/CyberGrandChallenge/blob/master/scripts/cqe-client.py).

## Requirements

The requirements below will describe what software and information is
required to connect to CGC servers. Additionally, the notation for all
information used later in this document will be defined here.

### Software Requirements

    * tar, challenge solution folders need to be packaged in a tar file
    * sha256 hashing needs to be FIPS compliant sha256
    * openssl v1.0 for encrypting the challenge solution packages

### CGC Distributed Requirements

**Announcement**: The following information will be delivered to CQE
participants by Nov 17, 2014. Soon after a testing window will be
open.

Keys for Amazon S3:

    This Access ID/Access Key are used for accessing the Amazon S3
    instanced used for downloading and uploading files during and
    before an event. These values will be provided in a single well
    formed file to each competitor. The Bucket name and Event name are
    logical folders within Amazon S3.

    * Access ID (string) 
        Defined as: ${aws access id}

    * Access Key (string)
        Defined as: ${aws access key}

    * Bucket name (string)
        Defined as: ${bucket name}

	* Event name (string)
		Defined as: ${event name}

CGC Encryption Key:

    The public encryption key is used to encrypt the solution package
    prior to submitting to CGC servers. This key is provided in pem
    format by the CGC administrators.

    * SSL Public Key (pem file)
        Defined as: ${cgc encryption key}

Contact the CGC administrators immediately in the event that any of this
information is lost. Additionally, be ready to provide a archive 
of all manifest files you've created.

## Overview

Each team is given an Access ID and an Access Key. These are the
keys used to authenticate with their Amazon S3 bucket. Amazon buckets
are folder like objects with unique names. A limited number of functions
are permitted to use against each bucket: listing, downloading, and
uploading files.

Several languages are supported to interact with Amazon S3 [1]. This
document will provide examples using python [2]. Other languages operate
similarly and documentation for those can be found on Amazon S3's SDK
page [3].

A complete CGC submission script is also provided.

Each competitor will have identical bucket structure as outlined below

    cqe/downloads/
		CGC game files related to CQE
		
    cqe/uploads/
		folder for challenge set solution uploads
		
    cqe/upload_manifest.json
		CGC game server will hash all uploads and
		append to this file. Competitors should check their local hashes
		against what the server received.
	
    test/
		fake challenge set solutions for you to test and verify
		packaging and uploading. These also serve as example for
		packaging. Folder structure is identical to cqe folder above.

    scored_event_<n>/
		Where <n> is a different scored
		event. Functionally and layout are identical to cqe folder but
		created for each scored event.

Note: the parent folders above ("cqe", "scored_event_<n>") represent event names (${event name})

## Basic Functions

### Authentication

Submissions to Amazon S3 servers require three pieces of information
provided by the CGC Administrators: Access ID, Access Key and a Bucket
name.


The snippet below shows a basic connection to Amazon S3.

    import boto
	s3 = boto.connect_s3('${aws access id}', '${aws access key}')
	bucket = s3.get_bucket('${bucket name}')

    ${aws access id} Provided by CGC Administrators

    ${aws access key} Provided by CGC Administrators

	${bucket name} Provided by CGC Administrators

### Download

Users are allowed to download two items during a scored event, the
challenge sets and the upload_manifest.json file.

Downloading requires that you create a key object. Each key object a
method for downloading to the local system.

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${even name}/${file name}
    k.get_contents_to_filename(${local path to download to})

    ${bucket name} name of your bucket. Provided by CGC administrators

    ${file name} full name of the package file to be uploaded (include
    extensions)

    ${source file on local system} local path to where the file should
    be saved

### Upload

Uploading challenge solutions is a multiple step process. Each file
uploaded needs to be packaged in a specific way and uploaded with a
manifest file in order to be processed by the CGC grading system.

Each upload will have a manifest file with the same name as the
challenge solution (${solution name}.txt). The manifest file needs to
contain the challenge binary it is for, hash of encrypted solution
package, and the name of the encrypted solution package.

The manifest **MUST** be uploaded to the game servers first and the
timestamp that is assigned on receipt will be used as the 'official'
time of record for the upload, and is therefore critical in
determining if the submission was correctly received within the bounds
of the game rules

Note: The naming of the manifest file must be the name of your
encrypted package with the extension changed to .txt.  Additionally,
the contents of the manifest file must match the encrypted solution
package. If these don't match the challenge solution will not be
processed.

The process goes in steps

1.	package solution 
2.	compress package
3.	encrypt package
4.	generate manifest file
5.	upload manifest file
6.	upload solution package

#### Packaging

Each challenge solution should be in it's own folder independent of
other solutions generated for the same challenge. The folder structure
needs to be as follows:

    ${solution folder name}/ 
        
        /bin/ 
        
        /pov/

#### Compress package

The entire package folder should be compressed to a single tar file

    tar -cf name.tar.gz ${solution folder name}

#### Encrypt package

The compressed package should now be encrypted with the CGC public key.

    openssl smime -encrypt -aes256 -binary -in ${path to compressed
    package} -out ${name of encrypted package} -outform DER ${cgc
    encryption key}

    ${cgc encryption key} CGC Administrators will provide you with a pem
    file that is used for this encryption step.

#### Generate manifest files

The manifest file is what is parsed to determine what solution files a
user uploaded. The last modified time stamp of this manifest file is
used to determine if a challenge solution should be considered "in
game". There should be one manifest file for each challenge solution
package. If more than one challenge solution exists for a challenge
binary, there needs to be a manifest file generated for each solution.

This file contains one line of comma separated values as follows:

    ${encrypted package name}, ${hash of encrypted package}, ${target
    challenge binary name}

    Manifest files should be named the same as the challenge solution
    except with a .txt extension.
    
    ${encrypted package name} challenge solution name

    ${hash of encrypted package} hash needs to be sha256 (string)

    ${target challenge binary name} name of the challenge binary
    (string)

#### Upload manifest file

Uploading files is similar to downloading files in that you need to
create a key object. Except, now you need to set its value with a set
method.

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${file name}
    k.set_contents_from_filename(${source file on local system})

    ${bucket name} name of your bucket. Provided by CGC administrators

	${event name} name of the scored event folder to upload to, ie
    "cqe"

    ${file name} full name of the package file to be uploaded (include
    extensions)

    ${source file on local system} local path to where the file should
    be saved

Note: This will overwrite the contents of a previous file if the key
names match.

#### Upload solution package

See upload manifest file

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${file name} 
    k.set_contents_from_filename(${source file on local system})

    ${bucket name} name of your bucket. Provided by CGC administrators
	
	${event name} name of the scored event folder to upload to, ie
    "cqe"

    ${file name} full name of the package file to be uploaded (include
    extensions)

    ${source file on local system} local path to where the file should
    be saved

[0]: http://aws.amazon.com/documentation/s3/ 

[1]: http://aws.amazon.com/developers/getting-started/ 

[2]: http://boto.readthedocs.org/en/latest/s3_tut.html 

[3]: https://aws.amazon.com/tools/
