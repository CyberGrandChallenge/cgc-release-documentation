# Debugging a Challenge Binary

This walk-through will guide you through debugging a challenge binary.  

During the creation of of Challenge Binaries (CBs), an author may need to use tools to inspect and debug various built binaries. 

## Inspecting a CB

The unix 'file' command can be used as a quick, high-level test that a file in question is a CGC binary.

    $ file LUNGE_00001
    LUNGE_00001: CGC 32-bit LSB executable, (CGC/Linux)

CGC tool-chain items intended to be  specifically used with CBs can be found in standard cross-build locations for 'i386-linux-cgc'.  Specifically:

    /usr/i386-linux-cgc/bin/
    /usr/bin/i386-linux-cgc-*

When wishing to use these tools, you must specify the full path to the tool, use the 'long name' for the specific tool in /usr/bin, or prepend the /usr/i386-linux-cgc/bin directory to your path. For instance, objdump can be used in these ways.

The full path for either location of objdump:

    $ /usr/bin/i386-linux-cgc-objdump -f LUNGE_00001
    $ /usr/i386-linux-cgc/bin/objdump -f LUNGE_00001

Using the 'long name' which, because it is in /usr/bin, is already in PATH:

    $ i386-linux-cgc-objdump -f LUNGE_00001

Prepending the location of the i386-linux-cgc tools to PATH:

    $ which objdump
    /usr/bin/objdump
    $ PATH=/usr/i386-linux-cgc/bin:$PATH
    $ which objdump
    /usr/i386-linux-cgc/bin/objdump
    $ objdump -f LUNGE_00001

In any of these cases, the output of 'objdump -f' should be similar to:

    $ objdump -f LUNGE_00001
    
    LUNGE_00001:     file format cgc32-i386
    architecture: i386, flags 0x00000112:
    EXEC_P, HAS_SYMS, D_PAGED
    start address 0x08048074

The CGC version of objdump can be used to perform many inspection functions, such as observing section headers, or observing symbols:

    $ objdump -h LUNGE_00001
    
    LUNGE_00001:     file format cgc32-i386
    
    Sections:
    Idx Name          Size      VMA       LMA       File off  Algn
      0 .text         00000255  08048074  08048074  00000074  2**0
                      CONTENTS, ALLOC, LOAD, READONLY, CODE
      1 .rodata       00000027  080482cc  080482cc  000002cc  2**2
                      CONTENTS, ALLOC, LOAD, READONLY, DATA
      2 .eh_frame     00000054  080482f4  080482f4  000002f4  2**2
                      CONTENTS, ALLOC, LOAD, READONLY, DATA
      3 .comment      0000001c  00000000  00000000  00000348  2**0
                      CONTENTS, READONLY
      4 .debug_aranges 00000040  00000000  00000000  00000364  2**0
                      CONTENTS, READONLY, DEBUGGING
      5 .debug_info   000001a2  00000000  00000000  000003a4  2**0
                      CONTENTS, READONLY, DEBUGGING
      6 .debug_abbrev 00000134  00000000  00000000  00000546  2**0
                      CONTENTS, READONLY, DEBUGGING
      7 .debug_line   000000da  00000000  00000000  0000067a  2**0
                      CONTENTS, READONLY, DEBUGGING
      8 .debug_str    000000ba  00000000  00000000  00000754  2**0
                      CONTENTS, READONLY, DEBUGGING
      9 .debug_loc    00000064  00000000  00000000  0000080e  2**0
                      CONTENTS, READONLY, DEBUGGING

    $ objdump -t LUNGE_00001
    
    LUNGE_00001:     file format cgc32-i386
    
    SYMBOL TABLE:
    08048074 l    d  .text	00000000 .text
    080482cc l    d  .rodata	00000000 .rodata
    080482f4 l    d  .eh_frame	00000000 .eh_frame
    00000000 l    d  .comment	00000000 .comment
    00000000 l    d  .debug_aranges	00000000 .debug_aranges
    00000000 l    d  .debug_info	00000000 .debug_info
    00000000 l    d  .debug_abbrev	00000000 .debug_abbrev
    00000000 l    d  .debug_line	00000000 .debug_line
    00000000 l    d  .debug_str	00000000 .debug_str
    00000000 l    d  .debug_loc	00000000 .debug_loc
    00000000 l    df *ABS*	00000000 service.c
    00000000 l    df *ABS*	00000000 libc.c
    00000000 l    df *ABS*	00000000 
    08048121 g       .text	00000000 random
    0804807f g       .text	00000000 _terminate
    0804810d g       .text	00000000 deallocate
    08048074 g       .text	00000000 _start
    08049348 g       .eh_frame	00000000 __bss_start
    0804813b g     F .text	0000010f main
    0804808d g       .text	00000000 transmit
    080480cd g       .text	00000000 fdwait
    080480ad g       .text	00000000 receive
    08049348 g       .eh_frame	00000000 _edata
    08049348 g       .eh_frame	00000000 _end
    0804824a g     F .text	0000007f transmit_all
    080480f3 g       .text	00000000 allocate

A stripped CB would exhibit less information in the case of symbols:

    $ strip LUNGE_00001
    $ objdump -t LUNGE_00001
    
    LUNGE_00001:     file format cgc32-i386
    
    SYMBOL TABLE:
    no symbols

## Using STDERR to debug a CB

The age-old method of inserting additional output into a program in order to track flow can certainly be used to debug a CB.  For example, preprocessor directives (specifically '#ifdef PATCHED_N') are used to indicated what should or should not be included in the PATCHED version of a CB.  Suppose, you want to test that code associated with such a preprocessor is reachable, and therefore a vulnerable condition is reachable. A simple way to do this is by adding additional 'transmit' calls in order to create output to STDERR.

Consider inserting the following lines into the example service.c beginning with the ifdef on line 24:

    #ifdef PATCHED_1
        transmit(STDERR, "Reached point 4\n", 16, 0);
        _terminate(4);
    #else
        transmit(STDERR, "Reached point 5\n", 16, 0);
        _terminate(5);

        if (buf[0] == 0x41 && buf[1] == 0x42) {
            char *p = 0;
            p[0] = 10;
        }
    #endif


By inserting additional calls to 'transmit' the output of the CB will clearly indicate if compilation process included the '#ifdef PATCHED_<n>' block or the 'else' block.  Similarly, by inserting additional '_terminate' calls, the CB will exit when this debugging error condition is met, and the CB return code can be tested to determine which of the '_terminate' calls was reached.  In fact, '_terminate' can be used in this fashion to debug without using 'transmit' at all.

After building the CB with the two additional 'transmit' and '_terminate' calls, we can observe the effects via output and via return code:

    $ ./bin/LUNGE_00001 > /dev/null
    Reached point 5
    $ echo $?
    5
    $ ./bin/LUNGE_00001_patched > /dev/null
    Reached point 4
    $ echo $?
    4

In the unpatched version of the CB, we reach the 'transmit' indicating we 'Reached point 5' and the error code stemming from the '_terminate' is also 5 (as reported by $?).  Similarly, we see point 4 and code 4 for the patched version of the CB.

Note:  If you already have pollers or PoVs in place, altering the output of a CB might cause these to no longer work.  Since the debugging output is temporary code that will later be removed, it is probably not worth altering pollers and PoVs to match the additional debugging output.  For this reason, instead of issuing a generic 'make' CB authors might consider using the 'build' make target: 'make build'.  The 'build' target will compile the unpatched and patched CBs, but will not perform additional steps required prior to submission of the final CB.

## Using GDB to debug a CB

GDB has been modified to work with CBs.  Simply load a CB into GDB by starting GDB with the CB as a command line argument.  The code listing below demonstrates loading a CB, setting a breakpoint by name, executing the CB and then single-stepping after GDB encounters the breakpoint.  Since the CB has not been stripped, symbols are loaded from the CB and the breakpoint can be set by name ('main') and line source information is provided while single stepping.

    $ gdb LUNGE_00001
    GNU gdb (GDB) 7.4.1
    Copyright (C) 2012 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
    and "show warranty" for details.
    This GDB was configured as "i686-pc-linux-gnu".
    For bug reporting instructions, please see:
    <http://www.gnu.org/software/gdb/bugs/>...
    Reading symbols from bin/LUNGE_00001...done.
    (gdb) break main
    Breakpoint 1 at 0x8048147: file src/service.c, line 11.
    (gdb) r
    Starting program: bin/LUNGE_00001 
    
    Breakpoint 1, main () at src/service.c:11
    11	    ret = transmit_all(STDOUT, STR1, sizeof(STR1) - 1);
    (gdb) s
    transmit_all (fd=1, buf=0x80482cc "This implements a simple echo service\n", size=38) at lib/libc.c:5
    5	    size_t sent = 0;
    (gdb) s
    6	    size_t sent_now = 0;
    (gdb) s
    9	    if (!buf) 

This sample service has a conditional, intentional bug at line 26:

    $ head -n 29 src/service.c | tail -n 4
      if (buf[0] == 0x41 && buf[1] == 0x42) {
          char *p = 0;
          p[0] = 10;
      }

The CB can be executed from GDB, and the write of 'AB' to reach the bug can be provided interactively.  Here we set a breakpoint on the condition around the basic block containing the bug (by line number - 'line 25').  First we provide input that fails the condition ('afd'), then we provide input that passes the condition ('AB').  When GDB encounters the null pointer assignment, GDB catches SIGSEGV and prompts the user about the signal.  When debugging a CB during development, a binary with debugging symbols is available in the directory 'build/release/bin/'.  If this binary is used, GDB can show the source code surrounding the line that caused the SIGSEGV.

    $ gdb LUNGE_00001
    GNU gdb (GDB) 7.4.1
    ...
    Reading symbols from bin/LUNGE_00001...done.
    (gdb) break 25
    Breakpoint 1 at 0x80481e1: file src/service.c, line 25.

    (gdb) run
    Starting program: bin/LUNGE_00001 
    This implements a simple echo service
    afd
    
    Breakpoint 1, main () at src/service.c:26
    26	        if (buf[0] == 0x41 && buf[1] == 0x42) {
    (gdb) disp buf
    1: buf = "afd\n", '\000' <repeats 1019 times>
    (gdb) c
    Continuing.
    afd
    AB
    
    Breakpoint 1, main () at src/service.c:26
    26	        if (buf[0] == 0x41 && buf[1] == 0x42) {
    1: buf = "AB\n", '\000' <repeats 1020 times>
    (gdb) c
    Continuing.
    
    Program received signal SIGSEGV, Segmentation fault.
    0x08048205 in main () at src/service.c:28
    28	            p[0] = 10;
    1: buf = "AB\n", '\000' <repeats 1020 times>
    
    (gdb) list src/service.c:28
    23	
    24	#ifdef PATCHED_1
    25	#else
    26	        if (buf[0] == 0x41 && buf[1] == 0x42) {
    27	            char *p = 0;
    28	            p[0] = 10;
    29	        }
    30	#endif
    31	
    32	        ret = transmit_all(STDOUT, buf, size);
    (gdb) 
        
The sample service is purposefully simple, but we can still observe a simple backtrace by pausing execution at 'transmit' which will be called via the library function 'transmit_all':

    $ gdb LUNGE_00001
    GNU gdb (GDB) 7.4.1
    ...
    Reading symbols from bin/LUNGE_00001...done.
    (gdb) break transmit
    Breakpoint 1 at 0x804808d
    (gdb) run
    Starting program: bin/LUNGE_00001 
    
    Breakpoint 1, 0x0804808d in transmit ()
    (gdb) bt
    #0  0x0804808d in transmit ()
    #1  0x080482a4 in transmit_all (fd=1, buf=0x80482cc "This implements a simple echo service\n", size=38) at lib/libc.c:16
    #2  0x08048163 in main () at src/service.c:11


GDB can also show a disassembly of the function:

    (gdb) disassemble transmit_all
    Dump of assembler code for function transmit_all:
       0x0804824a <+0>:	push   %ebp
       0x0804824b <+1>:	mov    %esp,%ebp
       0x0804824d <+3>:	sub    $0x28,%esp
    => 0x08048250 <+6>:	movl   $0x0,-0xc(%ebp)
       0x08048257 <+13>:	movl   $0x0,-0x14(%ebp)
       0x0804825e <+20>:	cmpl   $0x0,0xc(%ebp)
       0x08048262 <+24>:	jne    0x804826b <transmit_all+33>
       0x08048264 <+26>:	mov    $0x1,%eax
       0x08048269 <+31>:	jmp    0x80482c7 <transmit_all+125>
       ...

GDB may also be used to view the contents of the secret flag page

   $ gdb -q bin/CADET_00003
   Reading symbols from bin/CADET_00003...(no debugging symbols found)...done.
   (gdb) info files
   Symbols from "/home/vagrant/CADET_00003/bin/CADET_00003".
   Local exec file:
           `/home/vagrant/CADET_00003/bin/CADET_00003', file type elf32-i386.
           Entry point: 0x80485fc
           0x080480a0 - 0x08048700 is .text
           0x08048700 - 0x08048796 is .rodata
           0x08049798 - 0x0805d98c is .data
   (gdb) b *0x80485fc
   Breakpoint 1 at 0x80485fc
   (gdb) run
   Starting program: /home/vagrant/CADET_00003/bin/CADET_00003 
   
   Breakpoint 1, 0x080485fc in ?? ()
   (gdb) info proc map
   process 5714
   Mapped address spaces:
   
           Start Addr   End Addr       Size     Offset objfile
            0x8048000  0x8049000     0x1000        0x0 /home/vagrant/CADET_00003/bin/CADET_00003
            0x8049000  0x805e000    0x15000        0x0 /home/vagrant/CADET_00003/bin/CADET_00003
           0x4347c000 0x4347d000     0x1000        0x0  <== This is the secret page (only anonymous page at start)
           0xbaa8b000 0xbaaab000    0x20000        0x0 [stack]
   (gdb) x /16xb 0x4347c000
   0x4347c000:     0x4c    0xf5    0x57    0x33    0xa1    0xb0    0xd3    0x5f
   0x4347c008:     0x5f    0x0c    0xf2    0xca    0x5e    0x93    0x29    0x0c
   (gdb) run
   The program being debugged has been started already.
   Start it from the beginning? (y or n) y
   Starting program: /home/vagrant/CADET_00003/bin/CADET_00003 
   
   Breakpoint 1, 0x080485fc in ?? ()
   (gdb) info proc map
   process 5718
   Mapped address spaces:
   
           Start Addr   End Addr       Size     Offset objfile
            0x8048000  0x8049000     0x1000        0x0 /home/vagrant/CADET_00003/bin/CADET_00003
            0x8049000  0x805e000    0x15000        0x0 /home/vagrant/CADET_00003/bin/CADET_00003
           0x4347c000 0x4347d000     0x1000        0x0  <== This is the secret page (only anonymous page at start)
           0xbaa8b000 0xbaaab000    0x20000        0x0 [stack]
   (gdb) x /16xb 0x4347c000
   0x4347c000:     0xa1    0x94    0x0e    0x63    0xf1    0xf5    0xf9    0x62
   0x4347c008:     0xcd    0x5c    0x8c    0x87    0x06    0xc9    0xec    0xfa
   (gdb) 

## Using core files with GDB

The CGC kernel is capable of creating CGC core files when a CB crashes.  ulimit for core files is typically set to 0, to enable core dumps this ulimit must be non-zero (recommend: 'unlimited').  Valid core dumps cannot be created on folders shared with the host using VirtualBox. The core file will be created, but will have a zero length (use -d option to cb-server as below).

    $ ulimit -c
    0
    $ ulimit -c unlimited
    $ ulimit
    unlimited

If a CB crashes (and the ulimit for core files is non-zero), a file named 'core' will be created (e.g. core will be dumped).  

    $ ./LUNGE_00001
    This implements a simple echo service
    AB
    Segmentation fault (core dumped)
    $ file core 
    core: CGC 32-bit LSB core file (CGC/Linux)

Such a CGC core file can be supplied to GDB along with the binary (as a second argument or via the '-c' option).  

    $ gdb LUNGE_00001 core 
    GNU gdb (GDB) 7.4.1
    ...
    Reading symbols from /vagrant/cgc/trunk/challenge-sets/cqe/examples/service-template/bin/LUNGE_00001...done.
    [New LWP 7512]
    Core was generated by ''.
    Program terminated with signal 11, Segmentation fault.
    #0  0x08048205 in main () at src/service.c:28
    28	            p[0] = 10;


## Using GDB to attach to a running process

Locate the PID of the already running process.

    $ ps -ef | grep LUNGE_00001
    root      7621  7586  0 03:53 pts/0    00:00:00 [LUNGE_00001]

Then use GDB to attach to the process
    $ gdb
    GNU gdb (GDB) 7.4.1
    ...
    (gdb) attach 7621
    Attaching to process 7621
    Reading symbols from bin/LUNGE_00001...done.
    0x080480c6 in receive ()

Similarly, GDB can attach to processes launched via the cb-server as long as '--debug' is added to the command line as to disable the internal ptracing of CBs.  In this example, port 5555 is specified.  Note, the CB timeout should be set to an exceedingly long time for debugging purposes. In this example, a full year has been specified.  Netstat can be used to verify the CB is listening.

console 1: 

    $ cb-server -t 31536000 -p 5555 --insecure -d bin --debug LUNGE_00001 

console 2:

    $ netstat -ano | grep 5555
    tcp        0      0 0.0.0.0:5555            0.0.0.0:*               LISTEN      off (0.00/0/0)
    $ nc localhost 5555 
    This implements a simple echo service

console 3:

    $ ps -ef | grep LUNGE_00001
    vagrant   7653  3356  0 04:02 pts/0    00:00:00 cb-server -t 5000 -p 5555 --insecure -d /tmp/test LUNGE_00001
    vagrant   7657  7653  0 04:04 pts/0    00:00:00 [LUNGE_00001]
    $ gdb
    GNU gdb (GDB) 7.4.1
    ...
    (gdb) attach 7657
    Attaching to process 7657
    Reading symbols from /tmp/test/LUNGE_00001...done.
    0x080480c6 in receive ()

## Debugging a CFE POV

    Launch the challenge binary without timing out the CB:
        $ cb-server -d bin CADET_00003 --insecure -p 5535 -t 0

    In another terminal, launch the POV with the 
        $ cb-replay-pov --host 127.0.0.1 --port 5535 pov/pov_1.pov --attach_port 2601

    In another terminal, launch gdb and issue the command 'target :remote 2601'
        $ gdb -q pov/pov_1.pov
        (gdb) target remote :2601 
        Remote debugging using :2601
        Remote debugging using :2601
        Reading symbols from /lib/i386-linux-gnu/libpthread.so.0...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libdl.so.2...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libutil.so.1...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libz.so.1...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libm.so.6...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libc.so.6...(no debugging symbols found)...done.
        Reading symbols from /lib/i386-linux-gnu/libgcc_s.so.1...(no debugging symbols found)...done.
        Reading symbols from /lib/ld-linux.so.2...(no debugging symbols found)...done.
        Reading symbols from /usr/lib/python2.7/lib-dynload/_multiprocessing.so...(no debugging symbols found)...done.
        Reading symbols from /usr/lib/python2.7/lib-dynload/_hashlib.so...(no debugging symbols found)...done.
        Reading symbols from /usr/lib/i386-linux-gnu/i686/cmov/libssl.so.1.0.0...(no debugging symbols found)...done.
        Reading symbols from /usr/lib/i386-linux-gnu/i686/cmov/libcrypto.so.1.0.0...(no debugging symbols found)...done.
        Reading symbols from /usr/lib/python2.7/lib-dynload/_ssl.so...(no debugging symbols found)...done.
        0xb768267e in open () from /lib/i386-linux-gnu/libc.so.6
        (gdb)

    At this point, cb-replay-pov was waiting for gdb to attach to the process.  Use 'c' to continue once.
        (gdb) c
        Continuing.

        Program received signal SIGTRAP, Trace/breakpoint trap.
        0x080487a3 in _start ()
        (gdb)

    At this point, the POV has been loaded, but execution has not begun.  You can debug the POV from here.

## SEE ALSO

For information regarding the building a CB, see the building-a-cb.md walk-through

For information regarding using the cb-server, see man cb-server(1)

For support please contact CyberGrandChallenge@darpa.mil
