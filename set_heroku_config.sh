#!/bin/bash

# Load environment variables from .env file
while IFS= read -r line; do
    export "$line"
done < .env

# Define the Heroku app name
HEROKU_APP_NAME="game-deals-bot"

# Set the environment variables on Heroku
heroku config:set $(cat .env | grep -v '^#' | xargs) -a $HEROKU_APP_NAME
