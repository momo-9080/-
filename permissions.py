import discord
from typing import Union

def is_admin(user: Union[discord.Member, discord.User]) -> bool:
    """Check if user has administrator permissions"""
    if isinstance(user, discord.Member):
        return user.guild_permissions.administrator
    return False

def is_moderator(user: Union[discord.Member, discord.User]) -> bool:
    """Check if user has moderator permissions (manage messages, kick members, etc.)"""
    if isinstance(user, discord.Member):
        perms = user.guild_permissions
        return (perms.administrator or 
                perms.manage_messages or 
                perms.kick_members or 
                perms.manage_guild)
    return False

def has_manage_roles(user: Union[discord.Member, discord.User]) -> bool:
    """Check if user can manage roles"""
    if isinstance(user, discord.Member):
        return user.guild_permissions.manage_roles
    return False

def can_manage_bot(user: Union[discord.Member, discord.User]) -> bool:
    """Check if user can manage bot settings"""
    return is_admin(user)

def check_bot_permissions(guild: discord.Guild, required_perms: list) -> dict:
    """Check if bot has required permissions in guild"""
    bot_member = guild.me
    bot_perms = bot_member.guild_permissions
    
    results = {}
    for perm in required_perms:
        results[perm] = getattr(bot_perms, perm, False)
    
    return results

def get_missing_permissions(guild: discord.Guild, required_perms: list) -> list:
    """Get list of missing permissions for the bot"""
    perm_check = check_bot_permissions(guild, required_perms)
    return [perm for perm, has_perm in perm_check.items() if not has_perm]

# Required permissions for the bot to function properly
REQUIRED_BOT_PERMISSIONS = [
    'send_messages',
    'embed_links',
    'use_external_emojis',
    'add_reactions',
    'read_message_history',
    'manage_messages'  # Optional but recommended
]
