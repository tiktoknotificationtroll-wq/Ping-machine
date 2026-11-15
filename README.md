# Ping Machine

A safe Discord ping counter bot. `/pingme` sends one mention to the configured owner and has a 60-second cooldown. It never mass-pings, pings @everyone, or runs a spam loop. `/pingcount` tracks progress; `/pinggoal` changes the goal without sending notifications.

## Setup
1. Create a Discord application/bot at https://discord.com/developers/applications.
2. Invite it to your server with the **bot** and **applications.commands** scopes, and permission to send messages.
3. In your hosting provider, add environment variables:
   - `DISCORD_TOKEN`: bot token (secret)
   - `TARGET_USER_ID`: your Discord user ID
   - `GUILD_ID`: optional server ID for immediate slash command sync
4. Install dependencies: `pip install -r requirements.txt`
5. Start: `python bot.py`

## GitHub Actions note
GitHub Actions is designed for finite CI jobs, not persistent bot hosting. The included workflow only validates the Python files; it does **not** keep a Discord bot online. Use a dedicated Python host for continuous uptime. Never commit your bot token.
