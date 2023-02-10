#!/bin/bash

# This is an example script for using feeder and syncing the 
# config file to GitHub.  It makes certain assumptions, mainly
# that your config is called 'feeds.yaml' and is in the 
# root of your repo.

CONFIG_DIR=#Directory use to clone github repo
GH_TOKEN_NAME=#You Github personal access token name
GH_TOKEN_VAL=#Your Github personal access token value
GH_ORG=#Your github org
GH_REPO=#Your github repo
GH_BRANCH=#The github branch to use

pushd .

# Set up the directory structure
if [ ! -d $CONFIG_DIR ] ; then
  mkdir -p $CONFIG_DIR
fi

cd $CONFIG_DIR

# Clone the repo if it doesn't exist
if [ ! -d $CONFIG_DIR/$GH_REPO ] ; then
  git clone https://$GH_TOKEN_NAME:$GH_TOKEN_VAL@github.com/$GH_ORG/$GH_REPO
fi

# Sync the repo
cd $CONFIG_DIR/$GH_REPO
git fetch origin
git reset --hard origin/$GH_BRANCH

popd

# Try to build the latest image.  This is usually a NOP.
# If it fails ignore the error and continue in the hope that there is
# already a local image that will work.
docker build --tag feeder github.com/brianmartinil/feeder || true

# Run the image, set the container to delete itself after
docker run --rm -v $CONFIG_DIR/$GH_REPO/feeds.yml:/config/feeds.yml feeder:latest

# Todo - Delete feeder images that are not feeder:latest

# Push the changes
cd $CONFIG_DIR/$GH_REPO
git add feeds.yml && git commit -a -m "auto" && git push