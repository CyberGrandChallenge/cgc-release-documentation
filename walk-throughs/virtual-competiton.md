# Virtual Competition

This walk-through will guide you in the use of a CGC CFE simulator, known as Virtual Competition

The sole purpose of Virtual Competition is to facilitate CRS development in 
preparation for CFE.  Unlike CQE, CFE will evolve over time allowing many 
interactions between a CRS and the CGC infrastructure.

## About Virtual Competition

At it's core, Virtual Competition is a set of DECREE virtual machines.  In fact,
it's actually several instances of the same DECREE virtual machine assigned to 
different roles: ti, cb, ids, pov, and crs.  Briefly reviewing each role is useful
in understanding why the role is included as part of Virtual Competition:

* **ti** - this is the Team Interface.  The role represents the interface that will be provided to a CRS by the CFE infrastructure.
* **cb** - this is the Challenge Binary server.  This is the host where CBs are executed.
* **pov** - this is the POV server.  This role has the responsibility of 'throwing' POVs (and polls) at the cb server.
* **crs** - this is a host for simulating a CRS.  While no, simulated CRS capabilities are distributed as part of Virtual Competition, a sample client is provided to exercise the Team Interface.
* **ids** - this is the IDS host; the network appliance.  Filters fielded by a CRS will be installed on ids.  From a network perspective, ids is in between pov and cb.


## Obtaining Virtual Competition

Virtual Competition requires obtaining three components: the CGC development 
virtual machine, Vagrant, and a CGC-specific Vagrant 
configuration file used to manipulated the various Virtual Competition roles.

For more information about Vagrant, see walk-through Running the Virtual Machine (`running-the-vm.md`).

The Virtual Competition Vagrant `Vagrantfile` can be obtained from the CGC repo:

    $ wget http://repo.cybergrandchallenge.com/boxes/Vagrantfile

There is no need to manually download a DECREE .box file, Vagrant will do this automatically.

## Starting Virtual Competition

Most of the virtual machine functionality is automated by Vagrant.  To create virtual machines for each role and start each machine, issue 'vagrant up' while in the same directory as the Vagrantfile:

    $ vagrant up

The status of the virtual machines employing the Virtual Competition roles can be observed with vagrant:

    $ vagrant status
    Current machine states:

    cb                        running (virtualbox)
    ids                       running (virtualbox)
    pov                       running (virtualbox)
    crs                       running (virtualbox)
    ti                        running (virtualbox)

Note that most Vagrant actions are similar to those discussed in the walk-through Running the Virtual Machine (`running-the-vm.md`).  The difference is that the Vagrantfile for Virtual Competition is designed to run multiple virtual machines.  This may create some ambiguity depending on how the reader has used Vagrant in the past.  For example, when connecting to a host:

    $ vagrant ssh

The ssh command is ambiguous, to which virtual machine should Vagrant connect?  It so happens that in the provided configuration the crs role is assigned as the default ('primary') virtual machine, so the above ssh command would connect to the crs virtual machine.  To explicitly scope commands to a particular virtual machine, use the role moniker.  For example, to only start ti role specify the **ti** host:

    $ vagrant up ti

Even though each role is based on the same virtual machine, the instances are changed slightly by Vagrant so as to employ different IP addresses and hostnames.  These differences are detected by software common to the virtual machine instances to change the behavior of each role host.  For example, the host with the ti role may automatically starts a server component to make the CRS Team Interface API available.


## Establishing the Team Interface Server (Server side)

The server side components of Virtual Competition consist primarily of two tools: `ti-server` and `ti-rotate`.  `ti-rotate` generates data to simulate CFE rounds.  `ti-server` then makes this data available to a CRS.  Without `ti-rotate`, the `ti-server` has access to no data to serve.  These components should be run on the **ti** host.

To simulate many CFE rounds:

    $ vagrant ssh ti
    ti$ ti-rotate --roundlen 5 --debug

With this invocation, `ti-rotate` will continue to simulate new CFE rounds every 5 seconds until the process is stopped. Note that this 5 second round time is completely notional at this time.

`ti-server` can then make the data available to a CRS via HTTP and JSON. 

    ti$ ti-server


`ti-server` and `ti-rotate` require several configurable options.  For example, they both default to interactions as CFE team 1.  Of course, in CFE not all competitors will be identified as team 1.  Similarly, in Virtual Competition the authentication credentials are user *vagrant* and password *vagrant*, which `ti-server` will assume by default.  The situation is similar for local directory location for CBs, the directory that `ti-rotate` populates and is in-turn served by `ti-server` (e.g. webroot), and so on.

## Exercising the Team Interface(Client side)

An example client interface is provided in Virtual Competition to facilitate interactions with the Team Interface server.  In CFE, the consumer of the Team Interface data would be a CRS.  The example client employs an interactive prompt facilitating retrieval of data from a `ti-server`:

    $ vagrant ssh crs
    crs$ ti-client --hostname ti
    ti-client> help

    Documented commands (type help <topic>):
    ========================================
    EOF        counts  feedback  round       teams       upload_pov
    consensus  exit    help      scoreboard  upload_ids  upload_rcb

further help can be observed for each topic:

    ti-client> help upload_rcb

        Arguments:
            upload_rcb <CSID> <CBID>:<filename> ...[<CBID_N>:<filename_N>]

        Upload a new set of CBs for the specified challenge set

        Examples:
            upload_rcb CADET_00001 CADET_00001:/tmp/CADET_00001/bin/CADET_00001_patched
            upload_rcb LUNGE_00005 LUNGE_00005_3:/tmp/LUNGE_00005/bin/LUNGE_00005_3    
            
observe current round, scoreboard and teams:
    
    ti-client> round
    5
    ti-client> scoreboard
    1: 380
    5: 319
    4: 312
    3: 260
    2: 232
    6: 223
    7: 188
    ti-client> teams
    1, 2, 3, 4, 5, 6, 7

retreive feedback on CBs:
    
    ti-client> feedback cb
    1435856617 LUNGE_00002 - signal: 11
    1435856617 LUNGE_00002 - signal: 11
    1435856617 LUNGE_00002 - signal: 4

retreive LUNGE_00002 IDS rules for team 1 from round 0 fof consensus evaluation:

    ti-client> consensus LUNGE_00002 ids 1 0 /tmp
    downloaded: /tmp/LUNGE_00002-1-0.ids

retreive LUNGE_00002 CB for team 3 from round 1 for consensus evaluation:
   
    ti-client> consensus LUNGE_00002 cb 3 1 /tmp
    downloaded: /tmp/LUNGE_00002-3-1.cb

submit IDS signatures to the network appliance:    
    
    ti-client> upload_ids LUNGE_00002 /usr/share/ids/examples/LUNGE_00002.rules
    upload completed during round: 2    
    
leave the interactive client:    
    
    ti-client> exit

The data above is simulated by `ti-rotate`, therefore the round, scores, feedback, etc will vary.

## Testing Challenge Binaries

The reader may be familiar with testing a CB with commands similar to:

    $ cb-test --cb LUNGE_00002 --directory bin --xml pov/POV_00000.xml 
    ...
    # polls passed: 0
    # polls failed: 1
    not ok - process cored: (signal 11: SIGSEGV)
    
    $ cb-test --cb LUNGE_00002 --directory bin --xml poller/for-release/GEN_00333.xml
    ...
    # polls passed: 1
    # polls failed: 0

Virtual Competition facilitates similar testing across relevant CFE hosts, for example, throwing a POV from the **pov** host to the **cb** host.

    $ cb-test --cb LUNGE_00002 --directory bin --xml pov/POV_00000.xml --enable_remote 
    ...
    # polls passed: 0
    # polls failed: 1
    not ok - process cored: (signal 11: SIGSEGV)
    
    $ cb-test --cb LUNGE_00002 --directory bin --xml poller/for-release/GEN_00333.xml --enable_remote
    ...
    # polls passed: 1
    # polls failed: 0

Additionally, the POV can be tested with the IDS role.  That is, a POV may be thrown from the **pov** host traversing the **ids** host to the **cb** host.  The previous example actually traversed the **ids** host as well, however, the **ids** had no rules to enforce on that CB.  In this case, we provide a rules file for the **ids** to enforce:

    $ cb-test --cb LUNGE_00002 --directory bin --xml pov/POV_00000.xml --enable_remote --ids_rules /usr/share/ids/examples/LUNGE_00002.rules

    ...
    # cb-proxy: 2015-07-07 04:39:40,570 - INFO : blocking connection: filter matched...
    ...
    # polls passed: 0
    # polls failed: 1

    $ cb-test --cb LUNGE_00002 --directory bin --xml poller/for-testing/GEN_00602.xml --enable_remote --ids_rules /usr/share/ids/examples/LUNGE_00002.rules

    ...
    # polls passed: 1
    # polls failed: 0

In addition the interfaces provided on **ti* (exercised in this document with `ti-client`), the network appliance is capable of emitting best-effort network trace information similar to a network tap.  This information is emitted from `cb-proxy` and can be consumed with an example application `cb-packet-log`.  

To capture the network appliance UDP packets as part of `cb-test` utilize the --pcap option in conjunction with --enable_remote:


    $ cb-test --cb LUNGE_00002 --directory bin --xml poller/for-testing/GEN_00602.xml --enable_remote --ids_rules /usr/share/ids/examples/LUNGE_00002.rules --pcap ~/LUNGE_00002_ids_tap.pcap


A sample Wireshark decoder for the UDP network trace format can be found in `/usr/share/ids/extra/cgc.lua`.

More information about the IDS and the rules language can be found in the Using the Network Appliance walk-through (`using-the-network-appliance.md`), and the man pages for `cb-proxy` and `cb-packet-log`.

## End-to-end example of Virtual Competition

Start all of Virtual competition:

    $ vagrant up

Populate some CBs, in this example we have populated `LUNGE_00002`

    $ vagrant ssh ti

    ti$ cd /usr/share/cgc-sample-challenges/examples/LUNGE_00002/ && sudo make build generate-polls install
    ti$ cd /usr/share/cgc-sample-challenges/examples/LUNGE_00005/ && sudo make build generate-polls install
    ti$ cd /usr/share/cgc-sample-challenges/examples/EAGLE_00005/ && sudo make build generate-polls install

    ti$ cp -r /usr/share/cgc-challenges /tmp/test-cbs
    ti$ ls /tmp/test-cbs/
    LUNGE_00002
    LUNGE_00005
    EAGLE_00005

In CRS testing, there is utility in exercising all the options of the Virtual Competition tools.  For example, consider testing `ti-server` on a different port with a non-default webroot.


Start round simulation:

    ti$ cd
    ti$ ti-rotate --roundlen 300 --cbdir /tmp/test-cbs --webroot /tmp/test-webroot --team 4 --rounds 96 &

Start ti-server:

    ti$ ti-server --port 16000 --cbdir /tmp/test-cbs --username tim --password Katahdin --webroot /tmp/test-webroot --team 4


Connect with the client:

    $ vagrant ssh crs
    crs$ ti-client --hostname ti --port 16000 --username tim --password Katahdin --team 4
    ti-client> round
    ...
    ti-client> scoreboard
    ...
    ti-client> exit
    
Test polls and POVs:

    crs$ cd /usr/share/cgc-sample-challenges/examples/LUNGE_00002/ && sudo make build generate-polls install
    ...
    crs$ cb-test --cb LUNGE_00002 --directory bin --xml pov/POV_00000.xml --enable_remote --ids_rules /usr/share/ids/examples/LUNGE_00002.rules 
    ...

    crs$ cb-test --cb LUNGE_00002 --directory bin --xml poller/for-release/GEN_00335.xml --enable_remote --ids_rules /usr/share/ids/examples/LUNGE_00002.rules --pcap ~/LUNGE_00002_pol_gen_00335.pcap
    
## Updating Virtual Competition

The Vagrantfile for Virtual Competition includes an ability to check for new versions of the DECREE Virtual Machine.  When starting a Vagrant Virtual Machine you may experience a message similar to:

    ==> ti: A newer version of the box 'cgc-linux-dev' is available! You currently
    ==> ti: have version '6993'. The latest is version '7012'. Run
    ==> ti: `vagrant box update` to update.

This indicates that a newer version than the most recently download version of DECREE available.  To update virtual competition:

Destroy the local instances (any information stored solely in any of the virtual machines will be lost):

    $ vagrant destroy

Update the local DECREE virtual machine box:

    $ vagrant box update

Delete the outdated box (note: the numerical version may appear differently):

    $ vagrant box list
    cgc-linux-dev (virtualbox, 6993)
    cgc-linux-dev (virtualbox, 7012)

    $ vagrant box remove cgc-linux-dev --box-version 6993

Re-deploy Virtual Competition

    $ vagrant up

## SEE ALSO

For information regarding using a DECREE Virtual Machine , see the `running-the-vm.md` walk-through
For information regarding the IDS and IDS rules, see the `using-the-network-appliance.md` walk-through.


For information regarding using the components of Virtual Competition, see man ti-client(1), ti-server(2), ti-rotate(1), cb-proxy(1)

For support please contact CyberGrandChallenge@darpa.mil
