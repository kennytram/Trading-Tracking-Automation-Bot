import discord


def get_member_mention(guild, username: str):
    member = discord.utils.get(guild.members, name=username)
    if member:
        return f"<@{member.id}>"
    return None
