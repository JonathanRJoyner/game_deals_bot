# Deploying Your Discord Bot on Heroku

You can deploy your own instance of this Discord bot using Heroku. If done properly the cost should be $7/month. However, **you need to verify proper setup of your bot to ensure that pricing**. More details can be found on [Heroku's Pricing Page](https://www.heroku.com/pricing).

## Prerequisites

1. **Heroku Account**: Sign up for a [Heroku account](https://signup.heroku.com/).
2. **Heroku CLI**: Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

## Setting Up Your Tokens

Before deploying your bot, you need to obtain several tokens and set them as environment variables in your Heroku app. These tokens are crucial for your bot to interact with the Discord API, the IsThereAnyDeal API, and Supabase.

---

### Step 1: Obtain the Discord Bot Token

1. **Create a Discord Application**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click on the "New Application" button.
   - Give your application a name and click "Create".

2. **Create a Bot User**:
   - Navigate to the "Bot" tab on the left sidebar.
   - Click on the "Add Bot" button and confirm by clicking "Yes, do it!".

3. **Get the Bot Token**:
   - Under the "Bot" tab, you will see a section called "TOKEN".
   - Click on "Copy" to copy your bot token.

4. **Set Permissions (Optional but recommended)**:
   - Under the "OAuth2" tab, click on "URL Generator".
   - Select the "bot" scope and then select the required permissions your bot needs under "Bot Permissions".
   - Copy the generated URL, paste it into your browser, and authorize your bot to join a server.

For more detailed instructions, visit the [Discord Developer Documentation on Bots](https://discord.com/developers/docs/intro).

### Step 2: Obtain the IsThereAnyDeal API Token

1. **Create an Account**:
   - Go to the [IsThereAnyDeal home page](https://isthereanydeal.com/s).
   - Sign up for an account or log in if you already have one.

2. **Register Your Application**:
   - Once logged in, go to the [my apps page](https://isthereanydeal.com/apps/my/).
   - Click on "Create new app".
   - Fill out the necessary details about your application and submit.

3. **Get Your API Token**:
   - After registering your application, you will be provided with an API token.
   - Copy the API token for use in your bot.

Refer to the [IsThereAnyDeal API Documentation](https://isthereanydeal.com/apidoc/) for more information on using the API.

### Step 3: Set Up Supabase

1. **Create a Supabase Project**:
   - Go to the [Supabase Dashboard](https://app.supabase.io/).
   - Sign up or log in to your Supabase account.
   - Click on "New Project" and follow the prompts to create your project.

2. **Get Your Supabase URL and API Key**:
   - In the project dashboard, go to the "API" tab.
   - Copy the "URL" and "service key" (private API key).

4. **Set Up Environment Variables**:
   - You will need to add your Supabase URL and API key as environment variables in Heroku.

Refer to the [Supabase Documentation](https://supabase.io/docs) for more information on setting up and using Supabase.

### Adding Environment Variables to Heroku

After obtaining the required tokens, you need to set them as environment variables in your Heroku app.

1. **Create a `.env` File**:
   - Create a `.env` file in the root of your project directory and add your environment variables in the following format:

    ```bash
    # Required tokens
    DISCORD_BOT_TOKEN=your_discord_bot_token
    ITAD_KEY=your_isthereanydeal_api_token
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_api_key

    # Optional Tokens
    LOG_CHANNEL_ID=your_log_channel_id
    SERVER_COUNT_CHANNEL=your_server_count_channel
    TOPGG_API_TOKEN=your_topgg_api_token
    TOPGG_AUTH_TOKEN=your_topgg_auth_token

    ```

2. **Login to Heroku**:
   - Open your terminal and log in to Heroku using the CLI.

    ```bash
    heroku login
    ```

3. **Push `.env` Variables to Heroku**:
   - Use the following command to push all environment variables from your `.env` file to your Heroku app:

    ```bash
    xargs -a .env heroku config:set
    ```

    This command reads the `.env` file and sets each variable in your Heroku app configuration.

4. **Verify Environment Variables**:
   - Navigate to your Heroku dashboard, select your app, go to the **Settings** tab, and click on **Reveal Config Vars** to confirm that the variables are set correctly.


### Resources

- [Discord Developer Portal](https://discord.com/developers/applications)
- [IsThereAnyDeal API Documentation](https://isthereanydeal.com/apidoc/)
- [Supabase Documentation](https://supabase.io/docs)
- [Heroku Dev Center](https://devcenter.heroku.com/)
