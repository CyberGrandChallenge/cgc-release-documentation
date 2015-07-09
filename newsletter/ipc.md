# CGC News Letter 1.0

## Introduction

## Background

One of many challenges in building a representative platform for performing
security research is mimicking real world challenges 
while reducing the barrier to entry.

One area of research that is oft discussed is inter-process communication
(IPC).  IPC can be used for a multitude of purposes: to simplify a program,
to improve performance as well as a security mitigation.  A large barrier to
entry for analysis of IPC are the complex real world implementation intrinsics.
DECREE has distilled the IPC implementation down to transmit and receive
system calls within a brokered environment.  This distillation allow challenge
binary (CB) authors to replicate many real-word implications of IPC while
leveraging the existing communication interfaces provided by DECREE.
The simplification is further intended to allow the research community to
address the underlying IPC program analysis challenges without the complexities
of modern operating systems.

The IPC implementation provides a sandbox such that the executables that make
up the CB are able to inter-communicate in an arbitrary fashion as chosen by
the CB author. The sandbox precludes the ability to impact any other service
poll connection, proof of vulnerability connection, or other challenge
binary process running on that same host.

## Implementation

IPC is brokered within DECREE via cb-server by allocating allocating a socket
pair per executable in the set of executables within a CB.  As a starting
point, a CB made up of a single executable has three sockets provided by
cb-server:

    0, 1, and 2.

These three sockets are used for network receive, network transmit, and
debugging purposes respectively.  When a CB is made up of more than one
executable, a file descriptor pair is allocated sequentially starting at 3 and
incrementing upwards from there.

A CB made up of two executables will have one IPC socket-pair:

    (3, 4) and (5, 6).

A CB made up of three executables will have three IPC socket-pairs:

    (3, 4), (5, 6), and (7, 8)

The CB author may choose to use these socket-pairs to construct arbitrary
inter-connections between executables within the CB.  Communication is handled
via transmit, receive, and fdwait.


All of the allocated file descriptors, including the original sockets for
communicating over the network and the allocated socket pairs, are available to
all executables within the CB.  The CB author may leverage these descriptors in
any fashion within the set of executables.  

The executables that make up an instance of the CB is only able to communicate
via these descriptors to the other executables within the instance and over the
network.

Within CGC, a reformulated CB must be made up of the same number of executables
as the original CB.  Reformulated CBs may leverage the allocated file
descriptors as the CRS chooses.  The efficacy of the communication of
reformulated CBs will only be verified via the network receive and network
transmit file descriptors.

## Examples

### Pipeline

The Unix pipeline model can be simulated via iteratively leveraging the file
descriptors serially across the executables that make up the CB.  A three
process pipeline can be simulated as follows:

* CB_1 reads from 0 (network receive) and writes to 3 (CB_2).
* CB_2 reads from 4 (CB_1) and writes to 5 (CB_3).
* CB_3 reads from 6 and (CB_2) writes to 1 (network transmit).

The LUNGE_00003 CB template uses IPC in a fashion similar to the Unix
pipeline to accomplish the same tasks as the original service-template, but in
a pipelined fashion.  Input from the network is read from the first CB, passed
to the second which passes it to the third, which sends output to the network.

### Communication Broker

A brokered communication model can be simulated via a single executable
managing communication between the other executables that make up the CB.  A
producer / consumer model can be simulated with two executables as follows:

* CB_1 reads from 0 (network receive) and writes to 1 (network transmit). It also writes to 3 (CB_2) and reads from 4 (CB_2).
* CB_2 reads from 3 (CB_1) and writes to 4 (CB_1).

The LUNGE_00004 CB template 'ipc-producer-consumer' uses IPC in a fashion
similar to the producer consumer model, with all communication with the
network managed via the first executable, and all processing is managed by
the second executable.

### Dynamic Communication Channels

Communication paths are not required to be static within the context of a CB.
Dynamically built communication paths are possible with no pre-determined
order or required setup.

The example CB 'LUNGE_00005' is made up of multiple executables that each
implement a unique data transformation mechanism but can be configured to read
and write its output from the network to any of the other executables.  The
client is responsible for determining how each of the executables are plumbed
together.

## Conclusion

The examples provided here show how IPC within DECREE can provide a rich
environment for modeling complex challenges within the real world, without
drastically increasing the barrier to entry for program analysis.  

