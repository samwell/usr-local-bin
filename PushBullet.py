#!/usr/bin/python2
import LogUncaught, ConfigParser, urllib, urllib2, json, argparse, logging

pushConfig = ConfigParser.RawConfigParser()
pushConfig.read('scripts.cfg')

API_KEY = pushConfig.get('PushBullet', 'api_key')
auth = "Basic " + (API_KEY).encode("base64").rstrip()

# Logger File Handler
pushLFH = logging.FileHandler(pushConfig.get('PushBullet', 'log_location'))
pushLFH.setLevel(logging.DEBUG)

# Logger Formatter
pushLFORMAT = logging.Formatter('[%(asctime)s | %(levelname)s]  - %(message)s')
pushLFH.setFormatter(pushLFORMAT)

# Logger
pushLogger = logging.getLogger("pushbullet_logger")
pushLogger.setLevel(logging.DEBUG)
pushLogger.addHandler(pushLFH)

"""
Generates a list of devices which the API Key has access to.

Returns a dictionary of all devices { [device owner]:[device id] }
"""
def getPushDevices():
   global auth

   req = urllib2.Request('https://www.pushbullet.com/api/devices')
   req.add_header('Authorization', auth)

   res = sendPushRequest(req, "Retriving Devices")

   devices = json.loads(res.read())
   devices = devices['shared_devices'] + devices['devices']

   ids = {}

   for device in devices:
      ids[device['owner_name']] = device['id']
      
   pushLogger.info("Looking for available devices. Found: " + str(ids))

   return ids

"""
Send a message to a device by putting the title, message, and id in a dictionary.

data { 
   'title': [title you want to send], 
   'message': [message you want to send],
   'id': [list of id(s) of which device(s) you want to send to]
}
"""
def sendPushNote(data):
   global auth

   for id in data['id']:
      reqData = {'type':'note', 'title' : data['title'], 'body' : data['message'], 'device_id' : str(id)}

      req = urllib2.Request('https://www.pushbullet.com/api/pushes')
      req.add_header('Authorization', auth)
      req.add_data(urllib.urlencode(reqData))

      message = "Sending Message\nTitle: " + data['title']
      message += "\nMessage: " + data['message']
      message += "\nID: " + str(id)

      sendPushRequest(req, message)
      
"""
Sends requests and handles all status codes.

request - A Request Object
message - A String

Returns: A file Object
"""
def sendPushRequest(request, message):
   try:
      res = urllib2.urlopen(request)
      if res.getcode() == 200:      
         pushLogger.info("Successful Request\nRequest: " + message)
         return res
   except urllib2.URLError, e:
      if e.code == 400:
         errMessage = "Pretty sure a parameter was missing. Error Code: " + str(e.code)
      elif e.code == 401:
         errMessage = "No valid API key was provided. Error Code: " + str(e.code)
      elif e.code == 402:
         errMessage = "Request was correct, but failed. Error Code: " + str(e.code)
      elif e.code == 403:
         errMessage = "Invalid API key. Error Code: " + str(e.code)
      elif e.code == 404:
         errMessage = "Requested item doesn't exist. Error Code: " + str(e.code)
      else:
         errMessage = "Unknown status code recieved. Error Code: " + str(e.code)
         
      pushLogger.critical(errMessage + "\nRequest: " + message)
      exit(errMessage + "\nRequest: " + message)         
   except Exception, e:
      pushLogger.critical("Error when making a request\nRequest: " + message)
      pushLogger.critical(e)
      exit("Error when making a request\nRequest: " + message)
   
def getIds(devices):
   ids = []
   for device, id in devices.iteritems():
      ids.append(id)
      
   return ids

def getPushDevicesIds():
   return getIds(getPushDevices())

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Send PushBullet note')
   parser.add_argument('-l', '--list', help='List all devices', action='store_true')
   parser.add_argument('-a', '--all', help='Send message to all devices', action='store_true')
   parser.add_argument('-i', '--id', action='append', default=[], help='The device id or email address associated with the device, which the message is to be sent to')
   parser.add_argument('-t', '--title', help='The title of the note to be sent')
   parser.add_argument('-m', '--message', help='The message of the note to be sent')

   args = parser.parse_args()
   devices = getPushDevices()
   
   if args.list:
      for email, id in devices.iteritems():
         print email, ":", id
         
      exit()
      
   if args.title == None:
      exit("Title must be specified")
   if args.message == None:
      exit("Message must be specified")

   all = getIds(devices)
   ids = []
   
   if args.all and args.id != None:
      ids = all + args.id
   elif args.all and args.id == None:
      ids = all

   for id in args.id:
      if (id in devices) and (devices[id] not in ids):
         ids.append(devices[id])
      elif (id not in devices) and int(id) not in ids:
         ids.append(id)
      else:
         print "Duplicate device id:", id
         pushLogger.info("Duplicate device id was entered, skipped this id: " + id)
      
   sendPushNote({'id':ids, 'title':args.title, 'message':args.message})
