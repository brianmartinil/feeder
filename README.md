# feeder
Super simple RSS reader.  Given a file of RSS or Atom feeds, sends an email with links to new articles.

This is a modified version of [Dr. Drang's RSS aggregator](http://leancrew.com/all-this/2015/12/homemade-rss-aggregator-followup/).  I only wanted a twice daily email of links to new articles, rather than individual emails containing the contents of each article.

## Installation

`pip install feedparser pytz`

Edit feeder.py to include your email address, mail server password, mail server, timezone, etc.

Create a text file of feeds.  The format is one feed per line, the feed URL followed by a space followed by the URL of the most recent entry.  Use "none" for the most recent entry of a newly added feed.  See the example feeds.txt in this repo.

## Usage
`python feeder.py feeds.txt`

## TODO
Nothing, it works fine for me.  Other users might appreciate having the configuration moved out of the source code, and maybe making the email template easier to edit.
