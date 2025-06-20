import discord
from discord import app_commands, Interaction
from discord.ext import commands
import random
from data.questions import HAQAIQ, TAHADIAT, UQUBAT
from bot.views import GameView, NextOrRefuseView
from utils.permissions import is_admin
from config import EMOJIS, COLORS

async def setup_commands(bot):
    """Setup all slash commands for the bot"""
    
    @bot.tree.command(name="ping", description="فحص حالة البوت")
    async def ping(interaction: Interaction):
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title=f"{EMOJIS['ping']} حالة البوت",
            description=f"البوت يعمل بشكل طبيعي\nالتأخير: {latency}ms",
            color=COLORS['success']
        )
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="help", description="عرض قائمة الأوامر")
    async def help_command(interaction: Interaction):
        embed = discord.Embed(
            title="🤖 أوامر بوت حقيقة أو تحدي",
            color=COLORS['info']
        )
        
        embed.add_field(
            name="🎮 أوامر اللعبة",
            value="""
            `/ابدا_طابور` - بدء اللعبة وفتح الطابور
            `/انضم` - دخول الطابور
            `/انسحب` - الخروج من الطابور
            `/ابدأ` - بدء اللعب بالدور
            `/طابور` - عرض اللاعبين في الطابور
            """,
            inline=False
        )
        
        embed.add_field(
            name="🎲 أوامر الأسئلة",
            value="""
            `/حقيقة` - يعطي حقيقة عشوائية
            `/تحدي` - يعطي تحدي عشوائي
            `/عشوائي` - يعطي إما حقيقة أو تحدي عشوائي
            """,
            inline=False
        )
        
        embed.add_field(
            name="👑 أوامر الإدارة",
            value="""
            `/اضف` - إضافة سؤال جديد
            `/حذف` - حذف سؤال موجود
            `/طرد` - طرد شخص من الطابور
            `/انهاء` - إنهاء اللعبة والطابور
            """,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="ابدا_طابور", description="بدء لعبة حقيقة أم تحدي")
    async def start_queue(interaction: Interaction):
        if bot.game_manager.is_game_started(interaction.guild_id):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="اللعبة بدأت بالفعل في هذا الخادم",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        bot.game_manager.start_game(interaction.guild_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['game']} تم بدء لعبة حقيقة أم تحدي!",
            description=f"""
            {EMOJIS['queue']} استخدم `/انضم` لدخول اللعبة
            {EMOJIS['info']} سيتم ترتيب الأدوار حسب وقت الانضمام
            {EMOJIS['game']} استخدم `/ابدأ` لبدء اللعب عندما يكون هناك لاعبين
            """,
            color=COLORS['success']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="انضم", description="انضمام إلى لعبة حقيقة أم تحدي")
    async def join(interaction: Interaction):
        user = interaction.user
        guild_id = interaction.guild_id
        
        if not bot.game_manager.is_game_started(guild_id):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="لا توجد لعبة نشطة. استخدم `/ابدا_طابور` لبدء لعبة جديدة",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if bot.game_manager.is_player_in_queue(guild_id, user.id):
            embed = discord.Embed(
                title=f"{EMOJIS['warning']} تحذير", 
                description="أنت بالفعل في الطابور",
                color=COLORS['warning']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        success = bot.game_manager.add_player(guild_id, user)
        if success:
            player_count = bot.game_manager.get_player_count(guild_id)
            embed = discord.Embed(
                title=f"{EMOJIS['success']} تم الانضمام بنجاح!",
                description=f"{user.mention} انضم إلى اللعبة!\n👥 عدد اللاعبين الآن: {player_count}",
                color=COLORS['success']
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="الطابور ممتلئ أو حدث خطأ",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="انسحب", description="الخروج من طابور اللعبة")
    async def leave(interaction: Interaction):
        user = interaction.user
        guild_id = interaction.guild_id
        
        if bot.game_manager.remove_player(guild_id, user.id):
            embed = discord.Embed(
                title=f"{EMOJIS['warning']} انسحاب",
                description=f"{user.mention} خرج من اللعبة",
                color=COLORS['warning']
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="أنت لست في الطابور",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="طابور", description="عرض اللاعبين في الطابور")
    async def show_queue(interaction: Interaction):
        guild_id = interaction.guild_id
        players = bot.game_manager.get_players(guild_id)
        
        if not players:
            embed = discord.Embed(
                title=f"{EMOJIS['info']} الطابور فارغ",
                description="لا يوجد لاعبين في الطابور حالياً",
                color=COLORS['info']
            )
        else:
            player_list = "\n".join([f"{i+1}. {player.mention}" for i, player in enumerate(players)])
            current_player = bot.game_manager.get_current_player(guild_id)
            
            embed = discord.Embed(
                title=f"{EMOJIS['queue']} طابور اللاعبين",
                description=player_list,
                color=COLORS['info']
            )
            
            if current_player:
                embed.add_field(
                    name="🎯 الدور الحالي",
                    value=current_player.mention,
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="ابدأ", description="بدء دور اللعب")
    async def start_round(interaction: Interaction):
        guild_id = interaction.guild_id
        
        if not bot.game_manager.is_game_started(guild_id):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="لا توجد لعبة نشطة",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        current_player = bot.game_manager.get_current_player(guild_id)
        if not current_player:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="لا يوجد لاعبين في الطابور",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['game']} دور {current_player.display_name}",
            description="اختر: حقيقة أم تحدي؟",
            color=COLORS['game']
        )
        
        view = GameView(bot.game_manager, guild_id)
        await interaction.response.send_message(embed=embed, view=view)
    
    @bot.tree.command(name="عشوائي", description="الحصول على سؤال عشوائي")
    async def random_question(interaction: Interaction):
        all_questions = HAQAIQ + TAHADIAT
        question = random.choice(all_questions)
        
        embed = discord.Embed(
            title=f"{EMOJIS['random']} سؤال عشوائي",
            description=question,
            color=COLORS['game']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="حقيقة", description="الحصول على سؤال حقيقة")
    async def truth_only(interaction: Interaction):
        question = random.choice(HAQAIQ)
        
        embed = discord.Embed(
            title=f"{EMOJIS['truth']} حقيقة",
            description=question,
            color=COLORS['info']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="تحدي", description="الحصول على تحدي")
    async def dare_only(interaction: Interaction):
        question = random.choice(TAHADIAT)
        
        embed = discord.Embed(
            title=f"{EMOJIS['dare']} تحدي",
            description=question,
            color=COLORS['success']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="اضف", description="إضافة سؤال جديد (للمديرين)")
    @app_commands.describe(
        النوع="اختر نوع السؤال",
        النص="اكتب السؤال الجديد"
    )
    @app_commands.choices(النوع=[
        app_commands.Choice(name="🧠 حقيقة", value="haqeeqa"),
        app_commands.Choice(name="🎯 تحدي", value="tahady"),
        app_commands.Choice(name="⚠️ عقاب", value="uquba")
    ])
    async def add_question(interaction: Interaction, النوع: app_commands.Choice[str], النص: str):
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا الأمر مخصص للإدارة فقط",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add appropriate emoji prefix
        if النوع.value == "haqeeqa":
            HAQAIQ.append(f"{EMOJIS['truth']} {النص}")
            type_name = "حقيقة"
        elif النوع.value == "tahady":
            TAHADIAT.append(f"{EMOJIS['dare']} {النص}")
            type_name = "تحدي"
        else:
            UQUBAT.append(f"{EMOJIS['punishment']} {النص}")
            type_name = "عقاب"
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} تمت الإضافة بنجاح!",
            description=f"تم إضافة {type_name} جديد",
            color=COLORS['success']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="حذف", description="حذف سؤال موجود (للمديرين)")
    @app_commands.describe(
        النوع="اختر نوع العنصر",
        النص="اكتب النص الذي تريد حذفه بالضبط"
    )
    @app_commands.choices(النوع=[
        app_commands.Choice(name="🧠 حقيقة", value="haqeeqa"),
        app_commands.Choice(name="🎯 تحدي", value="tahady"),
        app_commands.Choice(name="⚠️ عقاب", value="uquba")
    ])
    async def delete_item(interaction: Interaction, النوع: app_commands.Choice[str], النص: str):
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا الأمر مخصص للإدارة فقط",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        removed = False
        if النوع.value == "haqeeqa":
            # Try to find and remove with emoji prefix
            item_with_emoji = f"{EMOJIS['truth']} {النص}"
            if item_with_emoji in HAQAIQ:
                HAQAIQ.remove(item_with_emoji)
                removed = True
            # Also try without emoji prefix in case user provided exact text
            elif النص in HAQAIQ:
                HAQAIQ.remove(النص)
                removed = True
        elif النوع.value == "tahady":
            item_with_emoji = f"{EMOJIS['dare']} {النص}"
            if item_with_emoji in TAHADIAT:
                TAHADIAT.remove(item_with_emoji)
                removed = True
            elif النص in TAHADIAT:
                TAHADIAT.remove(النص)
                removed = True
        else:  # uquba
            item_with_emoji = f"{EMOJIS['punishment']} {النص}"
            if item_with_emoji in UQUBAT:
                UQUBAT.remove(item_with_emoji)
                removed = True
            elif النص in UQUBAT:
                UQUBAT.remove(النص)
                removed = True

        if removed:
            embed = discord.Embed(
                title=f"{EMOJIS['success']} تم الحذف بنجاح!",
                description=f"تم حذف العنصر من قائمة {النوع.name}",
                color=COLORS['success']
            )
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="لم يتم العثور على هذا النص في القائمة المطلوبة",
                color=COLORS['error']
            )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="طرد", description="طرد لاعب من الطابور (للمديرين)")
    @app_commands.describe(المستخدم="اختر المستخدم المراد طرده")
    async def kick_player(interaction: Interaction, المستخدم: discord.Member):
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا الأمر مخصص للإدارة فقط",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        if bot.game_manager.remove_player(guild_id, المستخدم.id):
            embed = discord.Embed(
                title=f"{EMOJIS['stop']} طرد من اللعبة",
                description=f"تم طرد {المستخدم.mention} من الطابور",
                color=COLORS['warning']
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا المستخدم ليس في الطابور",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="انهاء", description="إنهاء اللعبة والطابور (للمديرين)")
    async def end_game(interaction: Interaction):
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا الأمر مخصص للإدارة فقط",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        bot.game_manager.end_game(guild_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['stop']} تم إنهاء اللعبة",
            description="يمكنك البدء من جديد باستخدام `/ابدا_طابور`",
            color=COLORS['warning']
        )
        
        await interaction.response.send_message(embed=embed)
