#!/usr/bin/python

import feedparser
from time import mktime, gmtime
from datetime import datetime
import pytz
import smtplib
import sys

me = 'your_email_address_here'
pw = 'your_email_password_here'
gmail = 'smtp.gmail.com:587'
subject = 'Your RSS feed update'
homeTZ = pytz.timezone('US/Central')
utc = pytz.utc
subfile = sys.argv[1]

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

subdict = {}
output = ''
errors = ''
newitems = 0

with open(subfile) as subs:
	for sub in subs:
		feed, lastlink = sub.split()
		subdict[feed] = lastlink

		try:
			f = feedparser.parse(feed)

			if 'version' not in f:
				errors += errorfmt.format(feed, "Error loading feed.")

			if len(f.entries) == 0:
				subdict[feed] = 'none'
				continue;

			feedname = f.feed.get('title', 'Untitled Feed').encode('utf8')
			items = ''

			subdict[feed] = f.entries[0].link

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
			subdict[feed] = lastlink
			# put something in the email so maybe we can debug?
			errors += errorfmt.format(feed, sys.exc_info()[0])


if newitems == 0:
	output += nonewitems

output += errors

try:
	# send
	server = smtplib.SMTP(gmail)
	server.starttls()
	server.login(me, pw)

	mail = mailfmt.format(me, me, subject, output)

	server.sendmail(me, [me], mail)
	server.quit()
except:
	# If sending the email fails, quit before updating the read feeds
	sys.exit(1)

with open(subfile, 'w') as subs:
	for k, v in subdict.iteritems():
		subs.write('%s %s\n' % (k,v) )
