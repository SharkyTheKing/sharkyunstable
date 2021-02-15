import asyncio
from typing import Optional

import discord
from redbot.core import Config, checks, commands

BASECOG = getattr(commands, "Cog", object)


GUILD_CONFIG = {"toggle_active": False, "recording_channel": None, "banish_role": None}
MEMBER_CONFIG = {"roles": []}


class BanishShin(BASECOG):
    """
    Banishing system for ShinJuri's Discord
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=223391425302102016)
        self.config.register_member(**MEMBER_CONFIG)
        self.config.register_guild(**GUILD_CONFIG)

    @commands.command(name="testbanish")
    @checks.is_owner()
    async def testing_banish_commands(self, ctx):
        channel = await self.get_log_channel(ctx.guild)
        if channel:
            return await ctx.send("Herro. this worked")

        await ctx.send("herro. this didn't work.")

    @commands.group(name="banishset")
    @checks.mod_or_permissions(kick_members=True)
    async def set_banish_settings(self, ctx):
        ...

    @set_banish_settings.command("banishchannel")
    async def log_banish_command(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sets the channel to send logs to.
        """
        if channel is None:
            await self.config.guild(ctx.guild).recording_channel.set(None)
            return await ctx.send("Done. No longer logging.")

        await self.config.guild(ctx.guild).recording_channel.set(channel.id)
        await ctx.send("Done. Now logging banishes to {}".format(channel.mention))

    @set_banish_settings.command(name="banishrole")
    async def banish_role(self, ctx, role: Optional[discord.Role]):
        """
        The role the user will gain for banishing
        """
        if role is None:
            await self.config.guild(ctx.guild).banish_role.set(None)
            return await ctx.send("Cleared the banish role.")

        if role >= ctx.author.top_role:
            return await ctx.send("You can't set a role equal to or higher than your own.")

        if role >= ctx.guild.me.top_role:
            return await ctx.send("You can't set a role that's equal to or higher than the bot.")

        await self.config.guild(ctx.guild).banish_role.set(role.id)
        await ctx.send(
            "Set the banish role to {}.".format(role.mention),
            allowed_mentions=discord.AllowedMentions(roles=False),
        )

    @commands.command(name="nuke")
    @checks.is_owner()
    async def clear_config(self, ctx):
        """
        Why would you need this?

        Sharky says so.
        """
        await self.config.clear_all_members()
        await ctx.tick()

    @checks.mod()
    @commands.command(name="unbanish", usage="<member> [reason]")
    async def unbanish_user(self, ctx, member: discord.Member, *, reason: Optional[str]):
        """
        Unbanishes the member.
        """
        get_role_ids = await self.config.member(member).roles()
        if not get_role_ids:
            return await ctx.send(
                "This user has not been banished. If this is incorrect, please contact Sharky."
            )

        banish_role = await self.get_banish_role(ctx.guild)
        if banish_role is not False:
            try:
                await member.remove_roles(banish_role)
            except:
                return await ctx.send(
                    "Something happened with removing banish role. Contact Sharky, please."
                )

        roles = []
        for role in get_role_ids:
            role_object = discord.utils.get(ctx.guild.roles, id=int(role))
            roles.append(role_object)

        try:
            await member.add_roles(*roles)
            await self.config.member(member).clear()
        except:
            return await ctx.send("Something happened with adding roles. Please contact Sharky.")

        channel = await self.get_log_channel(ctx.guild)
        if channel is False:
            return

        await channel.send(embed=await self.log_unbanish(member, ctx.author, reason))
        await ctx.send("You have unbanished {}".format(member.mention))

    @checks.mod()
    @commands.command(name="banish", usage="<member> [reason]")
    async def banish_user(self, ctx, member: discord.Member, *, reason: Optional[str]):
        """
        Banishes the member.

        `Member`: The Discord member in the server.
        """
        roles = member.roles[-1:0:-1]
        list_of_roles = []

        if any([isinstance(member, discord.Member) and member.top_role >= ctx.me.top_role]):
            return await ctx.send("I can't action someone higher or in the same role as me.")

        if roles:
            async with self.config.member(member).roles() as config_role:
                for author_role in roles:
                    list_of_roles.append(author_role)  # for embed
                    config_role.append(author_role.id)

        if list_of_roles is not None:
            try:
                await member.remove_roles(*list_of_roles)
            except:
                return await ctx.send(
                    "Something happened with removing roles. Contact Sharky, please."
                )

            channel = await self.get_log_channel(ctx.guild)
            if channel is False:
                return
            await channel.send(
                embed=await self.log_removal(member, ctx.author, list_of_roles, reason)
            )

        adding_role = await self.get_banish_role(ctx.guild)
        if adding_role is False:
            return
        try:
            await member.add_roles(adding_role)
        except:
            return await ctx.send("Something happened with adding roles. Contact Sharky, please.")

        await ctx.send("You have banished {}".format(member.mention))

    async def get_log_channel(self, guild: discord.Guild):
        channel_from_config = await self.config.guild(guild).recording_channel()
        if channel_from_config is None:
            return False

        channel = self.bot.get_channel(channel_from_config)
        if channel is None:
            return False

        return channel

    async def get_banish_role(self, guild: discord.Guild):
        role_from_config = await self.config.guild(guild).banish_role()
        if role_from_config is None:
            return False

        role = guild.get_role(role_from_config)
        if role is None:
            return False

        return role

    async def log_unbanish(self, member, author, reason: Optional[str]):
        """
        Logs when a member is unbanished
        """
        embed = discord.Embed()
        embed.title = "Member has been unbanished"
        embed.set_author(name=member, icon_url=member.avatar_url_as(static_format="png"))
        embed.set_footer(text="User ID: {member_id}".format(member_id=member.id))
        if reason is not None:
            embed.description = "**Reason:**\n{reason}".format(reason=reason)
        embed.add_field(name="Moderator:", value="{}\n{}".format(author.name, author.id))
        return embed

    async def log_removal(self, member, author, role, reason: Optional[str]):
        """
        Thank you Core Red.

        https://github.com/Cog-Creators/Red-DiscordBot/blob/1747d901d137ec8d55ba6a5d482df343f4902de9/redbot/cogs/mod/names.py#L216-L250
        """
        role_str = ", ".join([x.mention for x in role])
        if len(role_str) > 1024:
            continuation_string = (
                "and {numeric_number} more roles not displayed due to embed limits."
            )
            available_length = 1024 - len(continuation_string)

            role_chunks = []
            remaining_roles = 0

            for r in role:
                chunk = f"{r.mention}, "
                chunk_size = len(chunk)

                if chunk_size < available_length:
                    available_length -= chunk_size
                    role_chunks.append(chunk)
                else:
                    remaining_roles += 1

            role_chunks.append(continuation_string.format(numeric_number=remaining_roles))

            role_str = "".join(role_chunks)

        embed = discord.Embed()
        embed.set_author(name=member, icon_url=member.avatar_url_as(static_format="png"))
        embed.set_footer(text="User ID: {member_id}".format(member_id=member.id))
        embed.title = "Member has been banished"
        embed.add_field(name="Moderator:", value="{}\n{}".format(author.name, author.id))
        if role_str is not None:
            embed.add_field(
                name="Roles" if len(role) > 1 else "Role", value=role_str, inline=False
            )
        if reason is not None:
            embed.description = "**Reason:**\n{reason}".format(reason=reason)

        return embed
