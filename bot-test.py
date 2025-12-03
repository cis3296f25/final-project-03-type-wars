import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

GUILD_ID = 1420829218882719848
# --- Load environment variables ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Logging ---
#handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
logging.basicConfig(
    level=logging.DEBUG,
    filename="discord.log",
    encoding="utf-8",
    filemode="w",
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
)

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Create bot ---
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")  # optional if you have a custom help command

# --- Cog extensions ---
initial_extensions = ["cogs.games"]

# --- Ready event ---
@bot.event
async def on_ready():
    print(f"✅ Logged on as {bot.user.name}! ({bot.user.id})")
    # Sync slash commands to the guild(s)
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        #synced = await bot.tree.sync() #global sync
        print(f"🔄 Synced {len(synced)} commands with Discord")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")

# --- Optional message filter example ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Example: block the word "poo"
    if "poo" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} -- don't say that!!")

    await bot.process_commands(message)  # important for commands to work

# --- Run bot ---
async def main():
    async with bot:
        for ext in initial_extensions:
            await bot.load_extension(ext)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
