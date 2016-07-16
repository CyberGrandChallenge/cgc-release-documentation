# Submitting a Challenge Binary

This walk-through is targeted at the performers under contract to create Challenge Binaries (CBs) for the Cyber Grand Challenge. This walk-through will guide CB authors through submitting a completed challenge binary. Here they will also find details of the challenge binary acceptance criteria including how submissions will be assessed and feedback processes for remediation. CGC competitor teams may also be interested in this guidance to CB authors.

## Differences between CQE vs CFE

- A flag page containing random contents exists at known fixed address inside address space of the CB. A type 2 memory-disclosure PoV proves vulnerability by reporting four contiguous bytes from this flag page to the CFE infrastructure. The flag page contents are generated randomly for every service poll and are made available to the service poller. Consequently, CB authors are encouraged to use the flag page as _external data_ intrinsic to the functionality of the program and validated by the service poller.
- The use of the random() system call shall not be used by the CB authors to manipulate control flow.
- Each vulnerability must be individually enumerated in the code and the README.md as well as have their difficulty subjectively quantified.
- The Makefile for the CB must define a variable 'VULN_COUNT' with an integer that specifies the number of vulnerabilities in the CB.
- The use of the service poll generator is mandatory and must be capable of generating at least one million distinct service polls. The author can now choose when code paths in the generator are enabled in the course of CFE to validate the competitor replacement binaries.  No hand written polls will be allowed.
- All polls used during CFE will be seen by competitors at the time of use, as such "for-testing" service polls are no longer supported.
- The use of executable code in data buffers (like for JIT) is discouraged but no longer prohibited.
- The restriction that shared CB library code must be _libc_ style functions has been lifted. Library code shared between CBs must still be generalized library functions, must not exist outside of the DECREE universe and must be seen by competitors for the first time during the final event.


## CB Guidance

CBs are network services that accept remote network connections, perform processing on network-supplied data, and interact with remote hosts over network connections. CBs will be used as analysis challenges within the CGC program; CGC teams will develop technology that will attempt to locate and mitigate flaws in CBs. Each CB will be implemented as a network service which performs some task to be determined by the CB author; examples include (but are not limited to) file transfer, remote procedure call, remote login, p2p networking. While CB tasks should mirror real world tasks, the use of real world protocols is disallowed. CBs may contain methods of operation which mirror challenging cases in real world network defense: dynamic network resource allocation, high integrity execution, dynamic execution, etc. Each CB will contain at least one security flaw hidden in the program by that CB author and reachable via network input. Flaws should focus on traditional memory corruption flaw types.

Superior approaches will demonstrate knowledge of the problems involved in creating challenge software for the purpose of cybersecurity competition (e.g., binaries of excessive difficulty prevent any competitor from making progress, while binaries of limited difficulty prevent meaningful measurement). Strong CB authors will demonstrate knowledge of the current limits of automated cyber reasoning in terms of program complexity and flaw discovery difficulty; this knowledge is essential in order to create a collection of CBs that spans a difficulty range from challenging to beyond state-of-the-art. The task of creating novel hidden software flaws to challenge the leading edge of program analysis poses significant technology risk. CB authors are expected to overcome this risk with a representative corpus of Challenge Sets. Strong CB authors will cover a history of known software flaws that represent interesting analysis challenges, mapped to specific CWE categories that will be represented within the CS portfolio of the author.


## Deliverables
All items required when submitting a CB are _source_ not _binary_.  All binary components must be built as part of the compilation process.

### Conforming to Submission Requirements

Note that many of the items detailed in this document are created and instructions are followed implicitly by the tools and build process provided by the CGC dev team.

Generally, if a CB author has followed the CB building guide and used the provided tools, the resulting Challenge Set should already be well-formed and simply needs to be submitted as detailed below in the "Submission" section.

### Flag page

A special flag page is mapped into every Challenge Binary at address 0x4347C000 and filled with 4096 pseudo-random bytes uniquely generated for every connection. This special flag page represents precious external data to the CB. A competitor acquiring and reporting four contiguous bytes from this flag page constitute proof of vulnerability - called a memory-disclosure type 2 PoV.

Challenge Binary authors are strongly encouraged to make the use of this special flag data intrinsic to their program and service poller. To support this, the flag page data is also made available to the service poller to allow for functional verification of the contents. For example this flag page could be treated as a database of authentication credentials, a filesystem of secrets, the starting position of items in a physics simulation a dictionary, or the description of a maze in a game. Replacement binaries which corrupt the legitimate use of this page should create a measurable failure of functionality.

* N.B. A challenge binary leaking flag page contents out directly or indirectly is not forbidden but CB authors are reminded that any four contiguous bytes of this data will constitute proof of vulnerability.
* N.B. The CB author should not assume that a vulnerability which lends itself to a register-set style type 1 PoV precludes the competitor use of a memory-disclosure style type 2 PoV against the same vulnerability or vice versa.

### CB authors are required to deliver the following items included in their Challenge Sets (CS):

- CB(s)
    * Must be of sufficient complexity. I.e. simple fully automated testing of all possible inputs is not possible.
    * Naming conventions:
        - The top level directory of a CB delivery shall be named: AAAAA_DDDDD
          where AAAAA is an upper case sequence of 5 letters assigned by DARPA
          that represents the company name of the author, and DDDDD is a unique
          serial number with leading zeros if necessary, assigned by the author.
          Serial number must begin with 00001 and increment by one across the
          complete set of CBs provided by the author.
- PoVs
    * At least one PoV must be submitted to exercise each intentional vulnerability.
    * POVs must be either written in C or XML
    * XML POV requirements:
        - POVs must be _well formed_ and match the POV DTD provided .
        - XML POVs shall be stored in the 'pov' directory.
        - XML POVs shall be named: POV_ddddd.povxml, where ddddd is a unique serial integer with leading zeros as needed, incrementing by 1, starting at 1.
        - XML POVs must include Type 1 or Type 2 negotiation statements as per the XML DTD.
        - See the <a href="#Refs">XML template</a> below
    * C POV requirements:
        - Each C POV shall be stored in a directory named: pov_n, where n is a unique serial number without leading zeros, incrementing by 1, starting at 1.
        - C POVs will be compiled as DECREE binaries, similar to CBs
        - C POVs must declare if the POV is a type 1 or type 2 POV via the POV negotiation protocol on file descriptor 3.
        - C POVs may determine the type (1 or 2) at runtime
        - Refer to understanding-cfe-povs.md for details on the CFE type negotiation protocols.
        - C POVs must follow CB Source Code requirements
- Challenge Test module comprised of Service polls
    * Must have consistent input and output paired behavior
    * Must provide coverage for all _major or significant_ aspects of binary functionality.  Code segments that are not exercised by any poll may effectively never be executed and may therefore be considered superfluous. 
    * Should incorporate the CBs algorithm to verify the contents of the special flag page.
    * Each must be capable of generating at least 1,000,000 unique service polls.
    * Polls must be generated automatically; such polls must be named GEN_DDDDD after generation as detailed in 'Naming Convention' below.  Generated polls are not submitted as POVML, instead they are generated as part of the make process.  CB authors must submit all software required to generate polls. If using the supplied generator this means CB authors must supply the generation spec. (see understanding-poll-generators for more information)
    * Polls may not be dynamically created by incorporating the CB itself. The service polls are required to evaluate the correct function of replacement CBs as well as the correct function of the original CB. Dynamic generation of the service polls shall replicate the logic required to test functionality. This does not prevent the service poll generator from incorporating algorithms from the CB itself.
    * Each CB must include at least one identified vulnerability as detailed in the <a href="#README">README</a> section below
    * All polls must have a unique file name per CB
    * CB authors are responsible for determining when, in the course of CFE, that poll behavior will begin. For example CFE could start with polls that only exercise a small fraction of the CB functionality which can be increased over time. Or full functionality could be tested immediately.  Functional accessability can be tuned via the 'before' and 'after' attributes in the poll generator.
    * Naming conventions:
        - Polls shall be named: GEN_ddddd.xml where ddddd
          is a unique serial integer with leading zeros if necessary, as
          assigned by the author.

- Source code 
    * Building:
        - A CB shall contain no external library dependencies. Dynamic linking is
          not supported in the CGC execution environment.
        - Accordingly all CBs must be built with the following arguments or
          their equivalents:
            + -nostdinc++
            + -nostdinc
            + -nostdlib
            + -static
            + -nostartfiles
            + -nodefaultlibs
            + -nostdlib
    * The only authorized linker for CGC challenge binaries is the CGC 
      version of ld, i386-linux-cgc-ld, as provided by DARPA. All executable 
      files used in the CGC must be valid output from i386-linux-cgc-ld.
    * All challenge binaries must continue to function properly after all
      Cgc32_Shdr (Elf32_Shdr) section headers have been removed from the
      binary. In other words following an operation equivalent to:
      memset(Cgc32_Ehdr.e_shoff, 0, Cgc32_Ehdr.e_shnum * Cgc32_Ehdr.e_shsize)
      Cgc32_Ehdr.e_shnum = 0
    * Authoring:
        - Every source file (.c, .h) created by the author shall begin with
          the complete text of the copyright license included as a multi-line
          (/* */) comment.
        - Code reuse across CBs is severely restricted. No code may be shared
          between separate organizations under contract to DARPA to create CFE
          challenge binaries. Furthermore, within a given organization, the only
          source code that may be reused across challenge binaries will be limited
          to functionality that commonly would be found in a library.
        - Authors are free to implement their own versions of the C standard
          libraries. Alternatively authors may make use of any standard library
          routines supplied by DARPA.
        - The use of native assembly within CBs is strictly limited to \_start stubs
          and system call wrappers (e.g. no 'inline' assembly placed about CB code). 
          Specifically, assembly language may not be utilized to increase the 
          complexity/obscurity of a CB in any way.
        - The use of machine-dependent instructions, 'shellcode' or JIT within
          CBs is discouraged but not prohibited.  (e.g. calling into a data
          buffer filled with instructions). This does not lift the ban on native
          assembler. All instructions must originate from C or C++ source code
          compiled during the Make process.
        - The use of the random() system call shall not be used by the CB
          authors to manipulate control flow.  DECREE will use identical seeds
          to the pseudo random number generator when testing different
          competitors with the same service poll. A competitor replacement
          binary may use random() system call as part of a defensive strategy -
          the consequence is that different competitors could accidentally have
          divergent performance characteristics on the same poll which should
          be avoided. DARPA would encourage authors to use the special flag
          page when the challenge binary logic merely needs an external data
          source without the requirement for strong pseudo randomness.
        - Authors must facilitate creation of both a vulnerable and patched version 
          of the CB.  The distinction between the vulnerable and not vulnerable 
          version is identified by one or more instances of a preprocessor 
          directive "#ifdef PATCHED_<n>" where the <n> is the PoV number,
          followed by an optional "#else" and "#endif". The purpose of this
          differentiation is to allow the visualization framework to
          automatically distinguish between PoVs.
          Patched CBs must be **not** be vulnerable to associated PoVs.
<a id='README'></a>
- README that must include: 
    * Must be in _markdown_ format and follow the sample template provided
    * Author + contact info (i.e. "Clint Eastwood" <clint@example.com>)
    * Performer group of the Author (i.e. DARPA)
    * Description of service that the CB implements (i.e. A book library)
    * Feature list of service suitable for a play-by-play announcer during
      CFE. i.e This is a book server populated with the Defense Federal
      Acquisition Regulations. It supports adding new books, checking out
      sections of the book, keyword searching, compression, and deciphering
      contract officer speak into English.
   * For each vulnerability
       * The vulnerability number corresponding to the #ifdef PATCHED_<n> in
         the source code
       * Description of the vulnerability
       * CWE classification
           - must include which CWE(s) are covered by the author's best assessment
           - only documented vulnerabilities that have PoVs, mitigation and 
             service poll coverage will be considered
       * Generic class of the vulnerability: buffer overflow, underflow, format
         string, use-after-free, etc.
       * Description of the challenges presented with specific consideration
         to automated binary analysis tools (i.e. complex logic to reach vuln,
         floating point math in reachability, etc)
       * A subjective quantification of "easy", "medium" or "hard" for each of
         the three categories: discovering, proving and fixing the
         vulnerability. A rule of thumb which the CB author may is are
            - "easy" vulnerabilities are intentionally written to be or are
              believed to be easy for one or more categories
            - "hard" vulnerabilities are intentionally written to be or are
              believed to be hard for one or more categories
            - "medium" vulnerabilities are a catch all


##Submission:

#### Each CB must be compiled using the _Make_ file and process provided by the CGC infrastructure team and submitted via SVN using the _Submissions_ branch as follows:

Run 'make clean' before to copying files to the submissions branch.<br>
 svn copy svn+ssh://server/trunk/<mypath>/AAAAA_DDDDD svn+ssh://server/branches/submissions/AAAAA_DDDDD -m "Submitting a new CB..."
    
- Delivery to DARPA:
    * Each CB delivered to DARPA must contain a complete copy of all source code
       - Including "library" code that is required to build a working executable file for the given CB.
       - Including any generation tool used to automatically create polls
    * When packaged for delivery, a CB must include all source code
      required to successfully build the binary. 
        - If a CB links to a static
      library, that static library must be compiled as part of the CB build and
      all source code for that library must be included in the CB delivery.

#### The following directory hierarchy must be utilized when submitting a completed challenge binary:

```
      AAAAA_DDDDD-
             |- src  <directory>
                  |- all .c, .cc source files that implement the CB behavior
             |- include  <directory>
                  |- all .h header files utilized by the CB
             |- pov  <directory>
                  |- One or more Proof of Vulnerability Markup Language (POVML)
                  |- files that demonstrate an appropriate "crashing event"
                  |- in the provided CB.
                  |- At least one POVML file or binary POV must be provided for each
                  |- vulnerability intentionally planted in the CB
             |- pov_N  <zero or more directories numbered from N=1>
                  |- C source and headers (.c, .h) for a single POV.
                  |- The resulting binary demonstrates an appropriate "crashing event"
                  |- in the provided CB.
                  |- At least one POVML file or binary POV must be provided for each
                  |- vulnerability intentionally planted in the CB
             |- poller  <directory>
                  |- contains exactly one subdirectory classifying polls into
                  |- one category only: 'for-release'
                  |- The 'for-release' directory must include all polls related to the CB.
                  |- Polls must follow the naming convention as detailed under
                  |- poll "Naming Conventions" above
                  |- for-release  <directory>
                       |- State machine specification for the protocol specified
                       |- by the CB. This specification will be utilized by DARPA to
                       |- generate service polls used to evaluate mitigated challenge
                       |- binaries.
             |- lib [optional]   <directory>
                  |- all .c, .cc, .h files that implement any C library
                  |- functionality
             |- README.md A markdown file as described above 
             |- Makefile  A makefile that follows the CGC service guide

```


# Test cases:
The following is an incomplete list of tests and validations that will be performed on the CS after it
is submitted. This list is intended to provide guidance for authors as to the _types_ of tests that will be performed
but is not intended to provide a complete list. Please note that this list may be amended at any time to better address the program goals.

- service polls vs CB - verify the correctness of the service polls
- PoV vs CB - confirm the efficacy of the supplied PoVs
- PoV vs RB - confirm that the PoVs are ineffective against the replacement binary
- service polls vs RB - verify the correctness of the service polls
- evaluate the CB against existing program analysis tools
- check for code reuse 

#### Each CS will be independently evaluated.
Collated statistics will be provided on a dashboard on the submission/svn server, showing anonymized results for CWE coverage as well as how the CB fares against a variety of program analysis utilities. These statistics are intended to keep the CB authors apprised of the overall composition of CGC. These statistics are explicitly covered by the CGC NDA and not for distribution outside of the CGC team.

## SEE ALSO

For information regarding CFE POV types, see understanding-cfe-povs.md <br>
For information regarding the testing a CB, see testing-a-cb.md <br>
For information regarding the debugging a CB, see debugging-a-cb.md <br>
For information regarding the building a CB, see building-a-cb.md <br>
For information regarding automated generation of polls, see understanding-poll-generators.md <br>
For information regarding POVML, see replay.dtd (DOCTYPE specified at the top of example polls <br>

See the service-template CB for an exemplar CB including, source, libraries, identified vulnerability, POVs, polls, etc

For support please contact CyberGrandChallenge@darpa.mil
