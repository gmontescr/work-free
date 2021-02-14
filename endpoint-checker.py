#!/usr/bin/python3
# install dependencies: gspread, oauth2client
# create google api credentials.
# create a spreadsheet in google drive with urls, just one column.

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials


def getData():
  scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
  credentials = ServiceAccountCredentials.from_json_keyfile_name("APPLICATION_NAME.json", scope)
  client = gspread.authorize(credentials)
  sheet = client.open("NAME_SHEET").sheet1
  return sheet.get_all_values()

def get_status_code(url):
  try:
    response = requests.get(url)
    if len(response.history) > 0:
      return response.history[0].status_code
    else:
      return response.status_code
  except (requests.exceptions.MissingSchema, requests.ConnectionError) as error:
    return '0'
  
def to_slack(slackText):
  endpoint = "webhook-endpoint"
  slack_data = {'text': ""+slackText+""}
  response = requests.post(endpoint, data=json.dumps(slack_data), 
                           headers={'Content-Type': 'application/json'})

  if response.status_code != 200:
    return 'Post to slack error %d\n' % (response.status_code)
  return response

def main():
  data = getData()
  code = get_status_code(*data[i])
 
  for i in range(1, len(data)):
    code = get_status_code(*data[i])
    if code not in {200,301,302}:
      slackText += str(*data[i]) + '\n' 
  print(to_slack(slackText))

if __name__ == "__main__":
  main()
