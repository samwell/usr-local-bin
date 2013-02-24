#!/usr/bin/python2
import LogUncaught, ConfigParser, logging, os

sbConfig = ConfigParser.RawConfigParser()
sbConfig.read('scripts.cfg')

# Logger File Handler
sbLFH = logging.FileHandler(sbConfig.get('ServerBackup', 'log_location'))
sbLFH.setLevel(logging.DEBUG)

# Logger Formatter
sbLFORMAT = logging.Formatter('[%(asctime)s | %(levelname)s]  - %(message)s')
sbLFH.setFormatter(sbLFORMAT)

# Logger
sbLogger = logging.getLogger("serverbackup_logger")
sbLogger.setLevel(logging.DEBUG)
sbLogger.addHandler(sbLFH)

sbLogger.info("Script has begun")

sbLocation = sbConfig.get('ServerBackup', 'backup_location')
databasePass = sbConfig.get('Database', 'password')
lbLocation = sbConfig.get('LogBackup', 'backup_location')


