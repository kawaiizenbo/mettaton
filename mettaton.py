import discord, os

from discord.ext import commands
from cogs.commands import Commands

description = """Mettaton."""

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(description=description, intents=intents, debug_guilds=[913237315210588160])

bot.add_cog(Commands(bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

print("Mettaton init")
try:
    print("making upload directory")
    os.mkdir("uploaded")
except:
    print("upload directory already made")

bot.run(open("token.txt", "r").read())
