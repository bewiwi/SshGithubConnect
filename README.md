# SSHGithub

## Installation
To install or update launch the install script.

	# ./install.sh

and add the **AuthorizedKeysCommand** directive to your sshd configuration

	# echo 'AuthorizedKeysCommand /usr/bin/sshgithub' >> /etc/ssh/sshd_config
	# service sshd reload
	
## Configuration
The file configuration is **/etc/sshgit.ini**

First, you need to configure the **url** directive in **[SERVER]** section. url directive can be https://github.com or a gitlab url. Next edit th **[USER]** section and add one line per system user.

###Example
This config file authorize gituser and gituser2 to connect to root and gituser to connect to user2

	[SERVER]
	url=https://github.com/
	#url=https://gitlab/
	
	[USER]
	#sysuser=gituser,gituser2
	root=gituser,gituser2
	user2=gituser


## TEST
You can directly launch the command with the user

	# sshgithub root
	ssh-rsa AAAAB3NzaC1yc2EAA.....
	ssh-rsa AAAAB3NzaC1yc2EAA.....
	
And you can try to connect to ssh with an authorized account.

## DEV
Just use vagrant

	(host)    $ vagrant up
	(host)	  $ vagrant ssh
	(vagrant) $ sudo /vagrant/install.sh && sudo sshgithub root	