# Building a Challenge Binary

This walk-through will guide you through building a challenge binary.  

All challenge binaries should derive from the service template found in on the CGC VM at /usr/share/cgc-cb/templates/service-template. Begin by making a copy of this directory.

	$ cp -r /usr/share/cgc-sample-challenges/templates/service-template/ /vagrant/my-cb
	$ cd /vagrant/my-cb

The Makefile included in the service-template is already configured to work properly within the CGC development virtual machine. The only changes that are required in the Makefile are to edit the first three lines to replace the AUTHOR_ID, SERVICE_ID, and TCP_PORT with values specific to your new binary. For example

    AUTHOR_ID  = LUNGE
    SERVICE_ID = 00001
    TCP_PORT   = 10000

might become

    AUTHOR_ID  = DDTEK
    SERVICE_ID = 00005
    TCP_PORT   = 31336

## Adding source files

The Makefile is pre-configured to compile all .c files found in both the src and lib sub directories. These directories are also added to the include file path to locate any .h header files that are part of the challenge binary. The recommended division of files is to place boiler plate code such as system call wrappers and standard library functions into the lib directory and files that implement service specific behaviors, including any vulnerabilities, into the src directory.

## PATCHED_<n> macros

Authors must facilitate creation of both a vulnerable and patched version of the CB.  The distinction between the vulnerable and not vulnerable 
version is identified by one or more instances of a preprocessor directive "#ifdef PATCHED_<n>" where the <n> is the PoV number (beginning with 1),
followed by an optional "#else" and "#endif". The purpose of this differentiation is to allow the visualization framework to
automatically distinguish between PoVs. Patched CBs must be **not** be vulnerable to associated PoVs.

The Make process will create both an unpatched, vulnerable binary and a patched, secure binary from a single set of source files.  When building the patched, secure CB, the PATCHED_<n> macros will be defined.  When building the vulnerable, for-release CB, the PATCHED_<n> macros will not be defined.  CB authors must test if the PATCHED_<n> macros are defined to determine which code should be included in a given build. Simple examples of the use of these macros are shown here

    #ifdef PATCHED_1
       fgets(buf, sizeof(buf), stdin);
    #endif

    #ifndef PATCHED_1
       gets(buf);
    #endif

    #ifdef PATCHED_2
       //perform some checks that ensure a vulnerability can not be triggered below
    #endif

## Service Pollers

All challenge binaries must include a service poller generator specification designed to exercise the normal functionality of the challenge binary. Pollers must be designated as "for-release" (poller/for-release directory) for CFE there is no "for-testing" distinction. Note that both the unpatched and patched challenge binary must pass all provided service polls. 
A poll generator must be capable of generating at least 1,000,000 unique service polls. All service polls must conform to replay.dtd. NOTE: replay.dtd differs from cfe-pov.dtd primarily in that cfe-pov.dtd requires a negotiate element and supports submitting Type 2 PoV results. 

## Proofs of Vulnerability

All challenge binaries must include at least one proof of vulnerability (PoV) for each vulnerability contained in the CB. Each PoV must demonstrate that a Type 1 or Type 2 vulnerability may be triggered in a deterministic manner. If a CB contains more than one injected flaw, then PoVs that trigger each flaw must be provided.
XML PoVs conforming to to cfe-pov.dtd must be placed in the pov subdirectory. Source code for binary PoVs must be placed in pov_<n> directories (numbered from n = 1). Refer to submitting-a-cb.md for PoV naming conventions.

## Building the challenge binaries

The default (all) target in the Makefile will cause the "build", "test", and "package" targets to be built. The "build" target will compile and link both a patched and an unpatched version of the CB, placing the "bin" directory (which is created if missing). The "test" target will invoke the cb-replay utility once for each service poller and once for each pov. In order to successfully build the "test" target, the patched and unpatched binaries must successfully pass all service polls, the unpatched CB must generate a core file when replayed with each pov, and the patched binary must not generate a core file when replayed with each pov.  Additionally, the "test" target will cause network traffic to be captured for a replay of any poller in the for-release directory. All generated pcap files will be placed into a pcap directory (which is created if missing).

The provided Makefile is properly configured to utilize the CGC specific tool chain. CGC tool chain items intended to be specifically used with CBs can be found in standard cross-build locations for 'i386-linux-cgc'.  Specifically:

    /usr/i386-linux-cgc/bin/
    /usr/bin/i386-linux-cgc-*

When wishing to use these tools, you must specify the full path to the tool, use the 'long name' for the specific tool in /usr/bin, or prepend the /usr/i386-linux-cgc/bin directory to your path. For instance, objdump can be used in these ways.

The full path for either location of objdump:

    $ /usr/bin/i386-linux-cgc-objdump -f bin/DDTEK_00005
    $ /usr/i386-linux-cgc/bin/objdump -f bin/DDTEK_00005

Using the 'long name' which, because it is in /usr/bin, is already in PATH:

    $ i386-linux-cgc-objdump -f bin/DDTEK_00005

Prepending the location of the i386-linux-cgc tools to PATH:

    $ which objdump
    /usr/bin/objdump
    $ PATH=/usr/i386-linux-cgc/bin:$PATH
    $ which objdump
    /usr/i386-linux-cgc/bin/objdump
    $ objdump -f bin/DDTEK_00005

## SEE ALSO

For information regarding the testing a CB, see testing-a-cb.md

For information regarding the debugging a CB, see debugging-a-cb.md

For information regarding submitting a CB, see submitting-a-cb.md

For information regarding automated generation of polls, see understanding-poll-generators.md

For information regarding using the cb-server, see man cb-server(1)

For support please contact CyberGrandChallenge@darpa.mil
