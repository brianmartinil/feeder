#!/usr/bin/python

import feedparser
from time import mktime, gmtime
from datetime import datetime
import pytz
import smtplib
import sys
import yaml

# Load config from yaml file
configfile = sys.argv[1]
config = yaml.load(open(configfile))

me = config['email']['address']
pw = config['email']['password']
smtp = config['email']['smtp']
subject = config['email']['subject']
homeTZ = pytz.timezone(config['timezone'])
utc = pytz.utc

# Convert post date and time from UTC to home time zone.
def convertTZ(struct):
	dt = datetime.fromtimestamp(mktime(struct))
	return utc.localize(dt).astimezone(homeTZ)

mailfmt = '''\
From: {0}
To: {1}
Subject: {2}
Content-Type: text/html

{3}'''

feedfmt = '''\
<h1>{0}</h1>
{1}
'''

itemfmt = '''\
<p>
	<a href={2}>{0}</a><br />
	by {1} on {3}
</p>
'''

errorfmt = '''
<p>
	<b>Error for {0}: </b><pre>{1}</pre>
</p>
'''

nonewitems = '''\
<p>No new items at this time.</p>
'''

output = ''
errors = ''
newitems = 0

for sub in config['feeds']:
	feed = sub['url']

	if 'newest' not in sub:
		sub['newest'] = 'none'

	lastlink = sub['newest']

	try:
		f = feedparser.parse(feed)

		if 'version' not in f:
			errors += errorfmt.format(feed, "Error loading feed.")

		if len(f.entries) == 0:
			sub['newest'] = 'none'
			continue;

		feedname = f.feed.get('title', 'Untitled Feed').encode('utf8')
		items = ''

		sub['newest'] = f.entries[0].link.encode('utf8')

		for entry in f.entries:
			link = entry.link

			if link == lastlink:
				break
			else:
				title = entry.get('title', 'No Title').encode('utf8')
				author = entry.get('author', 'No Author').encode('utf8')
				date = entry.get('updated_parsed', gmtime())
				date = convertTZ(date).strftime('%B %d at %I:%M %p').encode('utf8')
				items += itemfmt.format(title, author, link, date)
				newitems += 1

		if items != '':
			# Take the collected items and add them to the output
			output += feedfmt.format(feedname, items)
	except:
		# rewind the feed to the original lastlink
		sub['newest'] = lastlink.encode('utf8')
		# put something in the email so maybe we can debug?
		errors += errorfmt.format(feed, sys.exc_info()[0])


if newitems == 0:
	output += nonewitems

output += errors

try:
	# send
	server = smtplib.SMTP(smtp)
	server.starttls()
	server.login(me, pw)

	mail = mailfmt.format(me, me, subject, output)

	server.sendmail(me, [me], mail)
	server.quit()
except:
	# If sending the email fails, quit before updating the read feeds
	sys.exit(1)

with open(configfile, 'w') as subs:
	subs.write(yaml.dump(config, default_flow_style=False))
