# Submitting a Challenge Binary


This walk-through is targeted at the performers under contract to create Challenge Binaries (CBs) for the Cyber Grand Challenge. This walk-through will guide CB authors through submitting a completed challenge binary. Here they will also find details of the challenge binary acceptance criteria including how submissions will be assessed and feedback processes for remediation. CGC competitor teams may also be interested in this guidance to CB authors.


## CB Guidance

CBs are network services that accept remote network connections, perform processing on network-supplied data, and interact with remote hosts over network connections. CBs will be used as analysis challenges within the CGC program; CGC teams will develop technology that will attempt to locate and mitigate flaws in CBs. Each CB will be implemented as a network service which performs some task to be determined by the CB author; examples include (but are not limited to) file transfer, remote procedure call, remote login, p2p networking. While CB tasks should mirror real world tasks, the use of real world protocols is disallowed. CBs may contain methods of operation which mirror challenging cases in real world network defense: dynamic network resource allocation, high integrity execution, dynamic execution, etc. Each CB will contain at least one security flaw hidden in the program by that CB author and reachable via network input. Flaws should focus on traditional memory corruption flaw types.

Superior approaches will demonstrate knowledge of the problems involved in creating challenge software for the purpose of cybersecurity competition (e.g., binaries of excessive difficulty prevent any competitor from making progress, while binaries of limited difficulty prevent meaningful measurement). Strong CB authors will demonstrate knowledge of the current limits of automated cyber reasoning in terms of program complexity and flaw discovery difficulty; this knowledge is essential in order to create a collection of CBs that spans a difficulty range from challenging to beyond state-of-the-art. The task of creating novel hidden software flaws to challenge the leading edge of program analysis poses significant technology risk. CB authors are expected to overcome this risk with a representative corpus of Challenge Sets. Strong CB authors will cover a history of known software flaws that represent interesting analysis challenges, mapped to specific CWE categories that will be represented within the author's CS portfolio.


## Deliverables
All items required when submitting a CB are _source_ not _binary_.  All binary components must be built as part of the compilation process.

### Conforming to Submission Requirements

Note that many of the items detailed in this document are created and instructions are followed implicitly by the tools and build process provided by the CGC dev team.

Generally, if a CB author has followed the CB building guide and used the provided tools, the resulting Challenge Set should already be well-formed and simply needs to be submitted as detailed below in the "Submission" section.


### CB authors are required to deliver the following items included in their Challenge Sets (CS):

- CB(s)
    * Must be of sufficient complexity. I.e. simple fully automated testing of all possible inputs is not possible.
    * Naming conventions:
        - The top level directory of a CB delivery shall be named: AAAAA_DDDDD
          where AAAAA is an upper case sequence of 5 letters assigned by DARPA
          that represents the author's company name, and DDDDD is a unique
          serial number with leading zeros if necessary, assigned by the author.
          Serial number must begin with 00001 and increment by one across an
          author's complete set of provided CBs.
        - The final executable version of the CB shall be named using an
          identifier identical to the top level directory name (see above).
          The patched version of the CB shall follow the same convention except that the
          file name will additionally have "_patched" appended.
- PoVs
    * XMLs must be _well formed_ and match the template provided 
    * At least one PoV must be submitted to exercise each intentional vulnerability
    * See the <a href="#Refs">XML template</a> below
- Service polls
    * Must have consistent input and output paired behavior
    * Must provide coverage for all _major or significant_ aspects of binary functionality.  Code segments that are not exercised by any poll may effectively never be executed and may therefore be considered superfluous. 
    * Each CB must have at least 1000 associated polls following the 'make' process between the _for-release_ and _for-testing_ categories.
    * Polls may be 'hand-written'; such polls must be named POLL_DDDDD as detailed in 'Naming Convention' below.  Hand-written polls are written in POVML.
    * Polls may be generated automatically; such polls must be named GEN_DDDDD after generation as detailed in 'Naming Convention' below.  Generated polls are not submitted as POVML, instead they are generated as part of the make process.  CB authors must submit all software required to generate polls. If using the supplied generator this means CB authors must supply the generation spec. (see understanding-poll-generators for more information)
    * Polls may not be dynamically created via interaction with a compiled CB; such polls will not provide coverage for all _major or significant_ aspects of binary functionality.
    * Each CB must include at least one identified vulnerability as detailed in the <a href="#README">README</a> section below
    * All polls must have a unique file name per CB
    * Polls are divided into two categories at the discretion of the CB author. However, both _for-testing_ and _for-release_ will be used for testing and competition polling.
        - _for-testing_ polls will only be used by CGC dev team for testing competitors' replacement CBs and will **not** be released to the competitors
        - _for-release_ polls **will** be released to competitors to inform them on CB functionality
    * CB authors are responsible for determining exactly how much and what type
      of network traffic will be released to competitors for use during CQE.  
      One PCAP file will be generated from the _for-release_ polls and given to competitors.
    * Naming conventions:
        - Polls shall be named: POLL_ddddd.xml or GEN_ddddd.xml where ddddd
          is a unique serial integer with leading zeros if necessary, as
          assigned by the author.
            + Polls with file names beginning with "POLL\_" indicate that the poll
              is "hand-written."  Hand-written polls are simply submitted in
              Proof of Vulnerability Markup Language (POVML) and are not touched
              by the CB build process. <a href="#Refs"> See more below </a>
            + Polls with file names beginning with "GEN_" indicate that the poll
              is generated as part of the CB build process.  Generated polls
              must not be submitted as POVML, instead the source for generation
              tool or specification must be submitted and these polls must be
              generated as part of the CB build process.<a href="#Refs"> See more below </a>
        - Please note that this guidance on service polls may change for CFE challenges.

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
          between separate organizations under contract to DARPA to create CQE
          challenge binaries. Furthermore, within a given organization, the only
          source code that may be reused across challenge binaries will be limited
          to standard C library (libc) functions requested by the performer and 
          approved by DARPA.
        - Authors are free to implement their own versions of the C standard
          libraries. Alternatively authors may make use of any standard library
          routines supplied by DARPA.
        - The use of native assembly within CBs is strictly limited to \_start stubs
          and system call wrappers (e.g. no 'inline' assembly placed about CB code). 
          Specifically, assembly language may not be utilized to increase the 
          complexity/obscurity of a CB in any way.
        - The use of machine-dependent instructions or 'shellcode' within CBs is strictly
          prohibited.  (e.g. calling into a data buffer filled with instructions).
        - Authors must facilitate creation of both a vulnerable and patched version 
          of the CB.  The distinction between the vulnerable and not vulnerable 
          version is identified by one or more instances of a preprocessor 
          directive "#ifdef PATCHED" followed by an optional "#else" and "#endif".
          Patched CBs must be **not** be vulnerable to provided PoVs.
<a id='README'></a>
- README that must include: 
    * Must be in _markdown_ format and follow the sample template provided
    * Author + contact info (i.e. "Clint Eastwood" <clint@palerider.net>)
    * Author's performer group (i.e. DARPA)
    * Description of service that the CB implements (i.e. A book library)
    * Feature list of service suitable for a play-by-play announcer during
      CFE. i.e This is a book server populated with the Defense Federal
      Acquisition Regulations. It supports adding new books, checking out
      sections of the book, keyword searching, compression, and deciphering
      contract officer speak into English.
   * Description of the vulnerability to include, where possible, specific
      locations in the source at which the vulnerability is evident.
    * CWE classification
        - must include author's best assessment of which CWE(s) are covered 
        - only documented vulnerabilities that have PoVs, mitigations and 
          service poll coverage will be considered
    * Generic class of the vulnerability: buffer overflow, underflow, format
      string, use-after-free, etc.
    * Description of the challenges presented with specific consideration
      to automated binary analysis tools (i.e. complex logic to reach vuln,
      floating point math in reachability, etc)


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
             |- bin  <directory>
                  |- the statically linked binary executable files resulting
                  |- from a successful "make" which shall be named AAAAA_DDDDD
                  |- AAAAA_DDDDD_patched as detailed under CB "Naming Conventions" 
                  |- above.
             |- pov  <directory>
                  |- One or more Proof of Vulnerability Markup Language (POVML)
                  |- files that demonstrate an appropriate "crashing event"
                  |- in the provided CB.
                  |- At least one POVML file must be provided for each
                  |- vulnerability intentionally planted in the CB
             |- poller  <directory>
                  |- contains exactly two subdirectories classifying polls into
                  |- two categories: 'for-testing' and 'for-release'
                  |- Specification of polls in the 'for-release' directory is at 
                  |- the discretion of the author. The 'for-testing' directory
                  |- must include all polls related to the CB.
                  |- Polls must follow the naming convention as detailed under
                  |- poll "Naming Conventions" above
                  |- for-testing  <directory>
                       |- State machine specification for the protocol specified
                       |- by the CB. This specification will be utilized by DARPA to
                       |- generate service polls used to evaluate mitigated challenge
                       |- binaries. (optional)
                       |- hand-written polls in POVML (optional)
                       |- Files in this directory will NOT be distributed outside of 
                       |- the CGC team for the event.
                  |- for-release  <directory>
                       |- State machine specification for the protocol specified
                       |- by the CB. This specification will be utilized by DARPA to
                       |- binaries. (optional)
                       |- hand-written polls in POVML (optional)
                       |- Files in this directory will be distributed outside of the
                       |- CGC dev team in the form of a single PCAP file
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

For information regarding the testing a CB, see testing-a-cb.md <br>
For information regarding the debugging a CB, see debugging-a-cb.md <br>
For information regarding the building a CB, see building-a-cb.md <br>
For information regarding automated generation of polls, see understanding-poll-generators.md <br>
For information regarding POVML, see replay.dtd (DOCTYPE specified at the top of example polls <br>

See the service-template CB for an exemplar CB including, source, libraries, identified vulnerability, POVs, polls, etc

For support please contact CyberGrandChallenge@darpa.mil
