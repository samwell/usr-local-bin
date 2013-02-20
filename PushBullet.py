#!/usr/bin/python2
import ConfigParser, urllib, urllib2, json, argparse, logging

config = ConfigParser.RawConfigParser()
config.read('scripts.cfg')

Log_Location = config.get('PushBullet', 'log_location')

logging.basicConfig(format='[%(asctime)s | %(levelname)s]  - %(message)s', level=logging.INFO, filename=Log_Location, filemode='a')

API_KEY = config.get('PushBullet', 'api_key')
auth = "Basic " + (API_KEY).encode("base64").rstrip()

"""
Generates a list of devices which the API Key has access to.

Returns a dictionary of all devices { [device owner]:[device id] }
"""
def getDeviceID():
   global auth

   req = urllib2.Request('https://www.pushbullet.com/api/devices')
   req.add_header('Accept', 'application/json')
   req.add_header('Content-type', 'application/x-www-form-urlencoded')
   req.add_header('Authorization', auth)

   try:
      res = urllib2.urlopen(req)
   except urllib2.URLError, e:
      message = ""
      
      if e.code == 400:
         message = "Pretty sure a parameter was missing: " + str(e.code)
      elif e.code == 401:
         message = "No valid API key was provided: " + str(e.code)
      elif e.code == 402:
         message = "Request was correct, but failed: " + str(e.code)
      elif e.code == 403:
         message = "Invalid API key: " + str(e.code)
      elif e.code == 404:
         message = "Requested item doesn't exist: " + str(e.code)
      else: 
         message = "Unknown status code recieved: " + str(e.code)
      
      logging.critical("Error in retriving devices. " + message)
      exit(message)         
   except Exception, e:
      logging.critical("Error sending to " + str(data['id']))
      exit("Error sending to " + str(data['id']))

   devices = json.loads(res.read())
   devices = devices['shared_devices'] + devices['devices']

   ids = {}

   for device in devices:
      ids[device['ownerName']] = device['id']
      
   logging.info("Looking for available devices. Found: " + str(ids))

   return ids

"""
Send a message to a device by putting the title, message, and id in a dictionary.

data { 
   'title': [title you want to send], 
   'message': [message you want to send],
   'id': [id of which device you want to send to]
}
"""
def send(data):
   global auth
   reqData = {'type':'note', 'title' : data['title'], 'body' : data['message'], 'device_id' : str(data['id'])}

   req = urllib2.Request('https://www.pushbullet.com/api/pushes')
   req.add_header('Accept', 'application/json')
   req.add_header('Content-type', 'application/x-www-form-urlencoded')
   req.add_header('Authorization', auth)
   req.add_data(urllib.urlencode(reqData))

   try:
      res = urllib2.urlopen(req)
      if res.getcode() == 200:
         message = "Title: " + data['title']
         message += "\nMessage: " + data['message']
         message += "\nID: " + str(data['id'])
      
         logging.info("Sent message successfully\n" + message)
   except urllib2.URLError, e:
      message = ""
      
      if e.code == 400:
         message = "Pretty sure a parameter was missing: " + str(e.code)
      elif e.code == 401:
         message = "No valid API key was provided: " + str(e.code)
      elif e.code == 402:
         message = "Request was correct, but failed: " + str(e.code)
      elif e.code == 403:
         message = "Invalid API key: " + str(e.code)
      elif e.code == 404:
         message = "Requested item doesn't exist: " + str(e.code)
      else:
         message = "Unknown status code recieved: " + str(e.code)
      
      message += "\nTitle: " + data['title']
      message += "\nMessage: " + data['message']
      message += "\nID: " + str(data['id'])
      
      logging.critical(message)
      exit(message)         
   except Exception, e:
      logging.critical("Error sending to " + str(data['id']))
      exit("Error sending to " + str(data['id']))
   
def getIds(devices):
   ids = []
   for device, id in devices.iteritems():
      ids.append(id)
      
   return ids

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Send PushBullet note')
   parser.add_argument('-a', '--all', help='Send message to all devices', action='store_true')
   parser.add_argument('-i', '--id', action='append', help='The device id which the message is to be sent to')
   parser.add_argument('-t', '--title', help='The title of the note to be sent', required=True)
   parser.add_argument('-m', '--message', help='The message of the note to be sent', required=True)
   
   args = parser.parse_args()
   ids = []
   
   if args.all and args.id != None:
      all = getIds(getDeviceID())
      ids = all + args.id
   elif args.all and args.id == None:
      all = getIds(getDeviceID())
      ids = all
   else:
      ids = args.id
      
   for id in ids:
      data = {'id':id, 'title':args.title, 'message':args.message} 
      send(data)
