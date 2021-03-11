# !/usr/bin/python3
#GoogleBackingStore.py
# uses Google Drive API

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

import BackingStore as Bs

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ('https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets') # allow updates
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Solar Monitor'

class GoogleBackingStore(Bs.BackingStore):
   'This will be the backing store class using Google for the Solar panel package'
   # class variables here

   # Initialisation code
   def __init__(self):
      Bs.BackingStore.__init__(self)
      self.driveService = None
      self.sheetService = None
      self.dir = None
      self.control = None
      self.driveService = self.getDriveService()
      self.sheetService = self.getSheetService()
      print("Created google backing store")
     
   def get_credentials(self):
      """Gets valid user credentials from storage.

      If nothing has been stored, or if the stored credentials are invalid,
      the OAuth2 flow is completed to obtain the new credentials.

      Returns:
           Credentials, the obtained credential.
      """
      home_dir = os.path.expanduser('~')
      credential_dir = os.path.join(home_dir, '.credentials')
      if not os.path.exists(credential_dir):
         os.makedirs(credential_dir)
      credential_path = os.path.join(credential_dir,
                                     'solar-monitor.json')
      # print("credential_path = ", credential_path)

      store = Storage(credential_path)
      credentials = store.get()
      if not credentials or credentials.invalid:
         flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
         flow.user_agent = APPLICATION_NAME
         if flags:
            credentials = tools.run_flow(flow, store, flags)
         else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
         print('Credentials stored in', credential_path)
      return credentials

   def getDriveService(self):
      if not self.driveService:
         credentials = self.get_credentials()
         http = credentials.authorize(httplib2.Http())
         self.driveService = discovery.build('drive', 'v3', http=http)
      return self.driveService

   def getSheetService(self):
      if not self.sheetService:
         credentials = self.get_credentials()
         http = credentials.authorize(httplib2.Http())
         discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                         'version=v4')
         self.sheetService = discovery.build('sheets', 'v4', http=http,
                                             discoveryServiceUrl=discoveryUrl)
      return self.sheetService

   def getDir(self):
      if not self.dir:
         service = self.getDriveService()
         results = service.files().list(pageSize=10,
                                        q="name='Solar'",
                                        fields="nextPageToken, files(id, name, size, parents)").execute()
         items = results.get('files', [])
         if not items:
            raise Exception('No directory Solar found.')
         item = items[0]
         self.dir = item['id']
         print("Solar directory can be found at", self.dir)
      return self.dir

   def findFile(self, fileName):
      service = self.getDriveService()
      results = service.files().list(pageSize=10,
                                     q="name='" + fileName + "' and '" + self.getDir() + "' in parents",
                                     fields="nextPageToken, files(id, name, size, parents)").execute()
      items = results.get('files', [])
      fileId = None
      if items:
         item = items[0]
         fileId = item['id']
      return fileId

   def getControl(self):
      if not self.control:
         self.control = self.findFile("Control")
         if not self.control:
            raise Exception('No file Control found.')
         print("Control file can be found at", self.control)
      return self.control

   def getSpreadsheet(self, fileName, keys):
      spreadsheetId = self.findFile(fileName)
      if not spreadsheetId:
         # not exist, so create it
         service = self.getDriveService()
         file_metadata = {
            'name' : fileName,
            'mimeType' : 'application/vnd.google-apps.spreadsheet',
            'parents': [self.getDir()]
            }
         file = service.files().create(body=file_metadata,
                                       fields='id').execute()
         spreadsheetId = file.get('id')
         # now it exists, we need to head the headings ...
         array = ["Timestamp"]
         for key in keys:
            array.append(key)
         service = self.getSheetService()
         rangeName = 'A1' # table starts at top left corner
         body = {'values': [array]} # just one row
         result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId,
                                                      range=rangeName,
                                                      valueInputOption='RAW',
                                                      body=body).execute()
         print("Started new spreadsheet called", fileName, "and can be found at", spreadsheetId)
      return spreadsheetId
        
   def getProperties(self):
      service = self.getSheetService()
      rangeName = 'A1:B100'
      result = service.spreadsheets().values().get(spreadsheetId=self.getControl(),
                                                   range=rangeName).execute()
      values = result.get('values', [])
      properties = dict(values)
      return properties

   def recordIt(self, key, value):
      # this assumes that the key is always first item!
      keys = [key]
      values ={key: value}
      self.recordAll(keys, values)

   def recordAll(self, keys, values):
      # this assumes that the keys are always in the same order!
      current = datetime.datetime.now()
      today = current.date().isoformat()
      fileName = "Record-" + today # unique file for each day
      spreadsheetId = self.getSpreadsheet(fileName, keys)
      array = [current.strftime("%d/%m/%y %H:%M:%S")] # current time stamp
      for key in keys:
         array.append(values.get(key))

      service = self.getSheetService()
      rangeName = 'A1' # table starts at top left corner
      body = {'values': [array]} # just one row
      result = service.spreadsheets().values().append(spreadsheetId=spreadsheetId,
                                                      range=rangeName,
                                                      valueInputOption='RAW',
                                                      body=body).execute()

def main():
    # This is just for testing
   bs = GoogleBackingStore()
   print("getProperties() returned")
   print(bs.getProperties())
   keys = ["One", "Two", "Three"]
   bs.recordAll(keys, {"One": 1, "Two": 2, "Three": 3})
   bs.recordAll(keys, {"Two": 5, "Three": 6})
   bs.recordAll(keys, {"This": 6, "That": 5, "The Other": 4, "One": 9})
   bs.recordIt("Four", 9)

if __name__ == '__main__':
    main()
