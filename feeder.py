#!/usr/bin/python

from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
import pystache
import pytz
import smtplib
import sys
from time import mktime, gmtime
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

template = '''\
{{#feeds}}
	<h1>{{feed}}</h1>
	{{#article}}
		<p>
			<a href="{{link}}">{{title}}</a><br />
			by {{author}} on {{date}}
		</p>
	{{/article}}
{{/feeds}}

{{^feeds}}
	<p>No new items at this time.</p>
{{/feeds}}

{{#errors}}
	<p>
		<b>Error for {{feed}}: </b><pre>{{error}}</pre>
	</p>
{{/errors}}
'''

data = {'errors': [], 'feeds': []}

for sub in config['feeds']:
	feed = sub['url']

	if 'newest' not in sub:
		sub['newest'] = 'none'

	lastlink = sub['newest']

	try:
		f = feedparser.parse(feed)

		if 'version' not in f:
			data['errors'].append({'feed': feed, 'error': "Error loading feed."})

		if not f.entries:
			sub['newest'] = 'none'
			continue;

		feedname = f.feed.get('title', 'Untitled Feed').encode('utf8')
		items = []

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
				items.append({'link': link, 'title': title, 'author': author , 'date': date})

		if items:
			# Take the collected items and add them to the output
			data['feeds'].append({'feed': feedname, 'article': items})
	except exc:
		# rewind the feed to the original lastlink
		sub['newest'] = lastlink.encode('utf8')
		# put something in the email so maybe we can debug?
		data['errors'].append({'feed': feed, 'error': exc})

try:
	# send
	server = smtplib.SMTP(smtp)
	server.starttls()
	server.login(me, pw)

	# Jump through the MIME hoops to make Unicode work right
	mail = MIMEMultipart('alternative')
	mail['Subject'] = Header(subject, 'utf-8')
	mail['From'] = Header(me, 'utf-8')
	mail['To'] = Header(me, 'utf-8')

	renderer = pystache.Renderer(string_encoding='utf8')
	body = renderer.render(template, data)
	html_text = MIMEText(body, 'html', 'utf-8')

	mail.attach(html_text)

	server.sendmail(me, [me], mail.as_string())
	server.quit()
except:
	# If sending the email fails, quit before updating the read feeds
	sys.exit(1)

with open(configfile, 'w') as subs:
	subs.write(yaml.dump(config, default_flow_style=False))
