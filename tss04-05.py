#!/usr/bin/python3
# find tss04 errors in GA engine, php backend.
# simple auth endpoint

import requests, json,psycopg2,re, difflib
from requests.auth import HTTPBasicAuth
from datetime import datetime

def stats_by_esp(senddbid, status, domain):
  endpoint = 'ENDPOINT'
  payload = {"api": "json", "senddbid": ""+senddbid+"", "status": ""+status+"", "domain": ""+domain+""}
  headers = {'content-type': 'application/json'}  
  response = requests.post(endpoint,auth=('USER', 'PASS'), params=payload)
  data = json.loads(response.text)['messages']
  return data

def get_senddbid():
  try:
    con = psycopg2.connect(host="HOST", port = PORT, database="DATABASE", user="USER", password="PASS")
    cursor = con.cursor()
    cursor.execute("""SELECT   max(send_id), listid
                      FROM     sends_lists 
                      WHERE    send_id IN (
                        SELECT id
                        FROM   sends 
                        WHERE  to_char(to_timestamp(injtime_first), 'yyyymmdd')  > to_char((current_date - INTERVAL '1 day')::date, 'yyyymmdd'))
                      GROUP BY listid""")

    records = cursor.fetchall()
    return records

  except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

  finally:
    if(con):
      cursor.close()
      con.close()

def slack_api(text):
  webhook_url = "SLACK_URL"
  slack_text = {'text': "```"+text+"```"}
  response = requests.post(webhook_url, data=json.dumps(slack_text),
    headers={'Content-Type': 'application/json'})
  if response.status_code != 200:
    raise ValueError('Post to slack error %d\n' % (response.status_code))

def main():
  tss04=""
  tss05=""

  for i in get_senddbid():
    try:
      value = stats_by_esp(str(i[0]), 'deferral', 'yahoo.com')
      for val in value:
        if val:
          if re.findall(r'TSS05', val['message']):
            tss05 += str(i[1] + ": " + str(val['message_count']) + '\n')
          if re.findall(r'TSS04', val['message']):
            tss04 += str(i[1] + ": " + str(val['message_count']) + '\n')
    except KeyError:
      pass
  if tss04:
    slack_api("TSS04 errors:\n" + tss04)
  if tss05:
    slack_api("TSS05 errors:\n" + tss05)

if __name__ == "__main__":
  main()
