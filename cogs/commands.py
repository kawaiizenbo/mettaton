from distutils.log import debug
import discord, datetime, time, platform

from discord.commands import slash_command, option
from discord.ext import commands

class Commands(commands.Cog):
    queue = [ None ]
    now_playing = "None"
    debug = False
    
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
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Bot Source", value="https://github.com/kawaiizenbo/mettaton", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.respond(embed = embed, ephemeral=not debug)

    @slash_command(name="queue")
    async def queue_cmd(self, ctx):
        """Show upcoming sounds."""
        queuef = ""
        for s in Commands.queue:
            if s == None:
                continue
            queuef += f"`{s}`\n"

        if queuef == "":
            queuef = "`None`"

        embed = discord.Embed(
            color = 0xFFFF55,
            title = "Queue",
        )

        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar)
        embed.add_field(name="Now Playing", value=f"`{Commands.now_playing}`", inline=False)
        embed.add_field(name="Queue", value=queuef, inline=False)
        
        await ctx.respond(embed = embed, ephemeral=not debug)

    @slash_command(name="play")
    @option("attachment", discord.Attachment, description="The music/video that you want to play")
    async def play(self, ctx, attachment: discord.Attachment):
        """Play a sound"""
        if ctx.voice_client is None:
            return await ctx.respond("Not in voice channel!", ephemeral=not debug)
        
        await attachment.save(f"uploaded/{attachment.filename}")

        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            Commands.queue.append(f"uploaded/{attachment.filename}")
            return await ctx.respond(f"Added to queue:\n`{attachment.filename}`", ephemeral=not debug)
        try:
            Commands.now_playing = f"uploaded/{attachment.filename}"
            voice.play(discord.FFmpegPCMAudio(f"uploaded/{attachment.filename}"))
        except:
            return await ctx.respond("sound failure!", ephemeral=not debug)
        await ctx.respond(f"Playing sound:\n`{attachment.filename}`", ephemeral=not debug)

    @slash_command(name="join")
    @option("channel", discord.VoiceChannel, description="Select a channel")
    async def join(self, ctx, channel: discord.VoiceChannel):
        """Join Voice Channel."""
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
            return await ctx.respond(f"Joined voice channel <#{channel.id}>", ephemeral=not debug)

        await channel.connect()
        await ctx.respond(f"Joined voice channel #{channel.name}", ephemeral=not debug)

    @slash_command(name="leave")
    @discord.default_permissions(move_members=True)
    async def leave(self, ctx):
        """Join Voice Channel."""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            return await ctx.respond("Left voice channel", ephemeral=not debug)

        await ctx.respond("Not in voice channel", ephemeral=not debug)
    
    @slash_command(name="skip")
    @discord.default_permissions(mute_members=True)
    async def skip(self, ctx):
        """Skip current sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            if len(Commands.queue) > 1:
                voice.play(discord.FFmpegPCMAudio(Commands.queue[1]))
                Commands.now_playing = f"uploaded/{Commands.queue[1]}"
                Commands.queue.pop(1)
                return await ctx.respond("Skipped sound.", ephemeral=not debug)
            return await ctx.respond("End of queue.", ephemeral=not debug)
        await ctx.respond("Nothing is playing.", ephemeral=not debug)

    @slash_command(name="next")
    async def next(self, ctx):
        """Skip current sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            return await ctx.respond("Something is playing.", ephemeral=not debug)
        voice.stop()
        if len(Commands.queue) > 1:
            voice.play(discord.FFmpegPCMAudio(Commands.queue[1]))
            Commands.now_playing = f"uploaded/{Commands.queue[1]}"
            Commands.queue.pop(1)
            return await ctx.respond(f"Now playing \"{Commands.now_playing}\".", ephemeral=not debug)
        return await ctx.respond("End of queue.", ephemeral=not debug)
    
    @slash_command(name="kill")
    async def kill(self, ctx):
        """Stop bot (bot owner only)"""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.respond("No permission.", ephemeral=not debug)
        
        await ctx.respond("```\n * YOU WON!\n * You earned 800 XP and 0 gold.\n * Your LOVE increased.\n```")
        exit(0)
