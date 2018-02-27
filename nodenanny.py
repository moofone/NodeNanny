#!/usr/bin/env python3

## NodeNanny v.002
# See README.md for instructions

from webcord import Webhook
import socket
import subprocess
import json
import requests

## Node Configuration -- CHANGE THIS #######
nodecmd = "coin2fly-cli"
nodename = "CTF-001"
tx = "1c5d17314391b4ffcf68daca7d7b6dde9b49"
webhook_url="https://discordapp.com/api/webhooks/..."
blockchain_api="http://explorer.coin2fly.com/api/"
blockchain_maxdrift = 5
######################

DEBUG=False
TEST=False

def send_message(msg):
    webhook = Webhook(webhook_url, avatar_url=None)
    webhook.send_message(msg, "NodeNanny", avatar_url=None)
    return

def blockchain_compare(blockcount, apiblockcount):
    if (TEST):
        blockcount = blockcount - 1

    output_str = "[**" + nodename + "**] (_Test_) Local BlockCount: **" + str(blockcount) + "** API BlockCount: **" + str(apiblockcount) + "**"
    diff = abs(apiblockcount - blockcount)

    if (blockcount != apiblockcount and diff >= blockchain_maxdrift):
        output_str = "[**" + nodename + "**] [**WARNING**] Local BlockCount: **" + str(blockcount) + "** API BlockCount: **" + str(apiblockcount) + "**"
        send_message(output_str)
    if (DEBUG):
        send_message(output_str)
    return


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02dh:%02dm:%02ds' % (hours, mins, secs)


# check blockchain api latest block vs coin2fly-cli getblockcount
cmd = subprocess.Popen([nodecmd, "getblockcount"], stdout=subprocess.PIPE)
blockcount=int(cmd.communicate()[0])
print(blockcount)

body = {}

headers = {
'Accept': 'application/json'
}

r = requests.get(blockchain_api + '/getblockcount', headers=headers, json=body)
apiblockcount = int(r.text)
# todo handle api errors

blockchain_compare(blockcount, apiblockcount)

# main (todo: refactor)
cmd = subprocess.Popen([nodecmd, "masternode", "list", "full", tx], stdout=subprocess.PIPE)
lines = cmd.communicate()

tokens=','.join(map(str,lines)).split(" ")
tokens = list(filter(None, tokens))
status = tokens[3]
uptime=int(tokens[7])
activedatetime = humanize_time(uptime)

#print(activedatetime)

good = 0
if (status == "ENABLED"):
	if (uptime < 1):
		output_str = "[**" + nodename + "**] Active Time: **" + activedatetime + "** Status: **ENABLED**"
	else:
		good=1
		output_str = "[**" + nodename + "**] (_Test_) Active Time: **" + activedatetime + "** Status: **" + status + "**"
else:
	output_str = "[**" + nodename + "**] [**WARNING**] Status: **" + status + "**"

webhook = Webhook(webhook_url, avatar_url=None)

if (good != 1):
	webhook.send_message(output_str, "NodeNanny", avatar_url=None)
