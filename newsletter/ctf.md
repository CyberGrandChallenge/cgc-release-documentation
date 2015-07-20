# CGC News Letter 3
## Introduction

When considered in the context of computer security, Capture the Flag (CTF)
involves taking control of and or defending digital "flags" in some way.
Many parallels can be drawn with the well-known physical game of CTF played 
by teams of people where each team typically defends one flag while also 
attempting to capture the flag of another team. 

Computer and network security oriented CTFs have grown quite popular in 
the past few years.  Some teams are now well-known and compete in many
events throughout the year.  In some cases a CTF might award considerable
prizes to top-placing teams, and in other cases teams compete solely for
prestige or educational experience.  In fact, similar to sporting events,
larger CTFs will hold preceding qualification rounds in order to 
determine eligibility for the later CTF.  In some cases, brackets are
formed or winners of peer events are automatically deemed eligible based
on prior performance.

Given that such CTF events are now a regular occurrence and team 
knowledge persists between events, a newcomer to the field may be at a 
significant disadvantage.  The disadvantage is not necessarily related to 
the technical prowess fielded by the team, but in a lack of historical 
knowledge regarding gameplay and even culture surrounding security-oriented
CTFs.  The intention of this article is to lessen this disadvantage by
relating historical gameplay knowledge that may well be taken for granted
by seasoned CTF participants.


## Background

Many CTF events, sometimes called exercises, recur annually and some enjoy
a longevity of more than a decade.  For example, the CTF associated with 
the annual hacker conference DEFCON has existed in some form since 1996, 
becoming more formally organized in 1999.  An event organized by the 
University of California - Santa Barbara has been held annually since 2003.
An event may impose certain restrictions based on desired learning
objectives, political pressure, availability of prizes to award or any
number of such influences.  Some events limit team size, or limit the
composition to only academic affiliates, professionals, or a certain 
level of education.  As such, the organization and composition of each 
event also vary widely with some events lasting only a few hours while
others last months.  Some stress defense, others focus on offense.
Some strive to represent "real world" security issues that may be 
encountered by programmers or security practitioners.  Some strive to 
test esoteric or depths of knowledge encountered by few.  In any case,
the quintessential property of a computer security CTF is that a 
participant will circumvent a security property in some way, and receives
some form of credit for doing so.

### Digital Flags

Flags, often called "keys," in these events typically consist of a 
relatively small set of sequential bytes.  A flag might be a short string 
of recognizable words, a set of random printable characters, a 
cryptographic hash, or indeed it may be nearly anything representable
by computer memory.  Flags are often on the order of dozens of bytes
in length. Flags are frequently stored in files and secured using
various access control facilities provided by the host operating
system.

Once a security property is circumvented, a player often must retrieve
or provide a flag in order to demonstrate the circumvention.  A CTF 
event may even differentiate between types of flags.  In an attack 
that results in increased information disclosure, an attacker may
gain the ability to read otherwise restricted memory.  In this case a 
flag has been "stolen."  These flags might be known as "read flags."
In a complementary way, a "write flag" or "overwrite flag"  may be 
used to demonstrate an ability to alter otherwise restricted memory.

The primary objective is to circumvent a security property, so following
a successful attack, locating the flag is often not difficult.  A
participant may even know the location far in advance of the attack, but 
not be able to access the flag data until mounting a successful
attack.  For example, a flag might simply exist as a file named "key" or
"flag" in a unix account home directory.  This name and location path of this
file might be easily enumerable by another other account, but due to file
permissions, the contents of the file might not be readily observed.  
Similar easy-to-locate yet difficult-to-leverage parallels exist for flag
content stored in other ways (e.g. database, in Random Access Memory, 
etc.).

### Game Type

Most CTFs can be categorized into two styles of game play: attack-defend
and board-style.  

Attack-defend involves actually attacking flags held by another team in 
some way, and mitigating attacks mounted by other teams.  In this type of
event, teams are often connected via a network and the network locations
of each team are known or readily discoverable.  Attack-defend events are
often held "on-site" on an isolated network with all participants physically 
present.  Often such events are co-located with a conference.  In some 
cases, attack-defend events are held in a geographically disparate way.  
However, even geographically distributed events tend to adopt an isolated
networking model using VPNs and restricted routing.  Teams operate and 
defend several discrete, vulnerable services on live computer systems.  
A service is a network accessible piece of software that often implements 
a communication protocol developed
specifically for the CTF and which contains intentionally injected
vulnerabilities intended to be discovered and exploited by participating teams.
Real world examples of services include web, email, telnet, and ftp servers.
Defenses may involve installing network security devices, configuring software
controls on the machine hosting a service, locating and patching a
vulnerability in a service, and so on.

The other popular style of play is board-style, often called a "Jeopardy 
Board" style game - regardless of the visual similarity to the popular
television game show.  Think of each square of a two-dimensional grid
representing a single discrete problem that has an associated credit 
awarded for completion.  Instead of services, these discrete problems 
are typically referred to as challenges or puzzles.  In the same way, 
flags might be referred to as solutions or answers.  Teams strive to 
complete more of the board than any other team.  In this style of play, 
teams often have no defensive responsibility at all.   A challenge might
be exactly the same as an attack-defend service, however the service is
hosted by the organizer and not other participants.  Board-style events
also lend to challenges that do not fit network-based or attack-defend
paradigms.  For example, challenges based on Digital Forensics might
adopt a form factor more as a complex file system rather than the 
single executable form factor adopted for attack-defend services. 
Similarly, such a Digital Forensics oriented challenge would not be 
interactive in any way, obviating several participant strategies and 
scoring mechanism described later.

Both types of events typically have one or more time components, the most
obvious of which is the duration of the event.  That is, when the event 
begins, teams often all share the same score, and at the end of the event,
the team with the best score is declared the victor.

There are, of course, many variations on these two types of play.  For 
instance, a "Defense only" event might be held, such as those organized
for the U.S. Service Academies or the Collegiate Cyber Defense Competition.
These are effectively attack-defend events, only the event organizer 
assumes all the attack components and forbids participants to attack via
event rules.

Modifications also exist to the board-style event, typically involving
some ostensibly clever modification to the board itself.  For example, a
CTF might force completion of puzzles in a certain progression, have 
all participants vote on the "next" puzzle, or have the puzzle selected 
by the most recent participant to provide a correct answer to the 
current question .  In the end, 
most events still reduce to the common thread of having sets of 
problems, and the team that possesses the most, or more valuable, 
solutions to these problems is in the favorable position.

### Service Availability

Particular to attack-defend events, Service Level Availability (SLA) 
refers to the notion that each team should actually present opportunities 
for other teams to attack.  Factoring SLA into a scoring algorithm is 
beneficial for gameplay and to encourage defensive tactics. The intent
of SLA is to prevent participants from creating a perfect defense by 
simply shutting down their services to eliminate any attack surface.
If every team did this however, there would be no game to play. Akin to 
the real-world task of securing Internet-facing services, such a service
is relatively safe when it is unavailable, but it provides little utility.

Measuring the "availability" of a service is an interesting proposition.
In the instance of a TCP-based service, the SLA measurement system should
not simply check for a successful connect on the service TCP port.  In 
this case, a perfect defense for a participant would be to disable the 
service entirely and then write software to accept connections on the 
same port, yet not actually do anything else with the TCP connection.
In this way, the SLA measurement system would always measure the service
as available.  Instead, measurements must actually interact with a 
service.

Unfortunately, interactions with services tend to vary widely, so 
measuring SLA becomes somewhat complex. 
Further, each service has known vulnerabilities, which
a participant is permitted to patch or otherwise mitigate, thereby 
changing at least some of the possible interactivity with the service 
(ideally, permitting all relevant interactions, but precisely 
disallowing interactions that lead to a vulnerability).  Therefore, the 
SLA measurement system must interact with each service in a manner 
specific to that service.  Furthermore, these interactions must 
exercise all relevant functionality that a service implements.  These 
interactions are sometimes called "polls" and likewise, the action of 
measuring SLA over time is called "polling."  Polls are typically 
measured one or more times per scoring round. In most cases polls do
not exercise the vulnerabilities planted within the services as observation
of such interactions would aid teams in locating the vulnerabilities.

### Scoring

A service in an attack-defend
event is typically scored over time.  That is, in contrast to a board-
style event, a flag can be defended and stolen and/or overwritten more 
than once.  The most common way to implement this is via the notion of
scoring rounds.  A scoring round is the duration of time in which a 
scoring event might occur.  For instance, if a scoring round is 
arbitrarily set to 5 minutes by the organizers, then a team that 
steals a flag from another team multiple times in a given 5 minute
window will only receive credit for one stolen flag within this
particular window of time. However, the next 5-minute interval
represents a new round, in which the team may again receive credit as
long as they are again able to mount a successful attack.  Logistically,
the organizers somehow change or "rotate" all the flags in the environment,
such that the same flag location will contain new data to be stolen in each
round. The requirement to steal new flags in each new round forces teams to
demonstrate persistent access into their adversary's services.

The actual scoring algorithms vary with each CTF, but in addition to 
offensive and defensive components, they typically include an 
aformentioned availability component, sometimes called Service Level 
Availability (SLA).  SLA is meant to ensure that teams are providing
services to the event, as opposed to disabling services entirely.

For each round, a team 
may achieve a perfect defensive score be ensuring none of their 
flags are stolen or overwritten.  Similarly, a perfect 
offensive score might be achieved by stealing flags for all services
from all other teams.   A perfect SLA would be achieved by having 
all of team's services available and responding correctly as measured
by some number of service polls.  CTFs might employ scoring algorithms
that favor one aspect or another and might introduce dependancies.  For
example, a CTF might not award any offense point unless a certain 
threshold of SLA is maintianed.

Pre-determined bonus values might also be awarded in an attack-defend
event, colloquially known as "breakthroughs."  These breakthroughs are
used to artificially boost a team's score as a reward for being the first
to demonstrate circumvention of a security property on a service.
Details vary by implementation, but scoring in attack-defend events 
is typically handled out-of-band using a dedicated interface for teams 
to present stolen flags.

In a board-style event, the value of solving a particular problem is 
typically entirely pre-determined by the organizers.  Often, a flag is 
procured by the team after solving a problem and the flag is presented to 
the organizers by the team as proof that a problem has been solved.  This
presentation, like attack-defend styles, is typically performed in a way 
that is out-of-band from the problem.

## Implementation

Some implementation-specific concepts have already been mentioned, such
as the notion of a 5-minute scoring round.  However, implementing a CTF
is a complex endeavor and as such numerous implementation details can 
be varied to distinguish one CTF from another.  In addition to defining
the nature or spirit of the CTF, implementation details might also vary
simply to encourage particular learning objectives or discourage particular
participant strategies.

Consider the participant's interfaces to the CTF infrastructure.  Fundamentally
all a participant requires is the ability to interact with other teams' services.  
However, it is very common to also provide a technological mechanism for 
presenting stolen flags as proof that a security property was violated and some
form of scoreboard to denote progress through the event and/or relative ranking
among other competitors.  The notion of a scoreboard is interesting in relation
to participant strategy.  If the scoreboard interface is tailored to each team, 
then colluding teams may maintain an advantage.  If the scoreboard presents not
only ordering of participants, but also scaled performance such that one team knows
by how much it is losing, the team might be able to calculate a likelihood of making 
up the difference in the remaining time.  If this likelihood is low, the losing
participant may well prematurely exit competition.  Such is also likely to occur
if a scoreboard is available to non-participants, so that outsiders can observe
the state of the CTF.

The notion of outsider, or spectator, involvement is often at odds with goals of
the CTF organizer.  In addition to the mentioned complexities relating
to a public scoreboard, consider other obvious candidates for spectator involvement.
Real-time indications of attack outcome effectively acts as an Intrusion Detection
System (IDS) for participants, prompting defenders to focus on related aspects of the
CTF.  Even seemingly innocuous visualizations intended to inform spectators may 
divulge information to participants.  When such visualizations are intended for
spectators, but used by participants, some consideration to fairness must be 
made by the organizers.  For instance, ensuring that all teams have an equal
ability to actually see the visualization.

Numerous other implementation decisions that may be made to govern the structure
of a CTF.  In attack-defend scenarios, the participant may be able to physically 
disconnect the server they are defending.  In this case, "in-line" defenses, such
as a Network IDS appliance might be employed to protect the server.  In other cases
a participant might instead connect to a physically remote server, eliminating the
possibility of using an "in-line" appliance.  In the same vein, decisions must be
made about "in-network" vs "out-of-network" key rotation.  That is, will key 
rotation performed by the organizers occur though the CTF network, or will keys
be rotated independent of the network; via a virtualization hypervisor, for
instance.  Some of these decisions are behind-the-scenes and participants may never
know the decision made or the reasoning behind it; other decisions have profound
impact on the particpant's interaction with the CTF.  In the end, each CTF event
is uniquely defined in this manner.

## Participant Strategies

Teams might develop broad strategies over time through the course of 
participating in several events.  Other strategies might be conceived
during an event or otherwise be event-specific.  To develop effective
event-specific strategies, a team must fully understand the scoring
algorithm.  For example, some scoring systems facilitate building 
insurmountable leads, while other systems encourage diversity in scoring
or facilitate inspiring come-from-behind scoring drives.  Strategies
offered in this section typically only apply to attack-defend CTFs.

Consider a commodity-based scoring system.  In such a system, a flag
scored by a team on a often-scored-upon service is worth very little, 
where a flag scored by a team on a rarely-scored-upon service is 
valued much higher.  This is the same principle, rarity, that makes
diamonds more valuable than rocks.  By scoring in this way, the service difficulty 
is determined by the participants themselves.  Easier services are
generally scored on more often, by more participants.  More difficult
services are scored on rarely by relatively few participants.  A
participant in a commodity-based scoring CTF must consider different
strategies of play.  For instance, if a participant believes that the 
likelihood of another participant scoring on a service under their own
accord is low, then the participant might wait until the final minutes
of the CTF to score a single, very valuable, flag from a service. 
Similarly, a participant might focus efforts on attacking one or two 
weak teams, because the weak team might not be able to learn anything 
from the attacks making the attack a low-risk proposition.  Or a team
might delay attacking a particular service in order to develop a more
stealthy attack, making the attack more difficult to observe or 
repurpose.

While the effects may be more pronounced under commodity-based 
scoring, attacking weaker participants or enhancing attacks to be
more stealthy, resistant to reverse engineering, or otherwise more
difficult to repurpose are all commonly employed strategies.

In attack-defend CTFs, participants are often connected to one 
another via standard networking, TCP/IP and Ethernet for instance.  
The shared resource of the network is typically managed by the CTF 
organizer.  From a participant's perspective, the network is the
only interface from which benign interactions with a service will 
occur (either from another participant or from the organizer as a
component of scoring).  If a participant is able to distinguish 
between scoring and participant-originated traffic, then action 
can be taken to ensure scoring traffic is untouched while 
participant traffic is abandoned or modified - thus creating a
perfect defense for the CTF.  Similar "fingerprinting" might be
done to detect traffic from individual competitors (e.g. those using
a different operating system than others, emitting TCP/IP stack 
artifacts unique to the CTF).

The network can also be used to identify attacks in order to inform
defensive tactics or to repurpose attacks.  Network traffic might be
correlated to a particular service (e.g. TCP port) and subsequently
some artifact of a successful attack (e.g. bash shell).  In any case,
if a portion of network traffic is identified as an attack, then 
the "victim" participant in this case, may focus effort on adapting
the captured traffic in order to attack a different participant.  The
cleanest example would be an attack where simply changing the source
and destination IPs would launch an attack to a new participant.  
While this strategy can be very effective, this is often, but not
always, a "keeping up" strategy.  That is, if this is a participant's
primary strategy, then that participant will never be the first to 
score points on any service.  However, if a team launches an attack
against a service that the same team has not yet patched, then they 
remain vulnerable to their own attack.   If a team that is good at 
repurposing is also better at automating attacks against all teams,
then they may quickly surpass the original author by effectively 
making better use of the attack.  In multi-team attack-defend CTFs, 
scoring scenarios can occur where many teams each have the highest
score component for one particular service, but one team that has
the second-highest score component for all services maintains a higher
overall score.  For reasons like these, much consideration should be
given to when and how attacks are mounted against which opponents.

Some strategies involve broad defenses meant to work in many environments.
Unsurprisingly, these often resemble real-world defenses used generically.  
Network firewalls, IDSs, proxies, etc fall in this category.  Of course,
these defenses to not work in all CTFs.  As in an implementation design 
discussed above, if the CTF does not allow a competitor to place devices 
between the vulnerable server and the CTF network, then participants 
simply are not able to deploy an in-line network firewalls or IDS.

Since service availability is often determined by the organizer polling
each service, participants can observe the polling and attempt to 
deceive the availability measurement.  For example, rewriting a service
from one programming language to another that has inherent security 
benefits.  From a network perspective, the newly written service can 
listen on the same TCP port, and indeed mimic the behavior of the 
original service - only without a software vulnerability introduced 
by the former language.  Depending on CTF organizer choices, such "service
replacement" might be encouraged or discouraged.  If the polls do not
emphasize most of the service functionality, then the replacement 
might only have to implement a subset of the original features
in order to gain all the SLA points from polling.

Progressing with the same idea of service replacemet is replacement of the 
entire defended host.  Especially when the participant's defended host is already
a Virtual Machine, creating a second, faux, target might yield considerable
defensive points.  Other participants might actively attack and steal 
keys on the secondary host.  Since, the organizer is not rotating keys
on this second host, keys presented for credit will never be valid.
If this is technically permitted, this is prime example of a strategy 
designed for a participant to benefit by undermining the CTF infrastructure.
That is, as opposed to binary patching, service replacement, or other 
defenses, this strategy is chiefly only useful for the specific CTF.  
Other methods of undermining infrastructure vary by CTF implementation
but might include the ability to present keys rotated to a participant's
own server for credit (scoring against self) or the ability to circumvent
security controls on CTF infrastructure systems.

Since much of the scoring occurs out-of-band in both styles of events,
the point in time that a challenge is completed or service is 
exploited is decoupled from the point in time that the flag is 
submitted for credit.  This leads to game play strategy where flags
are not immediately submitted causing a temporary artificially low 
score to appear for one's own team, giving the impression of weakness.  
There is obvious risk with such a strategy as other 
teams may reach a higher score first.  In an extreme case, a team can 
hoard keys turning them all in at the very end of the event.  Some
organizers combat hoarding by having keys expire, that is, a key can
only be redeemed for credit for N rounds after it is first made available
by the organizers. In some cases organizers are able to observe successful
access to flags in real-time eliminating both the need to submit stolen
flags out of band and eliminating the ability to hoard stolen flags for
later submission.



## Conclusion

Already, there are websites and groups of individuals devoted to tracking
and reasoning about inter-CTF relationships.  Team and individual
performance is tracked between events and ranked year-on-year.  CTFs are
no longer rare occurrences, and in some cases prizes awarded to winners 
are significant.  We have presented an overview of the two most common types
of CTFs along with relevant discussion regarding CTF implementation choices,
scoring, service level agreement, and strategy.  Our hope is that, by 
describing CTFs in this way, that newcomers are at less of a disadvantage
to seasoned participants. Implementation choices for infrastructure and 
scoring, along with the services or puzzles themselves are all created to 
support the goals of a particular CTF organizer.  Understanding the 
constraints enforced by the CTF infrastructure, effects of scoring, and 
ultimately strategies that opponents may employ are all critical components 
to succeeding in CTF.   Above all else, it is critical to understand how to 
participate in a particular CTF as a whole, as excellence in one particular 
aspect might prove worthless due to a particular scoring metric. 

The overview presented here merely scratches the
surface of what has already been done with CTFs.  The diversity and
flexibility inherent in CTF implementation choices indicates that there
are numerous ways to create a CTF.  This, bundled with a clearly increasing 
appetite for CTFs is evidence that CTFs will continues to provide a rich 
ground for innovation for some time to come.

