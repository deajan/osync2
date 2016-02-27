#!/usr/bin/env python3.4

#TODO: sphinx ou doxygen
#TODO: create libosync ?

PROGRAM="osync2"
AUTHOR="(L) 2013-2016 by Orsiris de Jong"
CONTACT="http://www.netpower.fr/osync2 - ozy@netpower.fr"
PROGRAM_VERSION="2.0-dev-nothing-works-yet"
PROGRAM_BUILD=201602402
IS_STABLE=False

import os
import sys, getopt
import getpass
import logging
import configparser
import time
import watchdog.events
import watchdog.observers

## BEGIN CONSTANTS (all filenames must be defined in the following class)

INITIATOR_TYPE = "initiator"
TARGET_TYPE = "target"

class OsyncDirectoryStructure:
	"""Contains osync directory structure"""

	osync_dir = ".osync2_workdir"
	lock_file = "lock"
	state_dir = "state"
	backup_dir = "backup"
	delete_dir = "deleted"
	partial_dir = "_partial"
	last_action_file = "last-action"
	resume_count_file = "resume-count"
	oss_file = "oss"
	deleted_list_file = "deleted-list"
	moved_list_file = "moved-list"
	modded_list_file = "modded-list"
	created_list_file = "created-list"

## END CONSTANTS


## GLOBAL VARIABLES
CONFIG = 0 # Contains full configuration array
INITREPLICA = 0 # Contains init replica instance
TARGETREPLICA = 0 # Contains target replica instance list
### END GLOBAL VARIABLES

class OsyncStateSerial():
	"""Reads and writes current state serial file for local replica"""

	def __init__(self, oss_file):
		self.oss_file = oss_file

	def get_local(self):
		if os.path.exists(self.oss_file):
			file_handle = open(self.oss_file, 'r')
			value = str(file_handle.readline())
			file_handle.close()
			return int(value)
		else:
			logging.debug("Creating new oss file [" + self.oss_file + "].")
			self.set_local(0)
			return 0

	def set_local(self, value):
		file_handle = open(self.oss_file, 'w')
		file_handle.write(str(value))
		file_handle.close

class Replica(OsyncDirectoryStructure):
	"""Contains all replica information"""
	def __init__(self, type, uri):
		if type != INITIATOR_TYPE and type != TARGET_TYPE:
			logging.critical("Invalid replica type [type].")
		elif type == INITIATOR_TYPE and uri.startswith("ssh://"):
			logging.critical("Initiator replica must be local.")
		else:
			self.type = type

		if uri.startswith("ssh://"):
			hosturiandpath = uri[6:]
			if '@' in hosturiandpath:
				hosturiandpath = hosturiandpath.split('@',1)
				self.remoteuser = hosturiandpath[0]
				hosturiandpath = hosturiandpath[1]
			else:
				self.remoteuser = getpass.getuser()
			hosturi = hosturiandpath.split('/',1)[0]
			self.path = hosturiandpath.split('/',1)[1]
			if ':' in hosturi:
				hosturi = hosturi.split(':',1)
				self.remotehost = hosturi[0]
				self.remoteport = hosturi[1]
			else:
				self.remoteport = 22
				self.remotehost = hosturi
		else:
			if os.path.isdir(uri):
				self.path = uri
			else:
				logging.critical("Path [" + uri + "] doesn't exist.")

		# Add ending slash to replica path and expanding user ~
		self.path = os.path.expanduser(os.path.normpath(self.path) + os.sep)
		logging.info("Initiated replica " + self.path)
		self.osync_dir = OsyncDirectoryStructure.osync_dir
		self.state_dir = self.osync_dir + os.sep + OsyncDirectoryStructure.state_dir
		self.backup_dir = self.osync_dir + os.sep + OsyncDirectoryStructure.backup_dir
		self.delete_dir = self.osync_dir + os.sep + OsyncDirectoryStructure.delete_dir
		self.partial_dir = self.osync_dir + OsyncDirectoryStructure.partial_dir
		self.last_action_file = self.path + self.osync_dir + os.sep + OsyncDirectoryStructure.last_action_file
		self.resume_count_file = self.path + self.osync_dir + os.sep + OsyncDirectoryStructure.resume_count_file
		self.oss_file = self.path + self.osync_dir + os.sep + OsyncDirectoryStructure.oss_file

		self.deleted_list_file = self.path + self.state_dir + os.sep + OsyncDirectoryStructure.deleted_list_file
		self.moved_list_file = self.path + self.state_dir + os.sep + OsyncDirectoryStructure.moved_list_file
		self.modded_list_file = self.path + self.state_dir + os.sep + OsyncDirectoryStructure.modded_list_file
		self.created_list_file = self.path + self.state_dir + os.sep + OsyncDirectoryStructure.created_list_file

		if self.type == INITIATOR_TYPE:
			self.checkStateDir()
			self.oss_handler = OsyncStateSerial(self.oss_file)
			self.oss = self.oss_handler.get_local()

	def checkStateDir(self):
		"""Create local state dir if not exists"""
		if not os.path.isdir(self.path + self.state_dir):
			#TODO os.makedirs is python 3.2+, replace by lower req ?
			os.makedirs(self.path + self.state_dir)

	def increaseOss(self):
		self.oss = self.oss + 1
		self.oss_handler.set_local(self.oss)

#class CheckDiskSpace

class CompareClocks():
	"""Be sure local and remote systems use the same clock"""

	def __init__(self, target):
		self.target = target

class LockFiles():
	"""Handling local and remote lock files"""

	def __init__(self, target):
		self.target = target

	def checkLocalLock():
		pass
	def checkRemoteLock():
		pass
	def lockLocal():
		pass
	def lockRemote():
		pass
	def unlockLocal():
		pass
	def unlockRemote():
		pass

class RemoteSSHWorker():
	"""Handling remote commands"""

	def __init__(self, target, command):
		self.target = target
		self.command = command

	def checkRemoteOsyncProcess():
		pass
	def executeRemoteCommand():
		pass

class OsyncStateHandler(watchdog.events.PatternMatchingEventHandler):
	"""Writes state files"""

	def __init__(self, replica):
		self.replica = replica
		self.ignore = list()
		self.ignore.append(self.replica.path + self.replica.osync_dir + "*")
		self.ignoreevents = list()
		watchdog.events.PatternMatchingEventHandler.__init__(self, ignore_patterns=self.ignore)
		self.del_file_handler = open(replica.deleted_list_file, 'a')
		self.move_file_handler = open(replica.moved_list_file, 'a')
		self.mod_file_handler = open(replica.modded_list_file, 'a')
		self.create_file_handler = open(replica.created_list_file, 'a')

	def __del__(self):
		self.del_file_handler.close()

	def on_modified(self, event):
		print(event.event_type)
		print(event.key)
		if (event.src_path == self.replica.path):
			return
		if (event.src_path in self.ignoreevents):
			self.ignoreevents.remove(event.src_path)
			return

		# Fix for Rsync: update mtime with ctime so rsync will aknowldge attr changes (chmod / setfacl only change ctime)
		if (CONFIG['RSYNC_OPTIONS']['sync_attrs'].lower() == "yes"):
			# Precision of ctime only works in Python 3+
			ctime = os.path.getctime(event.src_path)
			os.utime(event.src_path, (ctime, ctime))
			self.ignoreevents.append(event.src_path)
		self.mod_file_handler.write(event.src_path + '\n')
		self.mod_file_handler.flush()
		self.replica.increaseOss()

	def on_created(self, event):
		self.create_file_handler.write(event.src_path + '\n')
		self.create_file_handler.flush()
		self.replica.increaseOss()

	def on_moved(self, event):
		self.move_file_handler.write(event.src_path + ' ---osync-to--- ' + event.dest_path + '\n')
		self.move_file_handler.flush()
		self.replica.increaseOss()

	def on_deleted(self, event):
		self.del_file_handler.write(event.src_path + '\n')
		self.del_file_handler.flush()
		self.replica.increaseOss()

def loadConfigFile(configfile):
	"""Loads a config file"""

	global CONFIG

	if not os.path.exists(configfile):
		logging.critical("Config file [" + configfile + "] does not exist.")
		sys.exit(1)
	CONFIG = configparser.ConfigParser()
	CONFIG.sections()
	CONFIG.read(configfile)

def loadDefaultConfig():
	pass

def usage():
	if (IS_STABLE != "yes"):
		print("This is an unstable dev build. Please use with caution.")
	print(PROGRAM + " " + PROGRAM_VERSION + " " + str(PROGRAM_BUILD))
	print(AUTHOR)
	print(CONTACT)
	print("\n")
	print("osync2.py needs a configuration file in order to work.")
	print("Usage: osync2.py -c /path/to/config/file [OPTIONS]")
	print("Usage: osync2.py --config-file=/path/to/config/file [OPTIONS]")
	print("\n")
	print("[OPTIONS]")
	print("--dry		Will run osync withouht actually doing anything; just testing")
	print("--silent		No output to stdout, default mode for daemon running")
	print("--verbose	Increases output")
	sys.exit(1)

def main(argv):
	global INITREPLICA
	global TARGETREPLICA

	if len(argv) == 0:
		logging.critical(os.path.basename(__file__) + " cannot be launched without arguments.")
		usage()
	try:
		opts, args = getopt.getopt(argv, "h?c:")
	except getopt.GetoptError:
		usage()
	for opt, arg in opts:
		if opt == '-h':
			usage()
		if opt == '-c' or opt == '--config-file=':
			configFile=arg
		if opt == '--initiator=':
			initiator=arg
		if opt == '--target=':
			target=arg



	try:
		configFile
	except:
		loadDefaultConfig()
	else:
		loadConfigFile(configFile)



	INITREPLICA = Replica(INITIATOR_TYPE, CONFIG['REPLICAS'][INITIATOR_TYPE])
	TARGETREPLICA = list()
	for target in CONFIG['REPLICAS'][TARGET_TYPE].splitlines():
		TARGETREPLICA.append(Replica(TARGET_TYPE, target))


	print("Running for " + str(len(TARGETREPLICA)) + " targets")

	fs_event_handler = OsyncStateHandler(INITREPLICA)
	fs_observer = watchdog.observers.Observer()
	fs_observer.schedule(fs_event_handler, INITREPLICA.path, recursive=True)

	#TODO: thread this
	fs_observer.start()
	try:
		while True:
			time.sleep(2)
	except KeyboardInterrupt:
		fs_observer.stop()
	fs_observer.join()


if __name__ == "__main__":
	main(sys.argv[1:])
