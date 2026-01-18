import discord


def get_member_mention(guild, username: str) -> str | None:
    member = discord.utils.get(guild.members, name=username)
    if member:
        return f"<@{member.id}>"
    return None
