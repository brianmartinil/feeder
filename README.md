# feeder
Super simple RSS reader.  Given a file of RSS or Atom feeds, sends an email with links to new articles.

This is a modified version of [Dr. Drang's RSS aggregator](http://leancrew.com/all-this/2015/12/homemade-rss-aggregator-followup/).  I only wanted a twice daily email of links to new articles, rather than individual emails containing the contents of each article.

## Installation

`pip install feedparser pytz pyyaml`

Edit config.yml to have the values match your email account and feeds.

## Usage
`python feeder.py config.yml`

## TODO
Nothing, it works fine for me.  Maybe use a real template language for the email template?
