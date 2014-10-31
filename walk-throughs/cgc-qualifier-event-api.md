# CGC Qualifier Event API Release

## Release Notes

10/24/2014  
- v1.1  Updates based on competitor feedback:
    * Clarified naming conventions
    * Simplified solution commitment process
    * Switched to symmetric encryption to enable solution package
      verification by competitors

10/03/2014  
- v1.0  Initial release


## Purpose

This document describes distribution of challenges and submission of CRS
responses during CQE and preceding Scored Events. 

[Amazon S3](http://aws.amazon.com/s3/) [0] will be used for data storage and data
transfer to CQE grading system. A full working script with all the examples
from this document will be provided to all CGC competitors.  The
publicly-released DECREE VM will contain all the pre-requisites for packaging
solutions and extracting challenge set bundles.

The purpose of this document is to outline the usage of this system
such that a competitor could, if desired, build an alternative implementation of 
challenge retrieval and response submission.  

NB:  only scripts provided by DARPA will be officially supported.

## Requirements

The requirements below describe software and information needed to connect 
to CQE distribution and submission system.  Additionally, notation for all
information used later in this document is defined in this sections.

### Software Requirements

    * GNU ar to package challenge solutions.  An acceptable version is installed on
      the DECREE VM in /usr/bin/ar.
    * GNU gunzip to uncompress the challenge set bundle.  An acceptable version
      is installed on the DECREE VM in /bin/gunzip.
    * openssl for hashing and encrypting the challenge solution packages, as
      well as decrypting the challenge set bundle.
      An acceptable version is installed on the DECREE VM in /usr/bin/openssl.

### CQE Credentials

The following values will be provided in a single well-formed JSON file to each competitor:

    This Access ID/Access Key are used for authenticated access to the Amazon S3
    instance, enabling download of challenges (before the event) and upload of solution bundles (during the event).

    * Access ID (string) 
        Defined as: ${access_id}

    * Access Key (string)
        Defined as: ${access_key}

    Bucket names (unique per competitor) and Event names are logical folders within Amazon S3.

    * Distribution bucket name (string)
        Defined as: ${distribution_bucket}

    * Submission bucket name (string)
        Defined as: ${submission_bucket}

    The per-team encryption key is used to encrypt the solution package prior to submitting to S3.
    This key will be provided by the CGC administrators to each competitor.

    * CQE Encryption Key (string)
        Defined as: ${cqe_encryption_key}

NOTE: these keys and credentials are team-specific and enable the team to
authenticate to the CGC scoring infrastructure.  It is your responsibility to
keep these values confidential.  In the event that any of this information is lost or compromised,
contact the CGC administrators immediately.  Be prepared to provide an archive 
of all commitment files (see [Generate Commitment File]) that the team has uploaded for this event. 

Separate from the credentials listed above, the event password required to decrypt
the distribution package will be simultaneously distributed to all CGC competitors at the start of a scored event.

    * Event Password (string)
        Defined as: ${event password}


## Overview

Each team is given an Access ID and an Access Key, which are 
used to authenticate to the team-specific Amazon S3 buckets (a folder-like
structure).  

Each team will have two buckets with limited permissions:  

* Distribution bucket - used for retrieving the challenge set bundle for each event.
  Only "list" and "download" operations will be allowed on this bucket.

  The distribution bucket will have the following contents:

    test_event.ar.gz.enc
        A password-protected test challenge set bundle.
        The password is "CyberGrandChallenge".

    scored_event_1.ar.gz.enc
        A password-protected challenge set bundle for Scored Event 1.  
        A password will be distributed to all CGC teams simultaneously at the start of the event.

    scored_event_2.ar.gz.enc
        A password-protected challenge set bundle for Scored Event 2.
        A password will be distributed to all CGC teams simultaneously at the start of the event.

    cgc_qualifier_event.ar.gz.enc
        A password-protected challenge set bundle for CGC Qualifier Event.
        A password will be distributed to all CGC teams simultaneously at the start of the event.

* Submission bucket - used for uploading solution packages.
  Only "list", "download", and "upload" operations will be allowed on this bucket.

  The submission bucket will have the following contents:

    test_event/
            Folder for testing challenge set solution and commitment file uploads.
            This folder will be available and intended for testing solution uploads 
            between scored events.

    scored_event_1/
            Folder for challenge set solution and commitment files for Scored Event 1.

    scored_event_2/
            Folder for challenge set solution and commitment files for Scored Event 2.

    cgc_qualifier_event/
            Folder for challenge set solution and commitment files for CGC Qualifier Event.

Note: in code examples, ${event name} refers to an event folder above (e.g. "scored\_event\_1").


## Example scripts

Several example scripts have been provided [on github](https://github.com/CyberGrandChallenge/cgc-release-documentation/tree/master/scripts). These example scripts rely on the boto python package which may be installed by:

    sudo pip install boto


## Basic Functions
Several languages are supported to interact with Amazon S3 [1].
This document will provide examples using python [2]. Other languages operate similarly
and documentation for those can be found on Amazon S3's SDK page [3].

### Authentication

Accessing Amazon S3 servers requires three pieces of information
provided by the CGC Administrators: Access ID, Access Key, and a Bucket
name.

The code below shows how to setup a basic connection to Amazon S3:

    import boto
    s3 = boto.connect_s3('${access_id}', '${access_key}')
    bucket = s3.get_bucket('${bucket name}')

where:

    ${access_id}, ${access_key}, and ${bucket name} are provided 
    to each team by CGC Administrators and described in [CQE Credentials].

### Download

Downloading requires creation of a key object, which contains a
method for downloading to the local system.  

Continuing from the example above:

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${file name}
    k.get_contents_to_filename(${local file path})

where:

    ${bucket name} name of distribution or submission bucket provided by CGC administrators.
    ${file name}   full name of the file to be downloaded (include extensions)
    ${local file path} path to local file where the contents should be saved

For example, to retrieve a test\_event challenge set bundle, use the following settings:

    ${bucket name} = ${distribution_bucket}
    k.key = "test_event/test_event.ar.gz.enc"


### Upload

Uploading files is similar to downloading files and is also performed via a key object,
except using the set\_contents\_from\_filename() instead of get\_contents\_to\_filename() method.

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${file name}
    k.set_contents_from_filename(${local file path})

where:

    ${bucket name} name of distribution or submission bucket provided by CGC administrators.
    ${file name}   full name of upload destination file (include extensions)
    ${local file path} path to local file to be uploaded

Note: This operation will overwrite the contents of a previous file in S3 if the key
names match.

To upload a test\_event challenge set bundle, use the following settings (see
[Submit Challenge Solution] for naming convention):

    ${bucket name} = ${submission_bucket}
    k.key = "test_event/${csid}_${hash}.ar.enc"


## Retrieving challenge set bundle

Each challenge bundle will be provided in a single encrypted, compressed
archive in the competitors distribution bucket.  To retrieve the challenges,
follow these steps:

* To retrieve the encrypted challenge bundle, follow instructions in [Download]
  section to retrieve the file named ${event name}.ar.gz.enc from the S3 bucket
  named ${distribution\_bucket}.

    The example script can also be used:

        cqe-fetch-event-bundle.py -c "${json filename}" -e "${event name}"

      Where:

          ${json filename} filename of the JSON credentials file
          ${event name} is name of the scored event folder 

      For example:

          cqe-fetch-event-bundle.py -c test1234-cqe-credentials.json -e test_event

* Transfer the downloaded bundle into a DECREE VM.

* To decrypt the challenge bundle, run the following command in the DECREE VM:

        /usr/bin/openssl aes-256-cbc -d -pass "pass:${event password}" \
                         -in "${event name}.ar.gz.enc" -out "${event name}.ar.gz"

    where:

        ${event password} is the password provided by CGC administrators for this event

        ${event name}.ar.gz will now contain the compressed challenge bundle. 


    The unbundling operations may be performed with the example script:

        cqe-unpack-event-bundle.py -p "${event password}" -e "${event name}".ar.gz.enc

    Where:

        ${event password} is the password provided by CGC administrators for this event
        ${event name} is name of the scored event folder 

    For example:

        cqe-unpack-event-bundle.py -p CyberGrandChallenge -e test_event.ar.gz.enc

* To uncompress the challenge bundle, run the following command in the DECREE VM:

        /bin/gunzip "${event name}.ar.gz"
  
* To extract the challenge bundle, run the following command in the DECREE VM:

        /usr/bin/ar x "${event name}.ar"


The resulting set of files will be as follows.  For each challenge included in this challenge bundle,
the extracted file set will contain:

* A CGC challenge binary named ${csid}_${xx}, where
    - ${csid} is an 8-digit hex identifier
    - ${xx} is a 2-digit, 0-padded hex identifier
  For non-IPC challenges, ${xx} will be "01".  If the challenge is an IPC challenge, there will be several binaries,
  named ${csid}_01, ${csid}_02, etc.

* A pcap file named ${csid}.pcap containing captured network traffic for
  selected polls for this challenge binary (see poller/for-release
  directory in the example challenges).
  NOTE:  it is not an error for ${csid}.pcap to be missing.

Event bundle will also include a JSON manifest file named "manifest.json" mapping ${csid} to names of associated challenge binaries and pcap.
An example manifest for 2 challenges might be:

    {'cabeef01': {'cbs': ['cabeef01_01'], 'pcap': 'cabeef01.pcap'},
     'cab00f03': {'cbs': ['cab00f03_01', 'cab00f03_02', 'cab00f03_03'], 'pcap': ''}}

${csid} is the identifier that shall be used for naming corresponding
replacement binaries, PoVs, and commitments associated with this challenge.



## Submit challenge solution

Uploading challenge solutions is a multi-step process. Each solution
must be packaged and named in a specific way to be processed by the CGC grading system.

Each uploaded solution must have a zero-length commitment file that specifies the name of
the challenge and the hash of the solution package in its filename.  The name
of this file will determine what solution package is downloaded and graded.

The commitment **MUST** be uploaded first; the timestamp of this upload will be used as 
the 'official' time of record for the solution upload and is therefore critical in determining
if the submission is correctly received within the bounds of the event duration.

The process for submitting a solution is outlined below:

1. package solution 
2. generate commitment file
3. encrypt solution package
4. upload commitment file
5. upload solution package

#### Package solution

A challenge solution consists of a replacement binary (multiple binaries if this
challenge is an IPC challenge) and a PoV.  The number of replacement binaries
must match the number of original binaries in the challenge, and each solution
package must include a single PoV.  If CRS has not generated a PoV, the
provided empty\_pov.xml may be used as a stand-in.

The naming must follow the spec below for the challenge solution to be graded.  
${csid} is the name of the challenge set to which this solution applies.

To package the solution, execute the following command in the DECREE VM:
    
    * For single-binary challenge
        /usr/bin/ar rcSD ${csid}.ar RB_${csid}_01 POV_${csid}.xml

    * For IPC challenge
        /usr/bin/ar rcSD ${csid}.ar RB_${csid}_01 RB_${csid}_02 ... POV_${csid}.xml

where:
    ${csid} is the name of the challenge set to which this solution applies
    RB_${csid}_${xx} is the replacement binary (increment ${xx} for IPC case)
    POV_${csid}.xml is the PoV for this challenge 

Resulting solution package file should be named ${csid}.ar.

NOTE:  components of the solution package file **MUST** be named as above in
order for the solution package to be accepted.

The example script may be used to package up a challenge solution:

    cqe-package-solution.py -c "${json filename}" -n ${csid} -p POV_${csid}.xml -f RB_${csid}_${xx} [-f RB_${csid}_${xx+1} ...]

  Where:

      ${json filename} filename of the JSON credentials file
      ${csid} is the name of the challenge set to which this solution applies
      RB_${csid}_${xx} is the replacement binary (increment ${xx} for IPC case)
      POV_${csid}.xml is the PoV for this challenge 

  For example:

      cqe-package-solution.py -c test1234-cqe-credentials.json -n cab00f01 -p POV_cab00f01.xml -f RB_cab00f01_01


#### Generate commitment file

Before submitting the solution, a commitment file must be uploaded
to prove time of completion for the challenge solution.  
The naming of the commitment file is also critical in determining 
which challenge solution will be downloaded and graded.

To generate a commitment file, execute the following commands in the DECREE VM:

    ${hash} = `openssl sha256 ${csid}.ar | cut -d' ' -f2 -`
    touch ${csid}_${hash}.txt

where:

    ${hash} The sha256 hash of the *un-encrypted* solution package
    ${csid} The name of the challenge set

The resulting commitment file is ${csid}_${hash}.txt. This file is generated as a result of the above cqe-package-solution.py example.

#### Encrypt solution package

The solution archive package should now be encrypted with the CQE encryption key and 
named to match the commitment filename generated in the previous step.

To perform this, execute the following command in the DECREE VM:

    /usr/bin/openssl aes-256-cbc -pass "pass:${cqe_encryption_key}" \
                     -in ${csid}.ar -out ${csid}_${hash}.ar.enc

where:

    ${cqe_encryption_key} is a per-team key provided by CGC administrators (see [CQE Credentials]).
    ${csid} is the name of the challenge set
    ${hash} is the sha256 hash of the *un-encrypted* solution package (see [Generate commitment file])

Resulting encrypted solution package file ${csid}_${hash}.ar.enc is ready for upload. This file is generated as a result of the above cqe-package-solution.py example.

#### Upload commitment file

Transfer the encrypted solution package from a DECREE VM to an
Internet-connected machine.  Note that this step *MUST* complete before upload of the solution file.

The following code shows how to upload the commitment file:

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${csid}_${hash}.txt
    k.set_contents_from_filename(${path to commitment file})

where:

    ${bucket name} is the name of the submission bucket
    ${event name} is name of the scored event folder 
    ${path to commitment file} local path to commitment file
    ${hash} is the sha256 hash of the *un-encrypted* solution package (see [Generate commitment file])


The example script may be used to upload the solution:

    cqe-submit-solution.py -c "${json filename}" -p "${event name}/${csid}_${hash}.ar.enc" -m "${event name}/${csid}_${hash}.txt" -e "${event name}"

  Where:

      ${json filename} filename of the JSON credentials file
      ${event name} is name of the scored event folder 
      ${csid} is the name of the challenge set to which this solution applies
      ${hash} is the sha256 hash of the *un-encrypted* solution package (see [Generate commitment file])

  For example:

      cqe-submit-solution.py -c test1234-cqe-credentials.json -p cab00f01_1b81e796a04fd7cfd6ff138ffc1c68fc8c9e1cc4a5a52d230542fc946f708cea.ar.enc -m cab00f01_1b81e796a04fd7cfd6ff138ffc1c68fc8c9e1cc4a5a52d230542fc946f708cea.txt -e test_event

Now the solution package can be uploaded.

#### Upload solution package

The following code shows how to upload the solution package.  Note that this
must be performed *AFTER* the corresponding commitment file has been uploaded:

    bucket = s3.get_bucket(${bucket name}) 
    k = Key(bucket) 
    k.key = ${event name}/${csid}_${hash}.ar.enc
    k.set_contents_from_filename(${path to solution package})

where:

    ${bucket name} is the name of the submission bucket
    ${event name} is name of the scored event folder 
    ${hash} is the sha256 hash of the *un-encrypted* solution package (see [Generate commitment file])
    ${path to solution package} local path to solution package 



The upload of the solution package will have been performed by the cqe-submit-solution.py example script.

This completes the solution package submission process.


[0]: http://aws.amazon.com/documentation/s3/ 

[1]: http://aws.amazon.com/developers/getting-started/ 

[2]: http://boto.readthedocs.org/en/latest/s3_tut.html 

[3]: https://aws.amazon.com/tools/

[4]: http://www.w3.org/TR/NOTE-datetime
