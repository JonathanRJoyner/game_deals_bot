#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Define the Heroku app name
HEROKU_APP_NAME="game-deals-bot"

# Set the environment variables on Heroku
heroku config:set DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" \
                  ITAD_KEY="$ITAD_KEY" \
                  SUPABASE_URL="$SUPABASE_URL" \
                  SUPABASE_KEY="$SUPABASE_KEY" \
                  SERVER_COUNT_CHANNEL="$SERVER_COUNT_CHANNEL" \
                  TOPGG_API_TOKEN="$TOPGG_API_TOKEN" \
                  TOPGG_AUTH_TOKEN="$TOPGG_AUTH_TOKEN" \
                  VOTE_CHANNEL_ID="$VOTE_CHANNEL_ID" \
                  -a $HEROKU_APP_NAME
