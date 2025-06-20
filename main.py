import os
import discord
from discord.ext import commands
import asyncio
import subprocess
import threading
from config import BOT_TOKEN, COMMAND_PREFIX
from bot.commands import setup_commands
from bot.game_manager import GameManager

class TruthOrDareBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = False  # We don't need message content since we use slash commands
        intents.guilds = True
        intents.guild_messages = False  # Not needed for slash commands
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.game_manager = GameManager()
    
    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        await setup_commands(self)
        
        try:
            synced = await self.tree.sync()
            print(f"🔁 تم مزامنة {len(synced)} أمر")
        except Exception as e:
            print(f"❌ خطأ في مزامنة الأوامر: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"✅ تم تسجيل الدخول كـ {self.user}")
        print(f"🤖 البوت متصل بـ {len(self.guilds)} خادم")
        
        # Set bot activity
        activity = discord.Game(name="حقيقة أم تحدي | /help")
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ ليس لديك الصلاحيات المطلوبة لتنفيذ هذا الأمر.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ البوت لا يملك الصلاحيات المطلوبة.")
        else:
            print(f"خطأ غير متوقع: {error}")
            await ctx.send("❌ حدث خطأ غير متوقع.")

def start_web_server():
    """Start the Express.js web server in a separate thread"""
    try:
        # Use Popen instead of run to allow it to run in background
        subprocess.Popen(["node", "server.js"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("✅ تم تشغيل السيرفر الويب")
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل السيرفر: {e}")

def main():
    """Main function to run the bot"""
    # Start web server immediately
    start_web_server()
    
    bot = TruthOrDareBot()
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ فشل في تسجيل الدخول. تحقق من رمز البوت.")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
