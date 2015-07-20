# Testing a Challenge Binary

This walk-through will guide you through testing a challenge binary.  

Challenge binary authors are required to provide automated verification of their challenge binaries, verifying the functionality and vulnerabilities contained within their submissions.  In CFE, it is required that polls be generated using a poll generator capable of generating at least 1,000,000 unique polls (See understanding=poll-generators.md for more information on this specification). PoVs may be expressed using XML conforming to cfe-pov.dtd or in the form of a CGC binary.

Each of these commands assume a CWD within a DECREE environment with the cgc-sample-challenges package installed.  Before starting, change the current working directory to the following:

    /usr/share/cgc-sample-challenges/templates/service-template

## Testing a CB
The CB build process provides mechanisms for testing challenge binaries during the build-process.  However, it may be beneficial to test the binaries in a more manual fashion.

Use 'cb-test' to run the tests in the same fashion as performed by the build process.  This is done via the commands:

    $ sudo cb-test --port 10000 --cb LUNGE_00001 --xml poller/for-release/service-1.xml --directory bin

This command will test the challenge binary 'LUNGE_00001' in the directory 'bin', using the XML file 'poller/for-release/service-1.xml', on TCP port 10000.  The results of the test will be printed to STDOUT in the TAP format.  

This should result in the following output:

    # command line: /usr/bin/cb-test --port 10000 --cb LUNGE_00001 --xml poller/for-release/service-1.xml --directory bin
    # launching poll-validate poller/for-release/service-1.xml
    # launching cb-server --insecure -p 10000 -d bin LUNGE_00001
    # launching cb-replay --host 127.29.173.154 --port 10000 poller/for-release/service-1.xml
    # service - poller/for-release/service-1.xml
    ok 1 - slept 0.010000
    ok 2 - set values: 'it_is_hello'
    ok 3 - set values: 'my_name'
    # received 5468697320696d706c656d656e747320612073696d706c65206563686f
    ok 4 - match: string
    ok 5 - set foo to 5468697320696d706c65
    # received 20736572766963650a
    ok 6 - match: string
    ok 7 - set bar to 20736572766963650a
    # writing: 68656c6c6f2074686572650a
    ok 8 - write: sent 12 bytes
    # received 68656c6c6f2074686572650a
    ok 9 - match: string
    # writing: 48656c6c6f206d6f6d0a
    ok 10 - write: sent 10 bytes
    # received 48656c6c6f206d6f6d0a
    ok 11 - match: string (expanded from 'it_is_hello')
    ok 12 - match: string
    # writing: 48656c6c6f206461640a
    ok 13 - write: sent 10 bytes
    ok 14 - bytes received
    # received 48656c6c6f206461640a
    ok 15 - match: string
    ok 16 - match: pcre
    ok 17 - match: string
    # writing: 48656c6c6f20736973746572
    ok 18 - write: sent 12 bytes
    ok 19 - bytes received
    # received 48656c6c6f2073697374
    ok 20 - match: not string
    # variables at end of interaction:
    # 'bar' : ' service\n'
    # 'my_name' : 'hello there'
    # 'it_is_hello' : 'Hello'
    # 'foo' : 'This imple'
    # passed: 20
    # failed: 0
    # total passed: 20
    # total failed: 0
    # terminating cb-server

## Running the tests by hand
The 'cb-test' tool runs a number of commands under the hood that may be beneficial to run manually.

### Running a TCP Listener
To run an inetd-style TCP listener for a challenge binary, use the cb-server tool.

    $ cb-server --insecure -p 10000 -d bin LUNGE_00001

This command will create a TCP listener on port 10000 that spawns an instance of /bin/echo upon incoming connections without any security restrictions.

Each connection should result in output similar to the following output:

    connection from: 127.0.0.1:33170

### Validate the syntax of a POV or Poll
To validate a POV or Poll follows the XML DTD, use the 'poll-validate' command.

    $ poll-validate pov/*.xml

This command will validate all files ending in .xml in the pov directory follow the DTD specification for POVs.

This should result in no output, provided the XML files follow the DTD specification.  Any errors should be identified and resolved.

### Test a POV or POLL against a service
To test the efficacy of a POV or POLL against a service, use the 'cb-replay' command.

    From one 'vagrant ssh' window
    $ cd /usr/share/cgc-sample-challenges/templates/service-template
    $ cb-server --insecure -p 10000 -d bin LUNGE_00001

    From another 'vagrant ssh' window
    $ cd /usr/share/cgc-sample-challenges/templates/service-template
    $ cb-replay --host 127.0.0.1 --port 10000 poller/for-release/service-1.xml poller/for-release/service-2.xml

This command will test the challenge binary listening on port '10000' on the IP address '127.0.0.1' with the Poll/POVs 'poller/for-release/service-1.xml' and 'poller/for-release/service-2.xml'.

This should result in the following output:

    # service - poller/for-release/service-1.xml
    ok 1 - slept 0.010000
    ok 2 - set values: 'it_is_hello'
    ok 3 - set values: 'my_name'
    # received 5468697320696d706c656d656e747320612073696d706c65206563686f
    ok 4 - match: string
    ok 5 - set foo to 5468697320696d706c65
    # received 20736572766963650a
    ok 6 - match: string
    ok 7 - set bar to 20736572766963650a
    # writing: 68656c6c6f2074686572650a
    ok 8 - write: sent 12 bytes
    # received 68656c6c6f2074686572650a
    ok 9 - match: string
    # writing: 48656c6c6f206d6f6d0a
    ok 10 - write: sent 10 bytes
    # received 48656c6c6f206d6f6d0a
    ok 11 - match: string (expanded from 'it_is_hello')
    ok 12 - match: string
    # writing: 48656c6c6f206461640a
    ok 13 - write: sent 10 bytes
    ok 14 - bytes received
    # received 48656c6c6f206461640a
    ok 15 - match: string
    ok 16 - match: pcre
    ok 17 - match: string
    # writing: 48656c6c6f20736973746572
    ok 18 - write: sent 12 bytes
    ok 19 - bytes received
    # received 48656c6c6f2073697374
    ok 20 - match: not string
    # variables at end of interaction:
    # 'bar' : ' service\n'
    # 'my_name' : 'hello there'
    # 'it_is_hello' : 'Hello'
    # 'foo' : 'This imple'
    # passed: 20
    # failed: 0
    # service - poller/for-release/service-2.xml
    ok 1 - slept 0.025000
    # received 5468697320696d706c656d656e747320612073696d706c65206563686f20736572766963650a
    ok 2 - match: string
    ok 3 - slept 0.010000
    ok 4 - write: sent 10 bytes
    ok 5 - slept 0.010000
    # received 48656c6c6f206d6f6d0a
    ok 6 - match: string
    ok 7 - slept 0.010000
    ok 8 - write: sent 10 bytes
    ok 9 - slept 0.010000
    # received 48656c6c6f206461640a
    ok 10 - match: string
    # passed: 10
    # failed: 0
    # total passed: 30
    # total failed: 0

## SEE ALSO

For information regarding the TAP Format, see <http://testanything.org/>

For support please contact CyberGrandChallenge@darpa.mil
