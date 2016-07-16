# Writing an instruction tracer for DECREE Challenge Binaries using ptrace

This walk-through illustrates how *ptrace* can be used to obtain a simple instruction trace for DECREE Challenge Binaries. This walk-through is related to the *Running Intel PIN on DECREE Challenge Binaries* walk-through and also makes use of the *wrapper* capability in cb-test.

## Prerequisites

1. The latest DECREE virtual machine.
3. The source code at the end of this walk-through
4. A CB to test

## ptrace

ptrace is a ***nix system call that can be used to trace and debug processes. It is used by debuggers such as gdb, which is already supported by DECREE. The goal of this walk-through is to illustrate how it can be used to obtain an instruction trace of a DECREE CB. The basic idea behind ptrace is to allow the *tracer* process to issue different ptrace syscalls (supported ptrace operations can be found in the ptrace manpages,) to start, stop and continue execution of the *tracee* process as well as analyze and change the tracee state.

In this walk-through, we will primarily be using the PTRACE_SINGLESTEP option, which allows the tracee to execute one single instruction before returning to a STOPPED state. Once in the STOPPED state, the tracer can perform its analysis and then allow the tracee to continue execution of another instruction. This process repeats until all instructions are executed, a signal is raised, or ptracing stops.

## The instruction tracer

Since this instruction tracer is designed to be used along with the *wrapper* functionality in cb-test, it will only take one single argument - the name of the CB. Additionally, since cb-test (and cb-server) expects the wrapper process to still raise SIGINT and SIGILL to indicate a successful POV, the tracer process must identify these signals from the tracee process and then kill itself using the same signal. The execution flow of the instruction tracer is as follows:

1. The instruction tracer will receive the name of the CB to execute as the first and only argument.

2. The tracer will set a default log filename by appending ".log" to the end of the CB name.

3. The tracer will then fork itself. 

  a. The child process will be used to execute the CB while the parent process will be used to trace the CB. This is a standard tracing configuration where the parent process is the tracer and the child process is the tracee. In this design, the first thing that a child process does is to call ptrace with the *PTRACE_TRACEME* request to indicate that it is ready for tracing (i.e., it is now a tracee). Once that call is completed, the child will proceed to call *execve* to execute the desired CB.

		//Child says trace me please - the other parameters are ignored
		ptrace(PTRACE_TRACEME, 0, NULL, NULL);
		execve(child_argv[0], child_argv, NULL);

  b. The first thing the parent process does is call ptrace with the *PTRACE_ATTACH* request to attach to the waiting child process. This will setup the parent process as the tracer and the child (the one executing the CB) as the tracee. Once ptrace attach is completed, the parent process must now close the STDIN (0) and STDOUT (1) file descriptors. This is important since all file descriptors are retained after the call to fork, and cb-test expects STDIN and STDOUT to be read from and written to by the CB. Note that more file descriptors can also be used by the CB in the case of IPC challenge binaries, but cb-test (and cb-server) only expects the child to communicate through STDIN and STDOUT (STDERR can also be used).

		ptrace(PTRACE_ATTACH, childpid, NULL, NULL);
		close(0);
		close(1); 

Once STDIN and STDOUT are closed in the parent, the parent can then proceed to open the log file as well as the CB. Note that we open the files after the call to fork so that the child process will not share this particular file descriptor. 

		gMsgLog = fopen(msgFilename, "w+");

Once the CB has been opened successfully, the parent process simply single steps the child (using the *PTRACE_SINGLESTEP* request) and for each instruction (each step): read the child's register values using *PTRACE_GETREGS* to obtain the value of the *eip* register; retrive 15 bytes of memory from the tracee starting from the program counter using *PTRACE_PEEKTEXT*. The value of *eip* and the raw bytes are logged to the file.

		while (waitpid(childpid, &status, 0) == childpid)
		{
		  ...
		  ptrace(PTRACE_SINGLESTEP, childpid, NULL, NULL);
		}

There are two ways that a tracee can exit. First is a normal exit and second is an exit due to a signal. We detect the first case by checking the status from waitpid using the built-in macros.

		if (WIFEXITED(status)) ...

Then, for the second case, the signal could have been trapped by the tracer and thus not received by the tracee yet (which is what we expect since we are singlestepping) or the signal was not trapped and was sent to the tracee directly. This latter case can be determined using the *WIFSIGNALED()* and *WTERMSIG()* macros and the prior case with *WIFSTOPPED()* and *WSTOPSIG()* macros. In either case we need to check if the signal is either SIGSEGV or SIGILL and if so, kill the tracer process using the same signal so cb-test can detect it.

## Building and Running the Instruction Tracer

Building the instruction tracer is straight forward, copy the Makefile and tracer.c source code from the end of this walk-through and issue the make command.

	guest$ mkdir ptracer
	guest$ cd ptracer
	guest$ #COPY THE FILES OVER HERE
	guest$ make
	
We will reuse the same CBs and test POVs from the pin-for-decree walk-through here. The CB is YAN01_00001 and the sample generated poll (TESTINPUT.xml) is as follows.

	<?xml version="1.0" standalone="no" ?>
	<!DOCTYPE pov SYSTEM "/usr/share/cgc-replay/replay.dtd">
	<pov>
	<cbid>service</cbid>
	<replay>
	    <read><length>10</length><match><data>Player1:\x24 </data></match></read>
	    <write><data>P4IR2\x0a</data></write>
	    <read><length>10</length><match><data>Player2:\x24 </data></match></read>
	    <write><data>E\x0a</data></write>
	    <read><delim>\x0a</delim><match><data>You are stuck...\x0a</data></match></read>
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

Test this by issuing the following commands from within the YAN01_00001 parent directory.

	guest$ echo P4IR2 >> TESTINPUT
	guest$ echo E >> TESTINPUT
	guest$ echo N >> TESTINPUT
	guest$ echo S >> TESTINPUT
	guest$ /vagrant/ptracer/tracer bin/YAN01_00001 < TESTINPUT
	Player1:$ Player2:$ You are stuck...
	Player2:$ Player1:$ Player1:$ ERROR reading from user -- time to die
	guest$ tail bin/YAN01_00001.log 
        0804a5de : 81 c4 14 02 00 00 5e 5d c3 66 0f 1f 84 00 00
	0804a5e4 : 5e 5d c3 66 0f 1f 84 00 00 00 00 00 55 89 e5
	0804a5e5 : 5d c3 66 0f 1f 84 00 00 00 00 00 55 89 e5 83
	0804a5e6 : c3 66 0f 1f 84 00 00 00 00 00 55 89 e5 83 ec
	0804a8ec : 50 e8 00 00 00 00 b8 01 00 00 00 53 8b 5c 24
	0804a8ed : e8 00 00 00 00 b8 01 00 00 00 53 8b 5c 24 08
	0804a8f2 : b8 01 00 00 00 53 8b 5c 24 08 cd 80 5b c3 b8
	0804a8f7 : 53 8b 5c 24 08 cd 80 5b c3 b8 02 00 00 00 53
	0804a8f8 : 8b 5c 24 08 cd 80 5b c3 b8 02 00 00 00 53 51
	0804a8fc : cd 80 5b c3 b8 02 00 00 00 53 51 52 56 8b 5c
	
As the instruction log shows, the last thing that YAN01_00001 did is call *\_terminate* which is %cd 80*

We can achieve the same thing by using cb-test in wrapper mode.

	guest$ cb-test --directory bin --xml TESTINPUT.xml --wrapper /vagrant/ptracer/tracer --cb YAN01_00001
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
	
	guest$ tail bin/YAN01_00001.log 
	0804a5de : 81 c4 14 02 00 00 5e 5d c3 66 0f 1f 84 00 00
	0804a5e4 : 5e 5d c3 66 0f 1f 84 00 00 00 00 00 55 89 e5
	0804a5e5 : 5d c3 66 0f 1f 84 00 00 00 00 00 55 89 e5 83
	0804a5e6 : c3 66 0f 1f 84 00 00 00 00 00 55 89 e5 83 ec
	0804a8ec : 50 e8 00 00 00 00 b8 01 00 00 00 53 8b 5c 24
	0804a8ed : e8 00 00 00 00 b8 01 00 00 00 53 8b 5c 24 08
	0804a8f2 : b8 01 00 00 00 53 8b 5c 24 08 cd 80 5b c3 b8
	0804a8f7 : 53 8b 5c 24 08 cd 80 5b c3 b8 02 00 00 00 53
	0804a8f8 : 8b 5c 24 08 cd 80 5b c3 b8 02 00 00 00 53 51
	0804a8fc : cd 80 5b c3 b8 02 00 00 00 53 51 52 56 8b 5c

We can execute YAN01_00001 using a POV and we see a SIGSEGV as expected.

	guest$ cb-test --directory bin --xml pov/sample_shipgame_pov.xml --wrapper /vagrant/ptracer/tracer --cb YAN01_00001 
	# sample_shipgame - pov/sample_shipgame_pov.xml
	ok 1 - slept 0.025000
	ok 2 - write: sent 532 bytes
	ok 3 - slept 0.025000
	# passed: 3
	# failed: 0
	# total passed: 3
	# total failed: 0
	# core identified
	# process cored.  (signal 11: SIGSEGV)
	guest$ tail bin/YAN01_00001.log
	080481c9 : 3d 45 00 00 00 0f 85 0b 00 00 00 8b 45 f8 c6
	080481ce : 0f 85 0b 00 00 00 8b 45 f8 c6 00 45 e9 56 00
	080481df : 0f be 85 f4 fd ff ff 3d 48 00 00 00 0f 85 0b
	080481e6 : 3d 48 00 00 00 0f 85 0b 00 00 00 8b 45 f8 c6
	080481eb : 0f 85 0b 00 00 00 8b 45 f8 c6 00 48 e9 34 00
	080481fc : 0f be 85 f4 fd ff ff 3d 53 00 00 00 0f 85 0b
	08048203 : 3d 53 00 00 00 0f 85 0b 00 00 00 8b 45 f8 c6
	08048208 : 0f 85 0b 00 00 00 8b 45 f8 c6 00 53 e9 12 00
	08048219 : 8b 45 f8 c6 00 55 c7 45 fc ff ff ff ff e9 25
	0804821c : c6 00 55 c7 45 fc ff ff ff ff e9 25 00 00 00

We can also execute the EAGLE_00004 IPC cb using cb-test in wrapper mode.

	guest$ cb-test --debug --directory bin --xml poller/for-release/poller-1.xml --wrapper /vagrant/ptracer/tracer --cb EAGLE_00004_1 EAGLE_00004_2 EAGLE_00004_3
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
	
## Source for Makefile

	CC=gcc
	
	OBJS=tracer.o
	
	%.o: %.c 
		$(CC) -g -c $^ -o $@ $(CFLAGS)
	
	tracer: $(OBJS)
		$(CC) -g $^ -o $@ $(CFLAGS)
	
	clean:
		rm -f *.o tracer

## Source for tracer.c

	/** CGC Instruction Tracer Example 
	 *  @author Lok Yan
	 *  @date 20 Jan 2015
	**/
	
	#include <sys/ptrace.h>
	#include <unistd.h>
	#include <stdio.h>
	#include <stdlib.h>
	#include <string.h>
	#include <sys/user.h>
	#include <errno.h>
	#include <signal.h>
	
	typedef unsigned char byte;
	
	FILE* gMsgLog = NULL;
	pid_t gChildPid = -1;
	int gbAttached = 0;
	
	void cleanup()
	{
	  if (gMsgLog != NULL)
	  {
	    fflush(gMsgLog);
	    fclose(gMsgLog);
	    gMsgLog = NULL;
	  }
	}
	
	/**
	 *  A signal handler for flushing the contents and closing out
	 *  the log file.
	 *  NOTE: This is a signal handler for signals that are targetted
	 *    at the tracing (parent) process
	**/
	void signal_handler(int sig)
	{
	
	  //SIGALARM is raised when the time for execution is up (set by cb-server)
	  //SIGINT is if the user decides to interrupt this process
	  //So if the signal is not either of those, then just continue
	  if (sig != SIGALRM && sig != SIGINT)
	  {
	    return;
	  }
	
	  if (gbAttached && (gChildPid > 0))
	  {
	    //kill the child and then cleanup
	    ptrace(PTRACE_DETACH, gChildPid, NULL, NULL);
	    kill(gChildPid, SIGKILL);
	    gChildPid = -1;
	    gbAttached = 0;
	  }
	  cleanup();
	  exit(0);  
	}
	
	void handle_child_signals(int sig)
	{
	  //cb-server uses the following signals to detect
	  // a POV and therefore we must replicate them here
	  // by killing ourself (the wrapper tracer process)
	  // with the same signal
	
	  //SIGSEGV - if the child has segfaulted
	  //SIGILL - trying to execute an illegal instruction
	  if ( (sig == SIGSEGV) || (sig == SIGILL) )
	  {
	    //NOTE: If the child has stopped due to signal
	    // the signal hasn't actually been delivered to the 
	    // child yet. The handle_child_signal function should
	    // still pass the signal through to the child 
	    if (gbAttached && (gChildPid > 0))
	    {
	      ptrace(PTRACE_DETACH, gChildPid, NULL, NULL);
	      kill(gChildPid, sig);
	      gChildPid = -1;
	      gbAttached = 0;
	    }
	    cleanup();
	
	    kill(getpid(), sig);
	    exit(0);
	  }
	}
	
	/** Function to read the next 15 bytes of memory given an address
	 *  There is definitely a problem with over-reading since most
	 *  instructions are not that big.
	**/
	int getInsn(byte* insn, long pc, pid_t pid, int max)
	{
	  int i = 0; 
	  int j = 0;
	  long* insn_l = (long*)insn;
	  for (i = 0, j = 0; i < max; i+=sizeof(long), j++)
	  {
	    errno = 0;
	    insn_l[j] = ptrace(PTRACE_PEEKTEXT, pid, pc + i, NULL);
	    if ( (insn_l[j] == -1) && (errno))
	    {
	      return (-1);
	    }
	  }
	  return (0);
	}
	
	int main(int argc, char** argv)
	{
	  pid_t childpid;
	  int status;
	  struct user_regs_struct regs;
	  char* child_argv[2] = {NULL, NULL};
	  
	  byte insn[16];
	
	  struct sigaction sa;
	  sa.sa_handler = &signal_handler;
	  sigemptyset(&sa.sa_mask);
	  sa.sa_flags = 0;
	
	  char* msgFilename = NULL;
	
	  int i = 0;
	  for (i = 1; i < argc; i++)
	  {
	    if (strcmp(argv[i], "-o") == 0)
	    {
	      i++;
	      if (i < argc)
	      {
	        msgFilename =argv[i];  
	      }
	      else
	      {
	        fprintf(stderr, "Error: Filename expected after -o\n");
	        return (-1); 
	      }
	    }
	    else if (strcmp(argv[i], "-cb") == 0)
	    {
	      i++;
	      if (i < argc)
	      {
	        child_argv[0] =argv[i];  
	      }
	      else
	      {
	        fprintf(stderr, "Error: Filename expected after -cb\n");
	        return (-1); 
	      }
	    }
	    else
	    {
	      child_argv[0] = argv[i];
	      break;
	    }
	  }
	
	  if (child_argv[0] == NULL)
	  {
	    fprintf(stderr, "Error: a CB must be defined\n");
	    return (-1);
	  }
	
	  //set the default filenames if needed
	  if (msgFilename == NULL)
	  {
	    int childNameLen = strlen(child_argv[0]);
	    msgFilename = (char*)(malloc(childNameLen + 5));
	    if (msgFilename == NULL)
	    {
	      fprintf(stderr, "Error: Could not allocate space for a filename\n");
	      return (-1);
	    }
	    strcpy(msgFilename, child_argv[0]);
	    strcpy(msgFilename + childNameLen, ".log");
	  }  
	
	  childpid = fork();
	 
	  if (childpid == -1) //if error
	  {
	    fprintf(stderr, "Unable to fork\n");
	    return (-1);
	  }
	
	  if (childpid == 0)
	  {
	    //Child says trace me please - the other parameters are ignored
	    ptrace(PTRACE_TRACEME, 0, NULL, NULL);
	    execve(child_argv[0], child_argv, NULL);
	  }
	  else
	  {
	    //attach to the child to stop its execution
	    ptrace(PTRACE_ATTACH, childpid, NULL, NULL);
	    gbAttached = 1;
	    gChildPid = childpid;
	
	    //register the signal handler
	    if (sigaction(SIGINT, &sa, NULL) != 0)
	    {
	      fprintf(stderr, "Warning: Could not register the signal handler\n");
	    }
	    if (sigaction(SIGALRM, &sa, NULL) != 0)
	    {
	      fprintf(stderr, "Warning: Could not register the signal handler\n");
	    }
	
	    //close the stdin and stdout fds
	    close(0);
	    close(1);    
	
	    //open up the log files
	    gMsgLog = fopen(msgFilename, "w+");
	    if (gMsgLog == NULL)
	    {
	      fprintf(stderr, "Error: Could not open %s for writing\n", msgFilename);
	      goto detatch;
	    }
	
	    // Now that everything is setup, we can singlestep the child
	    //1. Wait for the child to be ready
	    while (waitpid(childpid, &status, 0) == childpid)
	    {
	      //if the child has exited then cleanup
	      if (WIFEXITED(status))
	      {
	        cleanup();
	        return (0);
	      }
	     
	      //if the child exited due to a signal - we handle
	      // the signal just incase we need to kill ourself
	      if (WIFSIGNALED(status))
	      {
	        //if the child terminated with a signal - then we should replicate the signal here
	        handle_child_signals(WTERMSIG(status));
	        return (0);
	      }
	
	      //if the child is not stopped then wait until the child
	      // is stopped
	      if (!WIFSTOPPED(status))
	      {
	        continue;
	      }
	
	      //The child could have stopped due to a signal
	      // so handle that possibility
	      handle_child_signals(WSTOPSIG(status));
	      
	      //get the CPU state
	      ptrace(PTRACE_GETREGS, childpid, NULL, &regs);
	
	      //get a number of bytes (15)
	      getInsn(insn, regs.eip, childpid, 15);
	      //we ignore the read errors from ptrace_PEEK at this time
	
	      //print the instruction and the raw bytes
	      fprintf(gMsgLog, "%08x : %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x\n", regs.eip
	                     , insn[0]
	                     , insn[1]
	                     , insn[2]
	                     , insn[3]
	                     , insn[4]
	                     , insn[5]
	                     , insn[6]
	                     , insn[7]
	                     , insn[8]
	                     , insn[9]
	                     , insn[10]
	                     , insn[11]
	                     , insn[12]
	                     , insn[13]
	                     , insn[14]);
	
	      //singlestep the child
	      ptrace(PTRACE_SINGLESTEP, childpid, NULL, NULL);
	    }
	
	    detatch:
	    ptrace(PTRACE_DETACH, childpid, NULL, NULL);
	    cleanup();
	  }
	
	  return (0);
	}
	
