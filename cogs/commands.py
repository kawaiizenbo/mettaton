import discord, datetime, time, platform

from discord.commands import slash_command, option
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded') 
        global startTime
        startTime = time.time()

    @slash_command(name="about")
    async def about(self, ctx):
        """Get bot info."""
        uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
        embed = discord.Embed(
            color = 0xFFFF55,
            title = "Bot info",
        )
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar)
        embed.add_field(name="Uptime", value=uptime)
        embed.add_field(name="Latency", value=round(self.bot.latency*1000, 1))
        embed.add_field(name="Pycord Version", value=discord.__version__)
        embed.add_field(name="Host OS", value=f"{platform.system()} {platform.release()}")
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.add_field(name="Bot Source", value="https://github.com/kawaiizenbo/mettaton", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.respond(embed = embed)

    @slash_command(name="play")
    @option("attachment", discord.Attachment, description="The sound that you want to play")
    async def play(self, ctx, attachment: discord.Attachment):
        """Play a sound"""
        if ctx.voice_client is None:
            return await ctx.respond("Not in voice channel!", ephemeral=True)
        
        f = open("files_log.txt", "a")
        f.write(f"{datetime.datetime.now()},{ctx.author.name}#{ctx.author.discriminator},{ctx.author.id},{attachment.filename};\n")
        f.close()
        await attachment.save(f"uploaded/{attachment.filename}")

        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
        try:
            voice.play(discord.FFmpegPCMAudio(f"uploaded/{attachment.filename}"))
        except:
            return await ctx.respond("sound failure!", ephemeral=True)
        await ctx.respond("Playing sound...", ephemeral=True)

    @slash_command(name="join")
    @option("channel", discord.VoiceChannel, description="Select a channel")
    async def join(self, ctx, channel: discord.VoiceChannel):
        """Join Voice Channel."""
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
            return await ctx.respond(f"Joined voice channel <#{channel.id}>", ephemeral=True)

        await channel.connect()
        await ctx.respond(f"Joined voice channel #{channel.name}", ephemeral=True)

    @slash_command(name="leave")
    @discord.default_permissions(move_members=True)
    async def leave(self, ctx):
        """Join Voice Channel."""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            return await ctx.respond("Left voice channel", ephemeral=True)

        await ctx.respond("Not in voice channel", ephemeral=True)
    
    @slash_command(name="stop")
    @discord.default_permissions(mute_members=True)
    async def stop(self, ctx):
        """Stop current sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            return await ctx.respond("Stopped sound.", ephemeral=True)
        await ctx.respond("Nothing is playing.", ephemeral=True)
        exit(0)
    
    @slash_command(name="kill")
    async def kill(self, ctx):
        """Stop bot (bot owner only)"""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.respond("No permission.", ephemeral=True)
        
        await ctx.respond("```\n * YOU WON!\n * You earned 800 XP and 0 gold.\n * Your LOVE increased.\n```")
        exit(0)
