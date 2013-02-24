#!/usr/bin/python2
import LogUncaught, ConfigParser, logging, PushBullet, os
from time import localtime, strftime

sbConfig = ConfigParser.RawConfigParser()
sbConfig.read('scripts.cfg')

# Logger File Handler
sbLFH = logging.FileHandler(sbConfig.get('ServerBackup', 'log_location'))
sbLFH.setLevel(logging.DEBUG)

# Logger Formatter
sbLFORMAT = logging.Formatter('[%(asctime)s | %(levelname)s] - %(message)s')
sbLFH.setFormatter(sbLFORMAT)

# Logger
sbLogger = logging.getLogger("serverbackup_logger")
sbLogger.setLevel(logging.DEBUG)
sbLogger.addHandler(sbLFH)

sbLogger.info("Script has begun")

sbLocation = sbConfig.get('ServerBackup', 'backup_location')
databasePass = sbConfig.get('Database', 'password')
lbLocation = sbConfig.get('LogBackup', 'backup_location')
date = strftime("%m_%d_%Y_%H_%M_%S", localtime())
sbFolder = sbLocation + "backup_" + date + "/"

os.makedirs(sbFolder)

if not os.path.exists(sbFolder):
   message = "Folder, \"%s\", couldn't be made" % sbFolder
   sbLogger.critical(message)
   PushBullet.sendPushNote({'id':PushBullet.getPushDevicesIds(), 'title':"Server Backup Error", 'message':message})
   exit(message)