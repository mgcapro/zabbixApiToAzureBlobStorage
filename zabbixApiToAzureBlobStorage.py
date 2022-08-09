#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import datetime

# Get dates 
timeFrom = datetime.datetime.now() - datetime.timedelta(minutes=30)
timeTill = datetime.datetime.now()

# Convert dates to epoch time
epochFrom = int(round(datetime.datetime.timestamp(timeFrom)))
epochTill = int(round(datetime.datetime.timestamp(timeTill)))

# Create a local directory to hold blob data
local_path = os.getcwd()

# Get the Storage Connection String
blob_service_client = BlobServiceClient.from_connection_string("STORAGE ACCOUNT STRING HERE")

# Container name must match with an existing one
container_name = "zabbix"

# List of zabbix items id to gather (each one is linked to a regions variable, first is ozzabbix, second brzabbix etc)
itemsids = ["29892","29169","29378","29518","29765","29339","30094"]

# Incremental variable of itemsids 
itemsidsrank = 0

# Suffix url of zabbix API 
regions = ["ozzabbix", "brzabbix", "cazabbix", "chazabbix", "frazabbix", "nlzabbix", "uszabbix"]
for x in regions: 
  url = 'https://zabbixurl.com/'+ str(x) + '/api_jsonrpc.php'
  r = requests.post(url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "user.login",
                        "params": {
                            "user": "Admin",
                            "password": "zabbix"},
                        "id": 1
                    }, verify = False)
  AUTHTOKEN = r.json()["result"]
  numberOfActiveAgents = {
    "jsonrpc": "2.0",
    "method": "history.get",
    "params": {
      "output": "extend",
      "history": "0",
      "itemids": [
        itemsids[itemsidsrank]
    ],
    "sortfield": "clock",
    "sortorder": "ASC",
    "time_from": epochFrom,
    "time_till": epochTill
},
"id": 1,
"auth": str(AUTHTOKEN)
}

  numberOfActiveFrameworks = {
      "jsonrpc": "2.0",
      "method": "history.get",
      "params": {
        "output": "extend",
        "history": "0",
        "itemids": [
          itemsids[itemsidsrank]
      ],
      "sortfield": "clock",
      "sortorder": "ASC",
      "time_from": epochFrom,
      "time_till": epochTill
  },
  "id": 1,
  "auth": str(AUTHTOKEN)
  }

  #increment itemsidrank to go to the next one
  itemsidsrank = itemsidsrank + 1

  #Send posts queries
  result1 = requests.post(url, json = numberOfActiveAgents, verify = False)
  result2 = requests.post(url, json = numberOfActiveFrameworks, verify = False)

  # Create a file in the local data directory to upload and download
  local_file_name = x + "-" + str(timeTill) + ".txt"
  upload_file_path = os.path.join(local_path, local_file_name)

  # Write text to the file
  file = open(upload_file_path, 'w')
  file.write(result1.text)
  file.write(result2.text)
  file.close()

  # Create a blob client using the local file name as the name for the blob
  blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

  # Upload the created file
  print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)
  with open(upload_file_path, "rb") as data:
      blob_client.upload_blob(data)
  
  # Delete local log file
  files_in_directory = os.listdir(local_path)
  filtered_files = [file for file in files_in_directory if file.endswith(".txt")]
  for file in filtered_files:
      path_to_file = os.path.join(local_path, file)
      os.remove(path_to_file)

