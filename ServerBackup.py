#!/usr/bin/python2
import LogUncaught, ConfigParser, logging, PushBullet, os, time, traceback, tarfile, json, shutil, MySQLdb as mdb
from time import localtime, strftime
from hurry.filesize import size
from boto.s3.connection import S3Connection
from boto.s3.key import Key

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

sbLocation = sbConfig.get('ServerBackup', 'backup_location')
filesToBackup = json.loads(sbConfig.get('ServerBackup', 'files_to_backup'))
databasePass = sbConfig.get('Database', 'password')
lbLocation = sbConfig.get('LogBackup', 'backup_location')
aws_access_key = sbConfig.get('AWS', 'access_key')
aws_secret_key = sbConfig.get('AWS', 'secret_key')
aws_bucket_name = sbConfig.get('AWS', 'bucket_name')
date = strftime("%m_%d_%Y_%H_%M_%S", localtime())
sbFolder = sbLocation + "backup_" + date + "/"
sqlDumpName = sbFolder + "backup_sql_" + date + ".sql"

def sendPush(title, message):
   PushBullet.sendPushNote({'id':PushBullet.getPushDevicesIds(), 'title':title, 'message':message})

def logCritical(message, exception):
   sbLogger.critical(message)
   sbLogger.critical(exception)
   sendPush("Server Backup Error", message)
   exit(message)

def mysqlDump():
   try:
      sbLogger.info("Starting MySQL dump")
      startTime = time.time()
      dbConn = mdb.connect('localhost', 'root', databasePass)
      sbLogger.info("Connected to MySQL Server")
      cur = dbConn.cursor()
      sbLogger.info("Putting read lock on tables")
      cur.execute("FLUSH TABLES WITH READ LOCK;")
      sbLogger.info("Taking MySQL dump")
      os.system("mysqldump -uroot -p" + databasePass + " --single-transaction --routines --triggers --all-databases > " + sqlDumpName)
      sbLogger.info("Finished taking MySQL dump")
      cur.execute("UNLOCK TABLES")
      sbLogger.info("Unlocked tables")
      dbConn.close()
      sbLogger.info("Disconnected from MySQL Server")
      endTime = str(time.time() - startTime)
      dumpSize = size(os.path.getsize(sqlDumpName))
      sbLogger.info("Took %s seconds to execute MySQL dump" % endTime)
      sbLogger.info("MySQL dump was %s" % dumpSize)
      sendPush("Server Backup [MySQL Dump]", "MySQL dump was successful, took %s seconds with a dump filesize of %s" % (endTime, dumpSize))
   except Exception, e:
      logCritical("An error occured during MySQL dump", traceback.format_exc())

def makeTar(fileName, whatToTar):
   tar = tarfile.open(fileName, "w:gz")
   tar.add(whatToTar)
   tar.close()

def makeTars():
   sbLogger.info("Making tar.gz backups")
   for name, location in filesToBackup.iteritems():
      sbLogger.info("Making backup of %s" % location)
      startTime = time.time()
      makeTar(sbFolder + "backup_%s_%s.tar.gz" % (name, date), location)
      endTime = time.time() - startTime
      backupSize = size(os.path.getsize(location))
      sbLogger.info("Finished making backup of %s" % location)
      sbLogger.info("Took %s seconds to make backup of %s" % (endTime, location))
      sbLogger.info("Backup of %s was %s" % (location, backupSize))
      
def sendToS3():
   backup_name = "backup_%s.tar.gz" % date
   sbLogger.info("Making %s" % backup_name)
   makeTar(sbLocation + backup_name, sbFolder)
   sbLogger.info("Finished making %s" % backup_name)
   sbLogger.info("Backup size is %s" % size(os.path.getsize(sbLocation + backup_name)))
   sbLogger.info("Making connection to S3")
   conn = S3Connection(aws_access_key, aws_secret_key)
   sbLogger.info("Made connection to S3 successfully")
   bucket = conn.get_bucket(aws_bucket_name)
   k = Key(bucket)
   k.key = backup_name
   sbLogger.info("Sending %s to S3 bucket, %s" % (backup_name, aws_bucket_name))
   k.set_contents_from_filename(sbLocation + backup_name)
   sbLogger.info("Finished sending %s to S3 bucket, %s" % (backup_name, aws_bucket_name))
   sbLogger.info("Removing backup folder, %s" % sbFolder)
   shutil.rmtree(sbFolder)
   if os.path.exists(sbFolder):
      sbLogger.critical("Backup folder, %s,wasn't removed" % sbFolder)
   else:
      sbLogger.info("Backup folder, %s, was removed" % sbFolder)

if __name__ == '__main__':
   sbLogger.info("Backup has begun")
   startTime = time.time()
   os.makedirs(sbFolder)

   if not os.path.exists(sbFolder):
      logCritical("Folder, \"%s\", couldn't be made" % sbFolder)
   
   mysqlDump()
   makeTars()
   sendToS3()
   
   endTime = time.time() - startTime
   sbLogger.info("Backup finished successfully in %s seconds" % endTime)
