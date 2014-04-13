# SSHGithub

## Installation
To install or update launch the install script.

	# ./install.sh

and add the **AuthorizedKeysCommand** directive to your sshd configuration

	# echo 'AuthorizedKeysCommand /root/sshgithub.py' >> /etc/ssh/sshd_config
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
