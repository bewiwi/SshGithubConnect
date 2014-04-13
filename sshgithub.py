#!/usr/bin/python
__author__ = 'bewiwi'

import ConfigParser
import sys
import syslog
import urllib2
import os
import stat

class SSHGithub():

    def __init__(self):
        configpath='/etc/sshgit.ini'
        if not os.path.isfile(configpath):
            raise Exception('Config file not found : '+configpath)

        st = os.stat(configpath)

        #Other write access
        if bool(st.st_mode & stat.S_IWOTH):
            raise Exception('Invalid right on the config file must be 0600')

        #Owner Check
        if st.st_uid != 0 or st.st_gid != 0 :
            raise Exception('Config file bad ownership must be root:root')

        self.config = ConfigParser.ConfigParser()
        self.config.read(configpath)
        if not self.config.has_option('SERVER','url'):
            raise Exception('No url parameter')
        self.url = self.config.get('SERVER','url')

    def getAuthorizedKey(self,SysUser):
        users = self.getGitUserAuthorized(SysUser)
        keys = []
        for user in users:
            keys=keys+self.getUserKeys(user)
        return keys

    def getGitUserAuthorized(self,SysUser):
        if not self.config.has_option('USER',SysUser):
            return []
        return self.config.get('USER',SysUser).split(',')

    def getUserKeys(self,user):
        try:
            userUrl = self.url+user+'.keys'
            response = urllib2.urlopen(
                userUrl
            ).read()
            strkeys = response.split('\n')
            return strkeys
        except urllib2.HTTPError as e:
            syslog.syslog(syslog.LOG_ERR,'Error HTTP with '+userUrl)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,'Unknown error '+str(e))
        return []


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise Exception('Invalid argument number')
    ssh_github = SSHGithub()
    for key in ssh_github.getAuthorizedKey(sys.argv[1]):
        print key