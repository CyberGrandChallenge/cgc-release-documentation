# Running Intel PIN on DECREE Challenge Binaries

This walk-through will guide you through the process of building and running the ["Simple Instruction Count"](https://software.intel.com/sites/landingpage/pintool/docs/65163/Pin/html/index.html#EXAMPLES) pintool on a DECREE Challenge Binary. 

A small DECREE syscall emulation library is provided to users as a way to test their CBs using Intel's PIN architecture. The source for the sample pintool is attached at the end of the walkthrough for reference. Please note that this library is not a high fidelity model of DECREE and there will be discrepancies between native execution and Intel PIN instrumented execution.

## Prerequisites

1. The latest DECREE virtual machine.
2. A PIN distribution (Version 67254 from Sep 02, 2014 was used for this walk-through)
3. A CB to test.

## The syscall emulator

The DECREE OS exposes 7 different system calls to CBs: *_terminate*, *transmit*, *receive*, *fdwait*, *allocate*, *deallocate* and *random* with sys call numbers 1 to 7 respectively. Since these syscall numbers are used by the native Linux OS for other purposes, an emulation layer was created so that DECREE CB system calls are emulated using normal system calls. In short, *_terminate* calls *exit*, *transmit* and *receive* calls *write* and *read*, *fdwait* calls *select*, *allocate* and *deallocate* calls *mmap* and *munmap*, and finally *random* is emulated using */dev/random*. This is known as "Passthrough" mode in the emulation library.

The emulation layer works by adding an Instruction Instrumentation Function that looks for any *int 0x80* instructions (what DECREE CBs use to make system calls). When one is found, it will then add a callback to the main emulation function to be called before the actual instruction is executed. The emulation layer will gather the system call parameters and emulate the requested call. Once completed, it will instruct PIN to skip the original system call instruction and continue execution by calling *PIN_ExecuteAt* at the next instruction.

As a convenience, the emulation library can also work in an "Emulation" mode. This default "Passthrough" mode simply passes the DECREE syscalls through to the underlying system, e.g. *transmit* calls *write*. It works with the rest of the cb testing infrastructure such as cb-test, cb-replay and cb-server. On the other hand, the emulation mode works by redirecting all *transmit* and *receives* to reads and writes from files that the user can specify as parameters to the pintool.

### Using the library

To use the emulation layer, all one needs to do is integrate the library source with their pintool while following these guidelines:

First, there are some initialization code in *cgc_init* that needs to be called at the beginning. This is best achieved by adding the following source line to the main function

	PIN_AddApplicationStartFunction(cgc_init, NULL);

Second, make sure that the instruction callback is registered to instrument each instruction during translation time. 

	INS_AddInstrumentFunction(cgc_instrumentInstruction, NULL);

Third, call the cleanup function when done

	PIN_AddFiniFunction(cgc_cleanup, 0);

Fourth, make sure that the options for your pintool does not conflict with the options for the emulation layer.

## Building the DECREE CB Compatible Sample Instruction Count pintool

Building the DECREE CB Compatible pintool is fairly straight forward. Just follow the directions from the Intel PIN Manual. In short, it consists of:

1. Copying the pintools distribution into the VM (copy it to the location of the vagrantfile on the host.)
2. Replacing the inscount0.cpp file with the version that includes the emulation library. OR integrate the emulation layer into the source code by following the instructions mentioned above. Don't forget to include *libcgc_pin.h* as well.
3. Make the pintool as normal

## Running the pintool

This walk-through will illustrate how the instruction counter pintool on the YAN01_0001 CB. To do so, first build the CB as normal. This will result in a DECREE binary that must be changed back into an ELF binary by changing the magic value back to ELF. Changing the magic value can be completed using the *cgc2elf* tool.

	mkdir bin/elf
	cp bin/YAN01_00001 bin/elf/YAN01_00001
        cgc2elf bin/elf/YAN01_00001

This will create a new subdirectory called elf (to avoid clobbering the DECREE binary in bin/) and copy the binary into bin/elf/. The last command converts the cgc binary back to ELF.

Once the magic value has been changed, the cb can then be run as normal with a pintool. For example, run YAN01_00001 as a normal program:


	$ /vagrant/pin-2.14-67254-gcc.4.4.7-linux/pin -t /vagrant/pin-2.14-67254-gcc.4.4.7-linux/source/tools/ManualExamples/obj-ia32/inscount0.so -- bin/elf/YAN01_00001
	Player1:$ A
	Bad Command - Try again
	Player1:$ H
	Sorry, I am not very helpful
	Player1:$ e
	Bad Command - Try again
	Player1:$ ^C
	
Check the logfile after running the sample.

	$ more inscount.out
	Count 6239

	
As mentioned previously, the emulation layer runs in "Passthrough" mode by default, meaning reads by the CB from fd of 0 will result in a read from stdin. Pipe in a list of commands from a file to illustrate this. Use the following generated poll as an example:

	<?xml version="1.0" standalone="no" ?>
	<!DOCTYPE pov SYSTEM "/usr/share/cgc-replay/replay.dtd">
	<pov>
	<cbid>service</cbid>
	<replay>
	    <read><length>10</length><match><data>Player1:\x24 </data></match></read>
	    <write><data>P4IR2\x0a</data></write>
	    <read><length>10</length><match><data>Player2:\x24 </data></match></read>
	    <write><data>E\x0a</data></write>
	    <read><delim>\x0a</delim><match><data>You are stuck...\x0a</data></match></r
	ead>
	    <read><length>10</length><match><data>Player2:\x24 </data></match></read>
	    <write><data>N\x0a</data></write>
	    <read><length>10</length><match><data>Player1:\x24 </data></match></read>
	    <write><data>S\x0a</data></write>
	    <read><length>10</length><match><data>Player1:\x24 </data></match></read>
	</replay>
	</pov>

The corresponding input file is:

	P4IR2
	E
	N
	S

Test this by issuing the following commands:

	$ echo P4IR2 >> TESTINPUT
	$ echo E >> TESTINPUT
	$ echo N >> TESTINPUT
	$ echo S >> TESTINPUT
	$ /vagrant/pin-2.14-67254-gcc.4.4.7-linux/pin -t /vagrant/pin-2.14-67254-gcc.4.4.7-linux/source/tools/ManualExamples/obj-ia32/inscount0.so -- bin/elf/YAN01_00001 < TESTINPUT
	Player1:$ Player2:$ You are stuck...
	Player2:$ Player1:$ Player1:$ ERROR reading from user -- time to die
	$ more inscount.out
	Count 10151

Run the CB in emulation mode by directing fd 0 to be the file TESTINPUT. This is done by adding the "-e -fd 0,TESTINPUT" parameters to the pintool.

	$ /vagrant/pin-2.14-67254-gcc.4.4.7-linux/pin -t /vagrant/pin-2.14-67254-gcc.4.4.7-linux/source/tools/ManualExamples/obj-ia32/inscount0.so -e -fd 0,TESTINPUT -- bin/elf/YAN01_00001 
	Player1:$ Player2:$ You are stuck...
	Player2:$ Player1:$ Player1:$ ERROR reading from user -- time to die
	$ more inscount.out
	Count 10151

### Running the pintool with the cb infrastructure

Use the cb-server in 'wrapper' mode in order to run the pintool with the cb infrastructure. A wrapper is basically a program (or script) that is called by cb-server where the first parameter is the name of the cgc binary. This is needed because cb-server launches cgc binaries which do not take in parameters. The wrapper can be used to call external tools such as pin that require multiple input parameters. 

A shell script will be used as a wrapper in this walk-through.  The following is the shell script that is based on the above mention pin commands. It is placed into the 'bin/elf' directory.

	#!/bin/sh
	#pin_wrap.sh
	/vagrant/pin-2.14-67254-gcc.4.4.7-linux/pin -t /vagrant/pin-2.14-67254-gcc.4.4.7-linux/source/tools/ManualExamples/obj-ia32/inscount0.so -- $1

Notice how the first parameter from cb-server was passed into the pintool.  Don't forget to make the script executable.

	chmod +x bin/elf/pin_wrap.sh


The server can be started by passing in the '-w' flag once the wrapper script is complete.

	$ cb-server --insecure -p 10000 -d bin/elf -w pin_wrap.sh YAN01_00001

Use cb-replay to replay the xml file and check the number of instructions counted.
	
	$ cb-replay --host 127.0.0.1 --port 10000 TESTINPUT.xml
	# service - TESTINPUT.xml
	ok 1 - bytes received
	ok 2 - match: string
	ok 3 - write: sent 6 bytes
	ok 4 - bytes received
	ok 5 - match: string
	ok 6 - write: sent 2 bytes
	ok 7 - match: string
	ok 8 - bytes received
	ok 9 - match: string
	ok 10 - write: sent 2 bytes
	ok 11 - bytes received
	ok 12 - match: string
	ok 13 - write: sent 2 bytes
	ok 14 - bytes received
	ok 15 - match: string
	# passed: 15
	# failed: 0
	# total passed: 15
	# total failed: 0

	$ more bin/elf/inscount.out 
	Count 10151
	

You can also run the pintool on a multi-binary CB the same way. The only thing to keep in mind is that the output file for the log should be different for each binary. As an example, cb-server will run the EAGLE_00004 CB with the following wrapper script.

	#!/bin/sh
	#pin_wrap.sh

	/vagrant/pin-2.14-67254-gcc.4.4.7-linux/pin -t /vagrant/pin-2.14-67254-gcc.4.4.7-linux/source/tools/ManualExamples/obj-ia32/inscount0.so -o inscount_$1.out -- $1

Notice how the only difference between this script and the previous one is an additional option to the pintool to use unique log files.

	$ cb-server --insecure -p 10000 -d bin/elf -w pin_wrap.sh EAGLE_00004_1 EAGLE_00004_2 EAGLE_00004_3
	
cb-replay will be run as normal and before examining the resulting instruction counts from the pintool.

	$ cb-replay --debug --host 127.0.0.1 --port 10000 poller/for-release/poller-1.xml 
	# EAGLE_00004 - poller/for-release/poller-1.xml
	ok 1 - write: sent 1905 bytes
	# received 'OUT: 0x2b15a909\n'
	ok 2 - match: string
	# received 'OUT: 0x9c369091\n'
	ok 3 - match: string
	# received 'OUT: 0xd1013543\n'
	...
	ok 83 - match: string
	# passed: 83
	# failed: 0
	# total passed: 83
	# total failed: 0

## Pintool Source

### Source for libcgc_pin.h

	#ifndef _LIBCGC_PIN_H
	#define _LIBCGC_PIN_H
	
	//NOTE: I just prefixed everything with CGC or cgc 
	// so that these declarations are different from the standard (e.g. linux)
	// ones.
	
	#define CGC_STDIN 0
	#define CGC_STDOUT 1
	#define CGC_STDERR 2
	
	#ifndef NULL
	#define NULL ((void *)0)
	#endif
	
	typedef long unsigned int cgc_size_t;
	typedef long signed int cgc_ssize_t;
	
	#define CGC_SSIZE_MAX       2147483647
	#define CGC_SIZE_MAX        4294967295
	#define CGC_FD_SETSIZE      1024
	
	typedef long int cgc_fd_mask;
	
	#define CGC_NFDBITS (8 * sizeof(cgc_fd_mask))
	
	typedef struct {
	        cgc_fd_mask _fd_bits[CGC_FD_SETSIZE / CGC_NFDBITS];
	} cgc_fd_set;
	
	#define CGC_FD_ZERO(set)                                                    \
	        do {                                                            \
	                cgc_size_t __i;                                                \
	                for (__i = 0; __i < (CGC_FD_SETSIZE / CGC_NFDBITS); __i++)     \
	                        (set)->_fd_bits[__i] = 0;                               \
	        } while (0)
	#define CGC_FD_SET(b, set) \
	        ((set)->_fd_bits[b / CGC_NFDBITS] |= (1 << (b & (CGC_NFDBITS - 1))))
	#define CGC_FD_CLR(b, set) \
	        ((set)->_fd_bits[b / CGC_NFDBITS] &= ~(1 << (b & (CGC_NFDBITS - 1))))
	#define CGC_FD_ISSET(b, set) \
	        ((set)->_fd_bits[b / CGC_NFDBITS] & (1 << (b & (CGC_NFDBITS - 1))))
	
	struct cgc_timeval {
	        int tv_sec;
	        int tv_usec;
	};
	
	#define CGC_EBADF           1
	#define CGC_EFAULT          2
	#define CGC_EINVAL          3
	#define CGC_ENOMEM          4
	#define CGC_ENOSYS          5
	#define CGC_EPIPE           6
	
	//Some additional definitions
	#define _TERMINATE 1
	#define _TRANSMIT 2
	#define _RECEIVE 3
	#define _FDWAIT 4
	#define _ALLOCATE 5
	#define _DEALLOCATE 6
	#define _RANDOM 7
	
	#define CGC_PAGE_SIZE	4096
	#define CGC_PAGE_MASK	(~(CGC_PAGE_SIZE - 1))
	
	#endif /* _LIBCGC_PIN_H */
	

### Source for inscount0.cpp

	/** CGC Instruction Count Example 
	 *  @author Lok Yan
	 *  @data 25 Aug 2014
	
	 * Note that this was only tested on 32bit systems - we might need to fix some
	 *  copying operations
	**/
	
	#include <iostream>
	#include <fstream>
	#include "pin.H"
	
	
	/********************************************/
	/** START OF CGC SYS_CALL EMULATOR SECTION **/
	/********************************************/
	
	//#include <malloc.h>
	#include <cstdlib>
	#include <unistd.h> // for dup, write, etc.
	#include <cerrno>
	#include <sys/mman.h> // for mmap
	#include <cstring>
	#include <cstdio> //for fopen
	
	//Include the cgc definitions
	#include "libcgc_pin.h"
	
	//a mode that passes the syscalls directly through to the kernel
	KNOB<BOOL> KnobModePassthrough(KNOB_MODE_WRITEONCE, "pintool",
	  "p", "1", "Syscall passthrough mode");
	
	//a mode that emulates the system calls using file inputs
	KNOB<BOOL> KnobModeEmulation(KNOB_MODE_WRITEONCE, "pintool",
	  "e", "0", "Syscall emulation mode");
	KNOB<string> KnobFDMap(KNOB_MODE_APPEND, "pintool",
	  "fd", "" , "File descriptor number to file mappings, \n"
	             "\t  e.g., -fd 0,mystdin will use 'mystdin' as input to fd 0\n"
	             "\t        -fd 0,mystdin -fd 1,mystdout will use 'mystdin' as input to 0 and 'mystdout' to 1");
	KNOB<string> KnobRandFile(KNOB_MODE_WRITEONCE, "pintool",
	  "rand", "/dev/urandom", "Filename for the source of random bytes");
	
	//NOTE: We are going to use a MAP for now - but perhaps a clean implementation will have 
	// a smaller footprint
	/* -- unordered_map is unsupported in cgc vm
	#include <unordered_map>
	typedef std::unordered_map<int, FILE*> fd_map_t;
	*/
	
	#include <map>
	typedef std::map<int, FILE*> fd_map_t;
	fd_map_t cgc_fds; //faster than a regular map
	
	FILE* randfd = NULL;
	
	VOID cgc_cleanup_files()
	{
	  //close all of the open files
	  while (!cgc_fds.empty())
	  {
	    fd_map_t::iterator it = cgc_fds.begin();
	    fclose(it->second);
	    cgc_fds.erase(it);
	  }
	  
	  if (randfd != NULL)
	  {
	    fclose(randfd);
	  }
	}
	
	/**
	 * This function is called before the analysis target is loaded
	**/
	VOID cgc_init(VOID* v)
	{
	  //0. Make sure that the size of fd_set and cgc_fd_set are the same
	  if (sizeof(fd_set) != sizeof(cgc_fd_set))
	  {
	    cerr << "ERROR!!! The sizeof native fd_set and cgc_fd_set are not the same" << endl;
	    cgc_cleanup_files();
	    exit(-2);
	  }
	
	  //1. First, we want to open up the randomness source
	  //The default value for KnobRandFile is /dev/urandom so KnobRandFile should always be well
	  // defined
	  randfd = fopen(KnobRandFile.Value().c_str(), "rb");
	  if (randfd == NULL)
	  {
	    cerr << "The random source file [" << KnobRandFile.Value() << "] could not be opened" << endl;
	    cgc_cleanup_files();
	    exit(-1);
	  }
	
	  //2. Next we want to see if emulation mode is enabled, if so then open up the rest of the files
	  //if we are going to emulate, then we would like to load the files corresponding
	  // to the defined fd numbers 
	  if (KnobModeEmulation)
	  {
	    //NOTE: All files are opened for read/write and in binary mode
	    for (size_t i = 0; i < KnobFDMap.NumberOfValues(); i++)
	    {
	      const string& str = KnobFDMap.Value(i);
	      std::string::size_type commaPos = str.find(',');
	   
	      int fdnum = 0;
	
	      /** std::stoi doesn't seem to exist in the cgc VM either -- so switching to strtol
	      try
	      {
	        fdnum = std::stoi(str.substr(0, commaPos - 1));
	      }
	      catch (std::invalid_argument e)
	      {
	        cerr << "Invalid argument received [" << str << "]" << endl;
	        cgc_cleanup_files();
	        exit(-1);
	      }
	      **/
	      
	      const char* cstr = str.c_str(); 
	      char* tempp = NULL;
	
	      fdnum = strtol(cstr, &tempp, 10);
	      //I am counting on some initial tests that shows strtol will stop at 
	      // the , if conversion was good and it will go beyond it if conversion
	      // was unsuccessful
	      if ( (tempp != (cstr + commaPos)) )
	      {
	        cerr << "Could not convert the fd in [" << str << "]" << endl;
	        cgc_cleanup_files();
	        exit(-1);
	      }
	
	      FILE* fp = fopen(str.substr(commaPos + 1).c_str(), "r+b");
	      if (fp == NULL)
	      {
	        cerr << "Could not open file [" << str.substr(commaPos+1) << "] for rw" << endl;
	        cgc_cleanup_files();
	        exit(-1);
	      }
	
	      if (cgc_fds.find(fdnum) != cgc_fds.end())
	      {
	        //if it exists already then errror
	        cerr << "The file for fd [" << fdnum << "] has already beed defined" << endl;
	        cgc_cleanup_files();
	        exit(-1);
	      }
	      
	      //everything checks out so add in the new entry 
	      cgc_fds[fdnum] = fp;
	    }//end for KnobFDMap.NumberOfValues
	  }//END if emulation
	
	  /** INSERT PINTOOLS INITIALIZATIONS HERE **/
	  /** END PINTOOLS INITIALIZATION SECTION **/
	}
	
	/** 
	 * This function is called when the program ends
	 * That is BEFORE the terminate system call is called
	**/
	VOID cgc_cleanup(INT32 code, VOID* v)
	{
	  cgc_cleanup_files();
	}
	
	
	
	#define CGC_SET_RETURN(_ctx, _val) PIN_SetContextReg(_ctx, REG_EAX, _val)
	
	/**
	 * This function is called if the system call number is 1 (_terminate)
	 * Notice that we don't need to do anything here because 1 is also
	 *   the system call number for sys_exit in 32bit linux. 
	 * If the host is 64bit, then we will need to change the sys_call number
	 *   to the proper value. Might have to fix the register values as well.
	**/
	VOID emulate_terminate(CONTEXT* ctx)
	{
	}
	
	/**
	 * Emulation function for sys call 2 (transmit)
	 * The basic idea is that, we can either pass this call through to the host
	 *   in which case we will need to worry about the file descriptors being 
	 *   shared between the pintool and the analysis target. We get around this
	 *   problem by writing our own wrapper launcher that will preallocate the 
	 *   file descriptors that the analysis target might need before transferring
	 *   control to the pintool. This way, the fds used by the pintools will be
	 *   above the ones needed by the CB.
	 * The other method is to emulate the file descriptors. This works by changing
	 *   all transmits into fwrites into the files that the user have defined
	 *   using the -fd #,filename arguments. If an argument was not defined, then
	 *   we default to passthrough mode (e.g. when user only passes in -fd 0,input.txt
	 *   we will emulate receive from fd 0 with a fread from input.txt but we will
	 *   just pass transmits to fd 1 right into stdout.)
	**/
	VOID emulate_transmit(CONTEXT* ctx)
	{
	  cgc_size_t stemp = 0;
	
	  size_t stret = 0;
	  ssize_t sstret = 0;
	
	  if (ctx == NULL)
	  {
	    return;
	  }
	
	  //int transmit(int fd, const void *buf, size_t count, size_t *tx_bytes);
	  ADDRINT fd = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT buf = PIN_GetContextReg(ctx, REG_ECX);
	  ADDRINT count = PIN_GetContextReg(ctx, REG_EDX);
	  ADDRINT tx_bytes = PIN_GetContextReg(ctx, REG_ESI);
	
	
	  /**
	       EBADF    fd is not a valid file  descriptor
	                or is not open.
	       EFAULT   buf   or  tx_bytes  points  to  an
	                invalid address.
	  **/
	 
	  //TODO: Make sure that the error logic is the same as in the kernel
	  // For example, right now we make sure that tx_bytes is writeable first
	  // before actually calling write. 
	    
	  if ((void*)tx_bytes != NULL)
	  {
	    if (PIN_SafeCopy((void*)(&stemp), (void*)(tx_bytes), sizeof(cgc_size_t)) != sizeof(cgc_size_t))
	    {
	      CGC_SET_RETURN(ctx, -CGC_EFAULT);
	      goto SKIP_INT;
	    }
	  } 
	
	  //we will try the emulation mode first - since not all fds might be defined
	  // for the ones that are not defined - we want to just pass through
	
	  if (KnobModeEmulation)
	  {
	    //in this case, we want to send it out to a file instead of using write 
	    fd_map_t::iterator it = cgc_fds.find(fd);
	    if (it != cgc_fds.end()) //if it exists then process
	    {
	      stret = fwrite((void*)buf, 1, (size_t)count, it->second);
	
	      //NOTE: is there anything to do with the return value? 
	      if (stret < count)
	      {
	        //TODO:what to return if there is an error?
	      }
	
	      if ((void*)tx_bytes != NULL)
	      {
	        stret = PIN_SafeCopy((void*)tx_bytes, (void*)(&stret), sizeof(cgc_size_t)); //this should work 
	      }
	      
	      CGC_SET_RETURN(ctx, 0);
	      goto SKIP_INT;
	    }
	    
	    //if the entry is not found then just pass it through
	  }
	
	  //PASSTHROUGH MODE - KnobModePassthrough is always TRUE
	  //if we are just passing it through then call write
	  sstret = write(fd, (void*)buf, count);
	  if (sstret >= 0)
	  {
	    CGC_SET_RETURN(ctx, 0); // we wrote something so set the return to 0
	
	    if ((void*)tx_bytes != NULL)
	    {
	      stret = PIN_SafeCopy((void*)tx_bytes, (void*)(&sstret), sizeof(cgc_size_t)); //this should work
	    }
	  } 
	  else // an error occurred
	  {
	    switch (sstret)
	    {
	      case (-EINVAL):
	      case (-EBADF):
	      {
	        CGC_SET_RETURN(ctx, -CGC_EBADF);
	        break;
	      }
	      default:
	      {
	        CGC_SET_RETURN(ctx, -CGC_EFAULT);
	        break;
	      }
	    }
	  }
	    
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	/**
	 * Function to emulate syscall 3 (receive)
	 * See the comments for emulate_transmit
	**/
	VOID emulate_receive(CONTEXT* ctx)
	{  
	  cgc_size_t stemp = 0;
	  size_t stret = 0;
	  ssize_t sstret = 0;
	
	  if (ctx == NULL)
	  {
	    return;
	  }
	
	  //int receive(int fd, void *buf, size_t count, size_t *rx_bytes)
	  
	  ADDRINT fd = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT buf = PIN_GetContextReg(ctx, REG_ECX);
	  ADDRINT count = PIN_GetContextReg(ctx, REG_EDX);
	  ADDRINT rx_bytes = PIN_GetContextReg(ctx, REG_ESI);
	
	  /**
	       EBADF    fd is not a valid file  descriptor
	                or is not open.
	       EFAULT   buf   or  rx_bytes  points  to  an
	                invalid address.
	  **/
	
	  //TODO: Make sure that the error logic is the same as in the kernel
	  // For example, right now we make sure that rx_bytes is writeable first
	  // before actually calling write. 
	    
	  if ((void*)rx_bytes != NULL)
	  {
	    if (PIN_SafeCopy((void*)(&stemp), (void*)(rx_bytes), sizeof(cgc_size_t)) != sizeof(cgc_size_t))
	    {
	      CGC_SET_RETURN(ctx, -CGC_EFAULT);
	      goto SKIP_INT;
	    }
	  } 
	
	  if (KnobModeEmulation)
	  {
	    //in this case, we want to read from a file
	    fd_map_t::iterator it = cgc_fds.find(fd);
	    if (it != cgc_fds.end()) //if it exists then process
	    {
	      stret = fread((void*)buf, 1, (size_t)count, it->second);
	
	      if (stret == 0) //if there is an error
	      {
	        if (!feof(it->second))
	        {
	          //TODO: What to do if there is an error - and not just the end of file?
	        }
	      }
	      //NOTE: is there anything to do with the return value? 
	      if ((void*)rx_bytes != NULL)
	      {
	        stret = PIN_SafeCopy((void*)rx_bytes, (void*)(&stret), sizeof(cgc_size_t)); //this should work 
	      }
	      
	      CGC_SET_RETURN(ctx, 0);
	      goto SKIP_INT;
	    }
	    
	    //if the entry is not found then just pass it through
	  }
	
	  //PASSTHROUGH MODE
	  //if we are just passing it through then call write
	  sstret = read(fd, (void*)buf, count);
	  if (sstret >= 0)
	  {
	    CGC_SET_RETURN(ctx, 0); // we wrote something so set the return to 0
	
	    if ((void*)rx_bytes != NULL)
	    {
	      stret = PIN_SafeCopy((void*)rx_bytes, (void*)(&sstret), sizeof(cgc_size_t)); //this should work
	    }
	  } 
	  else // an error occurred
	  {
	    switch (sstret)
	    {
	      case (-EINVAL):
	      case (-EBADF):
	      {
	        CGC_SET_RETURN(ctx, -CGC_EBADF);
	        break;
	      }
	      default:
	      {
	        CGC_SET_RETURN(ctx, -CGC_EFAULT);
	        break;
	      }
	    }
	  }
	    
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	
	
	int CGC_FD_IS_SET_EMPTY(cgc_fd_set* set)
	{
	  cgc_size_t i = 0;
	  if (set == NULL)
	  {
	    return (1);
	  }
	
	  for (i = 0; i < (CGC_FD_SETSIZE / CGC_NFDBITS); i++)
	  {
	    if (set->_fd_bits[i] != 0)
	    {
	      return (0);
	    }
	  }
	  
	  return (1);
	}
	
	/**
	 * This emulates syscall 4 (fdwait)
	 * Since fdwait is just like select, we will pass through
	 *   the parameters directly to select. This assumes that
	 *   the definitions for fd_set are the same between the CGC binary
	 *   and the host system. We do a quick and dirty check by
	 *   making sure that they are the same size. The definitions for FD_SETSIZE and 
	 *   CGC_FD_SETSIZE might be different.
	 * If we are running in emulation mode, then what we do is just
	 *   set the file descriptors ourselves as long as the fd number
	 *   to file map is defined. If it is not defined then we pass
	 *   the undefined fds to select.
	**/
	VOID emulate_fdwait(CONTEXT* ctx)
	{
	  int iret = 0;
	  int numReady = 0;
	  size_t stret = 0;
	
	  cgc_fd_set tempReadSet;
	  cgc_fd_set* pTempReadSet = NULL;
	  cgc_fd_set tempWriteSet;
	  cgc_fd_set* pTempWriteSet = NULL;
	
	  cgc_fd_set retReadSet;
	  cgc_fd_set* pRetReadSet = NULL;
	  cgc_fd_set retWriteSet;
	  cgc_fd_set* pRetWriteSet = NULL;
	  
	  /**
	  int  fdwait(int nfds, fd_set *readfds, fd_set *writefds, const struct timeval *timeout,
	       int *readyfds);
	  **/
	
	  ADDRINT nfds = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT readfds = PIN_GetContextReg(ctx, REG_ECX);
	  ADDRINT writefds  = PIN_GetContextReg(ctx, REG_EDX);
	  ADDRINT timeout = PIN_GetContextReg(ctx, REG_ESI);
	  ADDRINT readyfds = PIN_GetContextReg(ctx, REG_EDI);
	
	  /**
	       EBADF    an  invalid file descriptor was
	                given in one of the sets  (per‐
	                haps a file descriptor that was
	                already closed, or one on which
	                an error has occurred).
	       EINVAL   nfds  is  negative or the value
	                contained  within  *timeout  is
	                invalid.
	
	       EFAULT   One  of  the arguments readfds,
	                writefds,   timeout,   readyfds
	                points to an invalid address.
	       ENOMEM   unable  to  allocate memory for
	                internal tables.
	  **/
	 
	
	  if ((int)nfds < 0)
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	    goto SKIP_INT;
	  }
	
	  //NOTE: We are enforcing the less than CGC_FD_SETSIZE which might not be what
	  // the kernel is doing
	  if ((int)nfds > CGC_FD_SETSIZE)
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	    goto SKIP_INT;
	  }
	
	  //first we make a copy of the fd_set lists
	  if ((cgc_fd_set*)readfds != NULL)
	  {
	    pTempReadSet = &tempReadSet;
	    stret = PIN_SafeCopy((void*)pTempReadSet, (void*)readfds, sizeof(cgc_fd_set));
	    if (stret != sizeof(cgc_fd_set))
	    {
	      CGC_SET_RETURN(ctx, -CGC_EFAULT);
	      goto SKIP_INT;
	    }
	
	    //we also want the retReadSet to be zeroed out
	    // it will be set as fds are ready
	    pRetReadSet = &retReadSet;
	    CGC_FD_ZERO(pRetReadSet);
	  }
	  
	  if ((cgc_fd_set*)writefds != NULL)
	  {
	    pTempWriteSet = &tempWriteSet;
	    stret = PIN_SafeCopy((void*)pTempWriteSet, (void*)writefds, sizeof(cgc_fd_set));
	    if (stret != sizeof(cgc_fd_set))
	    {
	      CGC_SET_RETURN(ctx, -CGC_EFAULT);
	      goto SKIP_INT;
	    }
	
	    pRetWriteSet = &retWriteSet;
	    CGC_FD_ZERO(pRetWriteSet);
	  }
	
	  //now we should have pTempReadSet and pTrempWriteSet pointing to copies
	  // of the corresponding sets - OR NULL
	
	  //So lets go through emulation mode first and see if there are any fds that
	  // are already mapped
	  if (KnobModeEmulation)
	  {
	    for (int i = 0; (i < (int)nfds); i++)
	    {
	      if (cgc_fds.find(i) != cgc_fds.end())
	      {
	        //if the file exists - then remove the set bit now
	        if (pTempReadSet != NULL)
	        {
	          //if we are watching this particular fd
	          if (CGC_FD_ISSET(i, pTempReadSet))
	          {
	            //clear the corresponding bit in case we need to call select later
	            CGC_FD_CLR(i, pTempReadSet);
	            //but also set the same bit in the return set
	            CGC_FD_SET(i, pRetReadSet);
	            //increment the number of Ready fds
	            numReady++;
	          }
	        }
	
	        //do the same for the write set
	        if (pTempWriteSet != NULL)
	        {
	          //if we are watching this particular fd
	          if (CGC_FD_ISSET(i, pTempWriteSet))
	          {
	            //clear the corresponding bit in case we need to call select later
	            CGC_FD_CLR(i, pTempWriteSet);
	            //but also set the same bit in the return set
	            CGC_FD_SET(i, pRetWriteSet);
	            numReady++;
	          }
	        }
	      }
	    }
	
	    //At this point in time - temp*Set should be the left over any real fds that we don't have a
	    // file mapping to. We don't change nfds because one of the unmapped fds could be at the end
	    //TODO: Finally, note that the above logic WILL NOT WORK for read-only or write-only fds
	    // such as 0, 1, and 2. They will be counted twice since all files are opened as read and
	    // writeable.  
	  }
	  
	  //PASSTHROUGH MODE
	  /**
	  static int asmlinkage
	  cgcos_fdwait(int nfds, fd_set __user *readfds, fd_set __user *writefds,
	               struct timeval __user *timeout, int __user *readyfds) {
	    int res;
	    if (readyfds != NULL &&
	        !access_ok(VERIFY_WRITE, readyfds, sizeof(*readyfds)))
	      return (-EFAULT);
	
	    res = sys_select(nfds, readfds, writefds, NULL, timeout);
	
	    if (res < 0)
	      return (res);
	
	    if (readyfds != NULL && copy_to_user(readyfds, &res, sizeof(*readyfds)))
	      return (-EFAULT);
	
	    return (0);
	  }
	  **/
	
	  //if its emulation mode - then we want to skip this if the fdsets are now empty
	  if (CGC_FD_IS_SET_EMPTY(pTempReadSet) && CGC_FD_IS_SET_EMPTY(pTempWriteSet))
	  {
	    //if they are both empty then just skip the select step but to make sure iret is 0
	    iret = 0; 
	  }
	  else
	  {
	    iret = select((int)nfds, (fd_set*)pTempReadSet, (fd_set*)pTempWriteSet, NULL, (struct timeval*)timeout);
	  }
	 
	  //if its emulation mode we need to combine the results
	  if (iret < 0)
	  {
	    //either way - if select failed then an error occurred so we will just ignore
	    // all of temporary work we did above with the temporary knobs
	    CGC_SET_RETURN(ctx, iret);
	    goto SKIP_INT;
	  } 
	  else
	  {
	    if (KnobModeEmulation && (numReady > 0))
	    {
	      if (iret > 0)
	      {
	        //if its emulation mode AND we have some fds that are set AND select set some more
	        // then we need to merge the previous results with the ones from tempRead and WriteSets
	        for (cgc_size_t i = 0; i < (CGC_FD_SETSIZE / CGC_NFDBITS); i++)
	        {
	          if ( (pRetReadSet != NULL) && (pTempReadSet != NULL) ) //the two points should be consistent
	          {
	            pRetReadSet->_fd_bits[i] |= pTempReadSet->_fd_bits[i];
	          }
	          if ( (pRetWriteSet != NULL) && (pTempWriteSet != NULL) )
	          {
	            pRetWriteSet->_fd_bits[i] |= pTempWriteSet->_fd_bits[i];
	          }
	        }
	      }
	     
	      //We also need to update the total number
	      numReady += iret;
	    }
	    else
	    {
	      //since KnobModeEmulation was not set or there weren't anything of interest
	      // we can just set the return pointers to the tempSets that we passed into select
	      pRetReadSet = pTempReadSet;
	      pRetWriteSet = pTempWriteSet;
	      numReady = iret;
	    }
	
	    //by now pRetReadSet and pRetWriteSet should have all of the bits for ready fds
	    // set and numReady has the number of fds that are ready
	
	    //Lets copy back to the user
	    if ( ((void*)readfds != NULL) && (pRetReadSet != NULL) ) //once again these should be consistently NULL or non NULL at the same time.
	    {
	      stret = PIN_SafeCopy((void*)readfds, (void*)pRetReadSet, sizeof(cgc_fd_set));
	      if (stret != sizeof(cgc_fd_set))
	      {
	        CGC_SET_RETURN(ctx, -CGC_EFAULT);
	        goto SKIP_INT;
	      }
	    }
	
	    if ( ((void*)writefds != NULL) && (pRetWriteSet != NULL) ) //once again these should be consistently NULL or non NULL at the same time.
	    {
	      stret = PIN_SafeCopy((void*)writefds, (void*)pRetWriteSet, sizeof(cgc_fd_set));
	      if (stret != sizeof(cgc_fd_set))
	      {
	        CGC_SET_RETURN(ctx, -CGC_EFAULT);
	        goto SKIP_INT;
	      }     
	    }
	
	    if ((int*)readyfds != NULL)
	    {
	      stret = PIN_SafeCopy((void*)readyfds, (void*)(&numReady), sizeof(int));
	      if (stret != sizeof(int))
	      {
	        CGC_SET_RETURN(ctx, -CGC_EFAULT);
	        goto SKIP_INT;
	      }
	    }
	
	    CGC_SET_RETURN(ctx, 0); //success
	  }//end else error from select
	
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	/**
	 * allocate is a wrapper of sorts for mmap so we just pass
	 *   this one through mmap. There is no difference between emulation
	 *   and passthrough mode at the moment.
	 * As one would expect, and is well documented, the allocation 
	 *   behavior is going to be different between the CGC binary running
	 *   in PIN and one running natively by itself.
	**/
	VOID emulate_allocate(CONTEXT* ctx)
	{
	  ADDRINT temp = 0;
	  void* p = NULL;
	
	  if (ctx == NULL)
	  {
	    return;
	  }
	
	  //int allocate(size_t length, int is_X, void **addr)
	
	  ADDRINT len = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT is_X = PIN_GetContextReg(ctx, REG_ECX);
	  ADDRINT addr = PIN_GetContextReg(ctx, REG_EDX);
	
	  /**
	       EINVAL   length is zero.
	       EINVAL   length is too large.
	       EFAULT   addr   points   to  an  invalid
	                address.
	       ENOMEM   No memory is available  or  the
	                process'   maximum   number  of
	                allocations  would  have   been
	                exceeded.
	  **/  
	
	  if (len == 0)
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	    goto SKIP_INT;
	  }
	       
	  if ((void*)addr == NULL)
	  {
	    CGC_SET_RETURN(ctx, -CGC_EFAULT);
	    goto SKIP_INT;
	  }
	 
	  //try to read from the target address first to see if the memory address is valid
	  if (PIN_SafeCopy(&temp, (void*)(addr), sizeof(ADDRINT)) != sizeof(ADDRINT))
	  {
	    CGC_SET_RETURN(ctx, -CGC_EFAULT);
	    goto SKIP_INT;
	  }
	
	  //if we are here then the addr is valid so lets call mmap
	  p = mmap(0, len, PROT_READ | PROT_WRITE | (is_X ? PROT_EXEC : 0), MAP_PRIVATE | MAP_ANON, -1, 0); 
	 
	  if (p == (void*)(-1))
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	  }
	  else
	  {
	    PIN_SafeCopy((void*)addr, &p, sizeof(void*));
	    CGC_SET_RETURN(ctx, 0);
	  }
	
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	/**
	 * See emulate_allocate for more info
	**/
	VOID emulate_deallocate(CONTEXT* ctx)
	{
	  int ret = 0;
	
	  if (ctx == NULL)
	  {
	    return;
	  }
	
	  //int deallocate(void *addr, size_t length)
	
	  ADDRINT addr = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT len = PIN_GetContextReg(ctx, REG_ECX);
	
	  /**
	       EINVAL   addr is not page aligned.
	       EINVAL   length is zero.
	       EINVAL   any part of  the  region  being
	                deallocated   is   outside  the
	                valid  address  range  of   the
	                process.
	  **/
	
	  if ( (addr & (~CGC_PAGE_MASK)) || (len == 0) )
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	    goto SKIP_INT;
	  }
	
	  ret = munmap((void*)addr, len);
	
	  if (ret != 0)
	  {
	    CGC_SET_RETURN(ctx, -CGC_EINVAL);
	  }
	  else
	  {
	    CGC_SET_RETURN(ctx, 0);
	  } 
	
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	/**
	 * According to the kernel documentation there are three
	 *   ways to get_random_bytes - the first is the kernel function
	 *   with the same name, the second is from the user space through
	 *   /dev/random and the third is from /dev/urandom
	 *   Since there isn't a direct sys_call for random, we will emulate
	 *   this from the userspace. 
	 * According to the source in linux-source-3.13.2-cgc/drivers/char/random.c
	 *   get_random_bytes calls extract_entropy using the nonblocking_pool
	 *   /dev/random calls the userspace version using the blocking_pool
	 *   /dev/urandom calls it using the nonblocking_pool
	 *   and so, we will use /dev/urandom as the randomness source
	 * No matter the mode, randfd should be pointing to the right file or 
	 *   /dev/urandom
	**/
	VOID emulate_random(CONTEXT* ctx)
	{
	  size_t stret = 0;
	  //int random(void *buf, size_t count, size_t *rnd_bytes)
	
	  ADDRINT buf = PIN_GetContextReg(ctx, REG_EBX);
	  ADDRINT count = PIN_GetContextReg(ctx, REG_ECX);
	  ADDRINT rnd_bytes = PIN_GetContextReg(ctx, REG_EDX);
	
	  /**
	    EINVAL   count is invalid.
	    EFAULT   buf  or  rnd_bytes points to an
	                invalid address.
	  */
	
	  stret = fread((void*)buf, 1, (size_t)count, randfd);
	  if (stret < count) //an error has occurred
	  {
	    //first we check to see if eof has been reached
	    if (feof(randfd)) //this should only happen if fdrand is a file, /dev/urandom should not give us an eof
	    {
	      size_t bytesLeft = (size_t) count - stret;
	      fseek(randfd, 0, SEEK_SET); //go back to the beginning of the file
	      stret = fread((void*)(buf + stret), 1, bytesLeft, randfd); //read again
	      if (stret < bytesLeft) //another error - then just die
	      {
	        //TODO: How to die? Neither EINVAL nor EFAULT seems to be the right thing to do  
	      } 
	      else
	      {
	        //success so set the return value and go
	        goto SUCCESS; //not really needed
	      }
	    }
	    else
	    {
	      //NOTE: We will just assume that buf is wrong
	      CGC_SET_RETURN(ctx, -CGC_EFAULT);
	      goto SKIP_INT;
	    } 
	  }
	
	  SUCCESS:
	  if ((void*)rnd_bytes != NULL)
	  {
	    
	    stret = PIN_SafeCopy((void*)rnd_bytes, (void*)(&count), sizeof(cgc_size_t));
	    CGC_SET_RETURN(ctx, 0);
	  }
	
	  SKIP_INT:
	  ADDRINT curIP = PIN_GetContextReg(ctx, REG_EIP);
	
	  //int 0x80 is cd 80 in hex which is two bytes
	  //get the parameters off the stack first
	  PIN_SetContextReg(ctx, REG_EIP, curIP + 2);
	  PIN_ExecuteAt(ctx); //execute after the instruction
	}
	
	/**
	 * Our own small little syscall handler
	**/
	VOID cgc_syscallHandler(CONTEXT* ctx)
	{
	  if (ctx == NULL)
	  {
	    return;
	  }
	
	  //Check the syscall number
	  switch(PIN_GetContextReg(ctx, REG_EAX))
	  {
	    case (_TERMINATE):
	    {
	      emulate_terminate(ctx); 
	      break;
	    }
	    case (_TRANSMIT):
	    {
	      emulate_transmit(ctx); 
	      break;
	    }
	    case (_RECEIVE):
	    {
	      emulate_receive(ctx); 
	      break;
	    }
	    case (_FDWAIT):
	    {
	      emulate_fdwait(ctx); 
	      break;
	    }
	    case (_ALLOCATE):
	    {
	      emulate_allocate(ctx); 
	      break;
	    }
	    case (_DEALLOCATE):
	    {
	      emulate_deallocate(ctx); 
	      break;
	    }
	    case (_RANDOM):
	    {
	      emulate_random(ctx); 
	      break;
	    }
	    default:
	    {
	      //TODO: Right now we don't do anything,
	      // meaning we just pass the syscall through
	      //This is not the right behavior, since an 
	      // undefined cgc syscall is actually defined
	      // on Linux which is the context that PIN is running under
	      break;
	    }
	  }
	}
	
	/**
	 * We need an instruction handler so we can skip the int 0x80 instructions
	**/
	VOID cgc_instrumentInstruction(INS ins, VOID* v)
	{
	  //NOTE: Instead of using INS_isSyscall we will look for int 0x80 instead
	  //We could use INT_isInterrupt as well, but that covers more opcodes
	  // than just INT Immediate
	  if (INS_Opcode(ins) == XED_ICLASS_INT)
	  {
	    if ( (INS_OperandIsImmediate(ins, 0)) //its an immediate operand
	         && (INS_OperandImmediate(ins, 0) == 0x80) //and its 0x80
	       )
	    {
	      
	      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)cgc_syscallHandler,
	                     IARG_CALL_ORDER, CALL_ORDER_FIRST, //NOTE: We want to be called first, but you can change it
	                     IARG_CONTEXT,
	                     IARG_END
	                    );
	
	      //NOTE: We don't just delete the instruction at this point - we will update
	      // the PC and then call PIN_ExecuteAt to bypass these instructions later
	    }
	  }
	}
	
	/********************************************/
	/** END OF EMULATION SECTION **/
	/********************************************/
	
	/*BEGIN_LEGAL
	Intel Open Source License
	
	Copyright (c) 2002-2014 Intel Corporation. All rights reserved.
	
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are
	met:
	
	Redistributions of source code must retain the above copyright notice,
	this list of conditions and the following disclaimer.  Redistributions
	in binary form must reproduce the above copyright notice, this list of
	conditions and the following disclaimer in the documentation and/or
	other materials provided with the distribution.  Neither the name of
	the Intel Corporation nor the names of its contributors may be used to
	endorse or promote products derived from this software without
	specific prior written permission.
	
	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
	``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
	LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
	A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
	ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
	LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
	THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
	(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	END_LEGAL */
	
	ofstream OutFile;
	
	// The running count of instructions is kept here
	// make it static to help the compiler optimize docount
	static UINT64 icount = 0;
	
	// This function is called before every instruction is executed
	VOID docount() { icount++; }
	    
	// Pin calls this function every time a new instruction is encountered
	VOID Instruction(INS ins, VOID *v)
	{
	    // Insert a call to docount before every instruction, no arguments are passed
	    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_END);
	}
	
	KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
	    "o", "inscount.out", "specify output file name");
	
	// This function is called when the application exits
	VOID Fini(INT32 code, VOID *v)
	{
	    // Write to a file since cout and cerr maybe closed by the application
	    OutFile.setf(ios::showbase);
	    OutFile << "Count " << icount << endl;
	    OutFile.close();
	}
	
	/* ===================================================================== */
	/* Print Help Message                                                    */
	/* ===================================================================== */
	
	INT32 Usage()
	{
	    cerr << "This tool counts the number of dynamic instructions executed" << endl;
	    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
	    return -1;
	}
	
	/* ===================================================================== */
	/* Main                                                                  */
	/* ===================================================================== */
	/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
	/* ===================================================================== */
	
	int main(int argc, char * argv[])
	{
	    // Initialize pin
	    if (PIN_Init(argc, argv)) return Usage();
	
	    OutFile.open(KnobOutputFile.Value().c_str());
	
	    PIN_AddApplicationStartFunction(cgc_init, NULL);
	
	    /** ADD CGC CALLBACK **/
	    INS_AddInstrumentFunction(cgc_instrumentInstruction, NULL);
	
	    // Register Instruction to be called to instrument instructions
	    INS_AddInstrumentFunction(Instruction, 0);
	
	    // Register Fini to be called when the application exits
	    PIN_AddFiniFunction(Fini, 0);
	    PIN_AddFiniFunction(cgc_cleanup, 0);
	    
	    // Start the program, never returns
	    PIN_StartProgram();
	    
	    return 0;
	}

