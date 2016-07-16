# Running the Virtual Machine

This walk-through will guide you through the process of using Vagrant to automatically download, provision and run the development and testing VM.

## Basic Background Information

### Vagrant 

[Vagrant] [1] is a tool for automating the process of distributing, setting up (provisioning) and tearing down virtual machine images. The basic idea is for the cgc-team to make updates to a single master or base virtual machine image (known as a *box* in Vagrant parlance) and let Vagrant handle the task of downloading the box (if it hasn't already been downloaded,) cloning it (so that the original box remains unaltered) and then provisioning the clone (we will call this a VM) for use by the end user. All of this is configured in *Vagrantfile* script, which we will discuss next. 

The reader is welcomed to visit the [Vagrant documentation][2] page for more detailed information. This guide is based on that one.

[1]: http://www.vagrantup.com 	"Vagrant" [2]: http://docs.vagrantup.com	"Vagrant Docs"


### cgc-linux-dev

The development VM is known as *cgc-linux-dev* and the corresponding Vagrantfile configuration script is located at:

	http://repo.cybergrandchallenge.com/boxes/Vagrantfile

## The Basics

### Getting started

Getting started is extremely simple, just download the Vagrant script and issue the *vagrant up* command. Some sample output can be seen below:

	$ mkdir cgc
	$ cd cgc
	$ wget http://repo.cybergrandchallenge.com/boxes/Vagrantfile
	$ vagrant up
	Bringing machine 'default' up with 'virtualbox' provider...
	==> default: Box 'cgc-linux-dev' could not be found. Attempting to find and install...
	    default: Box Provider: virtualbox
	    default: Box Version: >= 0
	==> default: Adding box 'cgc-linux-dev' (v0) for provider: virtualbox
	    default: Downloading: http://repo.cybergrandchallenge.com/boxes/cgc-linux-dev.box
	==> default: Successfully added box 'cgc-linux-dev' (v0) for 'virtualbox'!
	==> default: Importing base box 'cgc-linux-dev'...
	==> default: Matching MAC address for NAT networking...
	==> default: Setting the name of the VM: provision-images_default_1399661463923_1981
	==> default: Clearing any previously set network interfaces...
	==> default: Preparing network interfaces based on configuration...
	    default: Adapter 1: nat
	==> default: Forwarding ports...
	    default: 22 => 2222 (adapter 1)
	==> default: Running 'pre-boot' VM customizations...
	==> default: Booting VM...
	==> default: Waiting for machine to boot. This may take a few minutes...
	    default: SSH address: 127.0.0.1:2222
	    default: SSH username: vagrant
	    default: SSH auth method: private key
	    default: Warning: Connection timeout. Retrying...
	==> default: Machine booted and ready!
	==> default: Checking for guest additions in VM...
	==> default: Mounting shared folders...
	    default: /vagrant => /private/tmp/cgc
	==> default: Running provisioner: file...
	==> default: Running provisioner: file...
	==> default: Running provisioner: shell...
	    default: Running: inline script
	==> default: Running provisioner: shell...
	    default: Running: inline script

The output shows how vagrant detects that the *cgc-linux-dev* box does not yet exist and so retrieves it from the cgc server. After the download has completed, vagrant then goes about cloning the virtual machine, provisioning it and then starting it. After the machine has been started, it will then wait until *ssh* is up and running in the VM at which time the VM is ready to use.

Once the VM is up and running, the *vagrant ssh* can be used to ssh into the VM. Once inside the VM, the user should see that the main configuration files (e.g. .profile) have been copied over from the host.

	$ vagrant ssh
	Linux cgc-linux-packer 3.13.2-cgc #1 Fri May 2 18:20:50 UTC 2014 i686
	
	The programs included with the Debian GNU/Linux system are free software;
	the exact distribution terms for each program are described in the
	individual files in /usr/share/doc/*/copyright.
	
	Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
	permitted by applicable law.
	Last login: XXXXXXXXXXXXXXXXXXXXXXXXXXXX 
	vagrant@cgc-linux-packer:~$ 


### On the VM

The CGC Virtual machine has been pre-installed with all of the CGC
enabled tools and manual pages.

#### CGC Enabled tools

Several build tools have been ported and others written to work on CGC binaries. These include:

	* binutils
	* cgcef-verify
	* libcgcef
	* readcgcef

More information is provided in the _Debugging a Challenge Binary_ and the _Testing a Challenge Binary_ walk-throughs.

#### Man pages of interest

	$ man cgcabi
	$ man cgc_executable_format

#### System Calls

	$ man _terminate
	$ man transmit
	$ man receive
	$ man fdwait
	$ man allocate
	$ man deallocate
	$ man random


### Sharing Files

Vagrant automatically sets up a shared folder for convenience. In cgc-linux-dev, the */vagrant* in the VM is **linked** directly to the directory where the Vagrantfile is located. This means that changes made to the directory or its files in the host are directly visible in the VM and vice versa. This is extremely useful since vagrant relies on ssh connections to the VM instead of a graphical UI. Thus, with direct sharing, one can simply edit the files from the host (e.g. using a graphical editor). 

** WARNING: Don't forget that the Vagrantfile directory on the host *is* the /vagrant directory in the VM. **

### Pausing/Stopping the VM

One of the first things you can do with a VM is to suspend it with *vagrant suspend*. This will save the current runtime state of the VM into the file system so you can restore it later. To restore the state, simply run *vagrant up* again. 

	$ vagrant suspend
	==> default: Saving VM state and suspending execution...
	
	$ vagrant up
	Bringing machine 'default' up with 'virtualbox' provider...
	==> default: Resuming suspended VM...
	==> default: Booting VM...
	==> default: Waiting for machine to boot. This may take a few minutes...
	    default: SSH address: 127.0.0.1:2222
	    default: SSH username: vagrant
	    default: SSH auth method: private key
	    default: Warning: Connection refused. Retrying...
	==> default: Machine booted and ready!

Use the *vagrant halt* command to shutdown or halt the machine. Once again, *vagrant up* can be used to bring the machine back up and running.

	$ vagrant halt
	==> default: Attempting graceful shutdown of VM...

** WARNING: All open connections will be closed when you suspend or halt the VM. Thus, make sure all of your progress is saved prior to issuing those commands **

### Updated VMs

The CGC team will periodically update the cgc-linux-dev virtual machine. Vagrant will automatically fetch an updated VM on the next *vagrant up* after the user removes the old VM.

	$ vagrant halt -f
	==> default: Forcing shutdown of VM...
	$ vagrant destroy
	    default: Are you sure you want to destroy the 'default' VM? [y/N] y
	==> default: Destroying VM and associated drives...
	==> default: Running cleanup tasks for 'file' provisioner...
	==> default: Running cleanup tasks for 'file' provisioner...
	==> default: Running cleanup tasks for 'shell' provisioner...
	==> default: Running cleanup tasks for 'shell' provisioner...
	$ vagrant box remove cgc-linux-dev
	Removing box 'cgc-linux-dev' (v0) with provider 'virtualbox'...
	$ vagrant up
	

The *vagrant destroy -f* command can be used to bypass the prompt should the user wish to script this process.

## Misc.

### User config files

In order to provide a consistent user environment, *.profile*, *.bashrc*, *.vimrc*, etc. are copied from the current user's home directory on the host into the vagrant user's home directory within the VM.


### Running the VM without Vagrant

While Vagrant is the preferred way to run the virtual machines, it is possible for the user to use another virtualizaton suite aside from VirtualBox (which is what Vagrant uses). The provisioned VM images can be found inside the *~/VirtualBox VMs* directory (you can also browse for it using the "Oracle VM VirtualBox Manager".) For example you might see a directory called *provision-images_default_1234567890_12345" which will contain the *.vmdk* disk image as well as the *.vbox* configuration file. The *.vmdk* image can be imported into VMware for example; just keep in mind that the shared folders might not exist.

The VirtualBox image itself can be downloaded from http://repo.cybergrandchallenge.com/boxes/cgc-linux-dev.box


# Support

For support please contact CyberGrandChallenge@darpa.mil
