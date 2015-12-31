# Proof of Vulnerability (POV) in CFE

The DARPA CGC FAQ (see https://cgc.darpa.mil/documents.aspx) in question 29, details 
POV methods for CFE. Two methods for demonstrating a POV are detailed, "Method 1", and
"Method 2" hereafter referred to as Type 1 and Type 2 POVs respectively.

A Type 1 POV requires execution of the remote CB/RB to fault at an instruction pointer
location negotiated with the CFE Competition Framework with the requirement that
one additional general purpose register also contains a second value negotiated with
the CFE Competition Framework. This negotiation process is described below.

A Type 2 POV is required to read a specific number of bytes dictated by the Competition
Framework from anywhere within a memory range specified by the Competition Framework.
The bytes retrieved by the POV are then submitted to the Competition Framework for
verification against the known expected values. Type 2 negotiation is described below.

## Type 1 POV Negotiation

### Type 1 Negotiation in CGC Binary Style POVs

File descriptor 3 shall be used to carry out POV type negotiations. A Type 1 POV
shall demonstrate control over a remote CB/RB's instruction pointer and one
additional general purpose register to a degree of precision negotiated
with the competition framework. A successful Type 1 POV must result in the
target binary faulting at the negotiated instruction pointer address with
one additional general purpose register containing the second negotiated value.

A Type 1 negotiation is initiated by the POV by first transmitting, on file descriptor 3,
the 32-bit, little endian value: 1, then transmitting 3, 32-bit, little-endian
integers. The first of these three integers is known as the "ipmask" and is used
to specify a mask of 32 bits that the POV asserts it can control in the
CB/RB's instruction pointer. In order to be considered valid, at least 20 bits in the
mask must be set to 1. An invalid  mask will result in a failed POV attempt. A valid
mask will cause the competition infrastructure to return 20 (or more as specified by
the provided mask) bits that must appear verbatim in the instruction pointer at the
moment the remote binary terminates in a faulting state. This negotiated value may be
obtained by the POV by receiving the first available 32-bit, little endian integer
value from file descriptor 3. 

The second, 32-bit, little endian integer transmitted by the POV during a Type 1 negotiation
is known as the "regmask" and is used to specify a mask of at least 20 bits that the
POV asserts it can control in one of the remote CB/RB's general purpose registers.
An invalid mask will result in a failed POV attempt. A valid mask will cause the competition
infrastructure to return 20 (or more as specif ed by the provided mask) bits that must appear
verbatim in the general purpose register specified during the Type 1 negotiation at the time the
challenge/replacement binary faults at the negotiated instruction pointer location. 
This negotiated value may be obtained by the POV by receiving the second available
32-bit, little endian integer value from file descriptor 3.

The third, 32-bit, little endian integer transmitted by the POV during a Type 1 negotiation is known as the
"regnum" and is used to specify the general purpose register that will contain the negotiated
register value at the time of the CB/RB fault. The following register mapping shall be used
to select one of eight general purpose registers:

   0 - eax
   1 - ecx
   2 - edx
   3 - ebx
   4 - esp
   5 - ebp
   6 - esi
   7 - edi
   
It is the responsibility of the POV to incorporate the negotiated eip and general purpose values
into the content that is exchanged with the remote CB/RB in order to cause the remote CB/RB to fault
in the state negotiated with the competition framework.

### Type 1 Negotiation in XML Style POVs

All POVs used during CFE shall be in the form of CGC binaries, however to assist with the 
transition from CQE to CFE, an XML specification for CFE POVs has been created by extending
the CQE POV XML dtd to allow for POV type negotiations. All XML style POVs shall be converted
to C source code utilizing the pov-xml2c utility after which they shall be compiled to
CGC binaries representing the final executable form of the POV. The libpov library exists
for the sole purpose of supporting this conversion process.

The specific XML elements responsible for Type 1 POV negotiation are the <negotiate>, <type1>,
<ipmask>, <regmask>, and <regnum> elements. These elements specify the required components of
a Type 1 POV negotiation as detailed above. An example of such a negotiation follows:

   <negotiate>
      <type1>
         <!-- base 10 or base 16 integer. Base 16 integers must be prefixed with "0x" -->
         <ipmask>0xBABABABA</ipmask>
         <!-- base 10 or base 16 integer. Base 16 integers must be prefixed with "0x" -->
         <regmask>0xD5D5D5D5</regmask>
         <!-- 0..7 [eax,ecx,edx,ebx,esp,ebp,esi,edi] -->
         <regnum>7</regnum>
      </type1>
   </negotiate>

Within the remaining replay elements, the negotiated instruction pointer value may be referred
using the variable TYPE1_IP, and the negotiated general purpose register value may be referred
to using the variable TYPE1_REG.
      
## Type 2 POV Negotiation

### Type 2 Negotiation in CGC Binary Style POVs

File descriptor 3 shall be used to carry out POV type negotiations.  A Type 2 POV shall
demonstrate the ability to read the contents of arbitrary memory locations within the
challenge/replacement binary as dictated by a negotiation with the competition framework.

For each attempt at a Type 2 POV, the competition infrastructure shall create a private
region within the remote CB/RB that is the subject of the POV. The competition
infrastructure shall populate this region with random, secret flag data.

A Type 2 negotiation is initiated by the POV by transmitting, on file descriptor 3,
the 32-bit little endian value: 2.  The competition framework shall respond with 3, 32-bit,
little-endian integers specifying details about the private memory region and the amount of
information to be obtained by the POV.

The first of these three integers is known as the "type2_addr" value and specifies the base
address of the private memory region. The second integer transmitted to the POV is 
known as the "type2_size" value and specifies the size of the the private memory 
region. The private memory region shall span a contiguous block within the CB/RB
memory space as defined by the address range type2_addr (inclusive) to 
(type2_addr + type2_size) (exclusive). The third integer transmitted to the POV is 
known as the "type2_length" value and represents the number of contiguous bytes
that the POV must obtain from any location within the private memory region.

A Type 2 POV demonstrates its success by transmitting the "type2_length" bytes
it has obtained from the CB/RB binary to the competition framework
on file descriptor 3. The competition framework will then judge the correctness of the 
submission and score the POV accordingly.

### Type 2 Negotiation in XML Style POVs

All POVs used during CFE shall be in the form of CGC binaries, however to assist with the 
transition from CQE to CFE, an XML specification for CFE POVs has been created by extending
the CQE POV XML dtd to allow for POV type negotiations. All XML style POVs shall be converted
to C source code utilizing the pov-xml2c utility after which they shall be compiled to
CGC binaries representing the final executable form of the POV. The libpov library exists
for the sole purpose of supporting this conversion process.

The specific XML elements responsible for Type 2 POV negotiation are the <negotiate>, <type2>,
and <submit> elements. These elements specify the required components of
a Type 2 POV negotiation as detailed above. An example of such a negotiation follows:

   <negotiate>
      <!-- The POV need only express its intent to perform a Type 2 -->
      <type2 />
   </negotiate>
   
   <!-- Other replay elements carry out the communication Whit the CB/RB -->
   
   <!-- Finally the retrieved secret flag bytes are submitted -->
   
   <submit>
      <!-- The submit element is optional, if it is omitted the value of
           the variable TYPE2_VALUE shall be submitted to the competition 
           framework prior to terminating the POV -->
      <var>MY_TYPE2_DATA</var>
   </submit>

Following the negotiate element, the negotiated type2_addr, type2_size, and type2_length values
may be referred using the variables TYPE2_ADDR, TYPE2_SIZE, and TYPE2_LENGTH respectively.

The POV should assign the required secret flag data into the variable TYPE2_VALUE (or any other
variable that is then referenced in a <submit> element.

## SEE ALSO

For information regarding submitting a CB, see submitting-a-cb.md <br>
For information regarding testing a CB, see testing-a-cb.md <br>
For information regarding debugging a CB, see debugging-a-cb.md <br>
For information regarding building a CB, see building-a-cb.md <br>
For information regarding XML markup for CFE POVs, see cfe-pov-markup-spec.txt <br>

