# Dynamically writing polls

Challenge binary interactivity verification within the context of DARPA's Cyber
Grand Challenge is implemented via specialized unit tests known as "service
polls".  Service polls are intended to validate the performance and
functionality of challenge binaries in order to test the efficacy and impact of
reformulation performed by competitors.  Similar in ideals to unit tests,
service polls should be written to validate the interactivity and complex state
machines implemented by CBs.

Due to the requirements for CB authors to deliver a large number of CB
validations that are both deterministic and unique, a service poll generator
has been provided that may be used to assist in developing these polls.

Developing services polls using the generator is performed through the use of a
weighted directed graph, and an associated python module that implements the
state machine that is used to generate the polls.

## Directed Graph

The Directed Graph specifies the connection between each individual components
within the state machine, allowing a CB author to define the polls as small
individual components, and explore the combinatorial permutations of between
the different components for CB validation.

The directed graph defines individual nodes, which relate to a method in the
provided python class, and edges, which define which nodes could be called upon
completion of the execution of a given node.

These components are defined in YAML, at the top level as a dictionary, 'nodes'
and 'edges' respectively.

### Nodes

The 'nodes' entry is composed of a list of dictionaries, each defining an
individual node.  Each dictionary must contain the key 'name', which is a
string that defines the name of the given node.  The value of the 'name' entry
corresponds to the name of the method within the provided python module that
should be executed upon accessing that node during the graph traversal.

Within this dictionary, two additional entries are supported: 'chance' and
'continue'.  Both 'chance' and 'continue', if provided,  are specified as
floats between 0.0 and 1.0. 

* 'continue' allows the developer to specify the likelihood that the state machine should continue processing upon execution of the node.
    
* 'chance' allows the developer to specify the likelihood that the state machine should execute the node, or continue traversal of the graph without executing the underlying functionality of the node.

Node names must be unique.  If the node name 'start' is provided, then
traversal will always begin at this node, otherwise, the traversal will start
at a random node in the graph.

### Edges

The 'edges' entry is composed of a list of dictionaries, each defining an edge
between two nodes.  Each dictionary can have up to two entries, with the first
defining the start and end nodes for a given edge.  The key and value both
refer to a node defined in the 'nodes' entry.  Within this dictionary, one
additional entry is supported: 'weight'.  'weight', if provided, is specified as
a float between 0.0 and 1.0.

* 'weight' allows the developer to specify the likelihood of traversal of a given edge when a node has multiple edges leaving the node within the graph.

## State Machine

The State Machine is a python class, which defines the implementations of
methods that perform the interactions with a service for a given state.  The
underlying implementation is a subclass of the generator.Actions python class
provided as part of the poll-generation package.

This class provides a set of methods that perform specific functions that are
reliant for CB interactions performed via the XML DTD used by 'cb-replay'.
These methods are:

* read: creates a read interaction
* write: creates a write interaction
* xml: create an XML for all of the existing interactions
* chance: simple to use wrapper to get a True or False value, specifying the likelihood that True will be taken via a float between 0.0 and 1.0.
* reset: resets the internal state of the machine, which is called per iteration of the graph traversal.

To create a state machine for use within the generate-polls, provide methods
for each node in the directed graph described above.  Each method should call
self.read and self.write as needed, which will implement read and write
interactions to the service.

There is a dictionary 'state', that is provided by the parent class that can be
used for storing arbitrary intermediary values during execution of a given
iteration but is reset between each iteration.  The 'state' dictionary is
reinitialized by the above 'reset' method.

# Sample Implementation Walk Through

A sample implementation of a poll generator, ftplite, is provided in the
/usr/share/poll-generator/examples/.  This generator provides a state machine
interaction to an FTP like protocol.

The 9 unique states in the machine, defined as the following:

    after_login, delete, fetch, file_list, login, logout, password, put, start

Each of these states have an entry in the graph as well as a method in the
python implementation of the state machine.

Looking at the python implementation, there are a few items of note.  The methods
'start' and 'after_login' are empty methods.  These methods are used as a common 
point for the directed graph to connect into.

The 'start' method is provided such that each iteration of walking the state
machine starts at the same location.

The 'after_login' method provides a common location in the graph that can such
that each of the methods intended to be run in an arbitrary combinations once
logins have occurred do not need to link to all of the rest of the methods.

In the 'state' dictionary, the key 'login' is used to track if the 'login'
state successfully completed.  This shows the ability to store and access
arbitrary information between states within the graph.

# Sample Implementation Walk Through 2

This is a step-by-step walkthrough for the overly simple CADET_00001 Palindrome service. The service is comprised of a banner on the initial connect, a banner requesting the user enter a possible palindrome, the user entering a palindrome, and the service returning back a response. We will build the state machine and the graph for this simple service.

Starting in the CADET_00001 directory edit poller/for-release/machine.py:

## Python module dependancies

Service poll generators are required to import the *Actions* module. Any others are up to the author. In our example we also use the *random* and *string* modules.

    from generator.actions import Actions
    import random
    import string

## Service poll generation class

The service poll generator expects a class derived from the CGC *Actions* class. This class will define each individual state in a service poller state machine. This class should also contain an empty *start* member which serves as the entry to the state machine.

    class Palindrome(Actions):
        def start(self):
            pass

## Banner

The palindrome service always begins with a "Welcome to Palindrome Finder" banner with an extra carriage return before it. Our state machine needs confirm the presence of this banner.

        def banner(self):
            # Confirm the initial empty line
            self.read(delim='\n', expect='\n')
            # Confirm the actual banner
            self.read(delim='\n', expect='Welcome to Palindrome Finder\n')

## State graph

We've created our first node in the state machine, now we need to connect it in the graph. The state machine graph is constructed in the state-graph.yaml file. It is composed of two sections.
1. Node definitions
2. Node connections

The format of the file looks like

    ---
    nodes:
    <add nodes here>
    edges:
    <add edges here>

### Initial node definitions

We created two nodes, start and banner, which must be defined in the state tree:

    - name: start
    - name: banner

We also need to define the edge for the state machine to traverse from the fictional start node into the banner:

    - start: banner

## Testing

We have a very rudimentary service poller generator that this point which can be tested. Generate one service poll via:

    $ generate-polls --count 1 poller/for-release/machine.py poller/for-release/state-graph.yaml poller/for-release

* Please note that the above generation example will fail with more complex graphs since a single generation won't hit all of the nodes. The count must be expanded for these more complex graphs

A single service poll was created in poller/for-release/gen_000000.xml
This service poll can be manually inspected or tested against the challenge binary with:

    $ cb-test --cb CADET_00001 --directory bin --xml poller/for-release/gen_000000.xml

The expected output indicates that strings matched:

    # service - poller/for-release/gen_000000.xml
    ok 1 - match: string
    ok 2 - match: string
    # passed: 2
    # failed: 0
    # total passed: 2
    # total failed: 0

An alternative testing strategy involves spawning the CB in one window while connecting to it with the cb-test utilility like so:	

    Window 1: sudo cb-server --insecure --once -p 12345 -d . bin/CADET_00001
    Window 2: cb-replay --failure_ok --host 127.0.0.1 --port 12345 poller/for-release/gen_000000.xml

## Handling palindrom requests

Following the banner, the service asks the user for possible palindromes. We must parse this request and test it with palindromes and non-palindromes.

    def request(self):
        # Skip the empty line
        self.read(delim='\n', expect='\n')
        # Confirm the request
        self.read(length=37, expect='\tPlease enter a possible palindrome: ') 

    def palindrome(self):
        halfword = self.random_string(random.randint(1, 16))
        self.write(halfword + halfword[::-1] + "\n")
        self.read(delim='\n', expect='\t\tYes, that's a palindrome!\n\n')

    def not_palindrome(self):
        word = self.random_string(random.randint(2, 32))
        while self.is_palindrome(word):
                word = self.random_string(random.randint(2, 32))
        self.write(word + "\n")
        self.read(delim='\n', expect='\t\tNope, that's not a palindrome\n\n')

## Helper functions
    def is_palindrome(self, word):
        for i in range(0, len(word) / 2):
                if word[i] != word[-i - 1]:
                        return False
        return True

    def random_string(self, size):
        chars = string.letters + string.digits
        return ''.join(random.choice(chars) for _ in range(size))


### Node definitions

We created three nodes which must be defined in the state tree: request, palindrome, and not_palindrome.

In the state tree:

    - name: request
      continue: .9
    - name: palindrome
    - name: not_palindrome

Note the 'continue' entry. There is a 90% chance that the poll generator will continue down the state graph on every service poll and a 10% chance that the service poll will stop.

We also need to define the edges for the state machine to traverse these nodes.  First we link the previous _banner_ node into the _request_ node and then into the _palindrome_ and _not_palindrome_ nodes.

    - banner: request
    - request: palindrome
      weight: .2
    - request: not_palindrome
      weight: .8

Note that each of the request edges contains a weight. 20% of the time the request will lead to a palindrome and 80% of the time it will lead to a non-palindrom.

Finally we must link both _palindrome_ and _not_palindrome_ back into the _request_ since this is effectively a circular state graph.

    - palindrome: request
    - not_palindrome: request


## Evaluating the generated polls

The poll generated creates an edges.png and a nodes.png in the output directory. These should be manually inspected to confirm the desired graph traversals and nodes are reached.
