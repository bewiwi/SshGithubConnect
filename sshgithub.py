#!/usr/bin/python
__author__ = 'bewiwi'

import ConfigParser
import sys
import syslog
import urllib2
import os
import stat
import time

class SSHGithub():
    def __init__(self):
        configpath = '/etc/sshgit.ini'
        if not os.path.isfile(configpath):
            raise Exception('Config file not found : ' + configpath)

        self.checkPerm(configpath)
        self.config = ConfigParser.ConfigParser()
        self.config.read(configpath)

        #Set url
        if not self.config.has_option('SERVER', 'url'):
            raise Exception('No url parameter')
        self.url = self.config.get('SERVER', 'url')

        #Set Cache
        self.cache_time = 0
        if self.config.has_option('SERVER', 'cache_time'):
            self.cache_time = self.config.getint('SERVER', 'cache_time')
            if self.cache_time > 0:
                self.cache_folder = self.config.get('SERVER', 'cache_dir')

                if not os.path.exists(self.cache_folder):
                    os.makedirs(self.cache_folder, mode=0700)
                self.checkPerm(self.cache_folder)
                self.removeOldCache()

    def error(self, e):
        syslog.syslog(syslog.LOG_ERR, e.message)
        raise e

    def checkPerm(self, path):
        st = os.stat(path)

        #Other write access
        if bool(st.st_mode & stat.S_IWOTH):
            self.error(Exception("Bad permission : %s must at least 0660" % path))

        #Owner Check
        if st.st_uid != 0 or st.st_gid != 0:
            self.error(Exception("Bad ownership : %s must be root:root" % path))

        return True

    def getAuthorizedKey(self, SysUser):
        syslog.syslog(syslog.LOG_INFO, 'Get keys for %s' % SysUser)
        users = self.getGitUserAuthorized(SysUser)
        keys = []
        for user in users:
            keys = keys + self.getUserKeys(user)
        return keys

    def getGitUserAuthorized(self, SysUser):
        if not self.config.has_option('USER', SysUser):
            return []
        return self.config.get('USER',SysUser).split(',')

    def getUserKeys(self, user):

        if self.cache_time > 0 :
            cache_keys = self.getUserKeyInCacheDir(user)
            if cache_keys != False:
                syslog.syslog(syslog.LOG_INFO, 'Get keys for %s from cache' % user)
                return cache_keys

        keys = self.getUserKeyInServer(user)
        self.addUserKeyInCacheDir(user, keys)
        syslog.syslog(syslog.LOG_INFO, 'Get keys for %s from server' % user)
        return keys

    def getUserCacheFile(self, user):
        return self.cache_folder + '/' + user

    def getUserKeyInCacheDir(self, user):
        #Secu
        if not os.path.exists(self.getUserCacheFile(user)):
            return False
        if not os.path.isfile(self.getUserCacheFile(user)):
            self.error(Exception('Cache file is not a file , Hack ?'))
        self.checkPerm(self.getUserCacheFile(user))

        #read
        f = open(self.getUserCacheFile(user), 'r')
        keys = f.read().splitlines()
        f.close()
        return keys

    def addUserKeyInCacheDir(self, user, keys):
        cache_file = open(self.getUserCacheFile(user), 'a')
        os.chmod(self.getUserCacheFile(user), stat.S_IRUSR)
        for key in keys:
            cache_file.write(key + '\n')
        cache_file.close()

    def removeOldCache(self):
        for file in os.listdir(self.cache_folder):
            (mode, ino, dev, nlink,
             uid, gid, size, atime,
             mtime, ctime) = os.stat(self.cache_folder+file)

            diff = ((int(time.time()) - ctime) / 60)
            if diff >= self.cache_time:
                syslog.syslog(syslog.LOG_INFO, 'Remove %s from cache (to old)' % file)
                os.remove(self.cache_folder+file)

    def getUserKeyInServer(self, user):
        try:
            userUrl = self.url + user + '.keys'
            response = urllib2.urlopen(
                userUrl
            ).read()
            strkeys = response.split('\n')
            return strkeys
        except urllib2.HTTPError as e:
            syslog.syslog(syslog.LOG_ERR, 'Error HTTP with ' + userUrl)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, 'Unknown error ' + str(e))
        return []


if __name__ == "__main__":

    if len(sys.argv) > 2 or len(sys.argv) == 1:
        raise Exception('Invalid argument number')

    ssh_github = SSHGithub()
    for key in ssh_github.getAuthorizedKey(sys.argv[1]):
        print key