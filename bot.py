import os, json, asyncio
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("TARGET_USER_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
DATA_PATH = "ping_data.json"
COOLDOWN = 60

def load_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"total": 0, "goal": 1_000_000}

data = load_data()
last_ping = 0.0
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

def owner(interaction):
    return interaction.user.id == OWNER_ID and interaction.guild is not None

@bot.event
async def on_ready():
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    else:
        await bot.tree.sync()
    print(f"Ready as {bot.user}")

@bot.tree.command(name="pingme", description="Send one opt-in ping to you (60s cooldown)")
async def pingme(interaction: discord.Interaction):
    global last_ping
    if not owner(interaction):
        return await interaction.response.send_message("Owner-only command.", ephemeral=True)
    now = asyncio.get_running_loop().time()
    if now - last_ping < COOLDOWN:
        return await interaction.response.send_message(f"Wait {int(COOLDOWN-(now-last_ping))} seconds.", ephemeral=True)
    last_ping = now
    data["total"] += 1
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(
        f"<@{OWNER_ID}> ping #{data['total']:,} · goal {data['goal']:,}",
        allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False)
    )

@bot.tree.command(name="pingcount", description="View your counter")
async def pingcount(interaction: discord.Interaction):
    await interaction.response.send_message(f"**{data['total']:,} / {data['goal']:,}** pings", ephemeral=True)

@bot.tree.command(name="pinggoal", description="Set a counter goal (no pings sent)")
@app_commands.describe(goal="Goal from 1 to 1 billion")
async def pinggoal(interaction: discord.Interaction, goal: app_commands.Range[int, 1, 1_000_000_000]):
    if not owner(interaction):
        return await interaction.response.send_message("Owner-only.", ephemeral=True)
    data["goal"] = goal
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message(f"Goal set to {goal:,}.", ephemeral=True)

@bot.tree.command(name="pingreset", description="Reset your ping counter")
async def pingreset(interaction: discord.Interaction):
    if not owner(interaction):
        return await interaction.response.send_message("Owner-only.", ephemeral=True)
    data["total"] = 0
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message("Counter reset.", ephemeral=True)

if not TOKEN or not OWNER_ID:
    raise RuntimeError("Configure DISCORD_TOKEN and TARGET_USER_ID in environment variables.")
bot.run(TOKEN)
