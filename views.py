import discord
from discord.ui import View, Button
from discord import ButtonStyle, Interaction
import random
from data.questions import HAQAIQ, TAHADIAT, UQUBAT
from config import EMOJIS, COLORS

class GameView(View):
    def __init__(self, game_manager, guild_id):
        super().__init__(timeout=300.0)  # 5 minutes timeout
        self.game_manager = game_manager
        self.guild_id = guild_id
    
    @discord.ui.button(label="🧠 حقيقة", style=ButtonStyle.primary)
    async def truth_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        
        current_player = self.game_manager.get_current_player(self.guild_id)
        
        if interaction.user != current_player:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا ليس دورك",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        question = random.choice(HAQAIQ)
        
        embed = discord.Embed(
            title=f"{EMOJIS['truth']} حقيقة",
            description=question,
            color=COLORS['info']
        )
        
        view = NextOrRefuseView(self.game_manager, self.guild_id)
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🎯 تحدي", style=ButtonStyle.success)
    async def dare_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        
        current_player = self.game_manager.get_current_player(self.guild_id)
        
        if interaction.user != current_player:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا ليس دورك",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        question = random.choice(TAHADIAT)
        
        embed = discord.Embed(
            title=f"{EMOJIS['dare']} تحدي",
            description=question,
            color=COLORS['success']
        )
        
        view = NextOrRefuseView(self.game_manager, self.guild_id)
        await interaction.followup.send(embed=embed, view=view)
    
    async def on_timeout(self):
        """Called when the view times out"""
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True

class NextOrRefuseView(View):
    def __init__(self, game_manager, guild_id):
        super().__init__(timeout=300.0)  # 5 minutes timeout
        self.game_manager = game_manager
        self.guild_id = guild_id
    
    @discord.ui.button(label="✅ تم التنفيذ", style=ButtonStyle.success)
    async def complete_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        
        current_player = self.game_manager.get_current_player(self.guild_id)
        
        if interaction.user != current_player:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا ليس دورك",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Move to next player
        self.game_manager.next_turn(self.guild_id)
        next_player = self.game_manager.get_current_player(self.guild_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} تم بنجاح!",
            description=f"الدور التالي: {next_player.mention if next_player else 'لا يوجد لاعبين'}",
            color=COLORS['success']
        )
        
        # Disable all buttons
        for item in self.children:
            try:
                item.disabled = True
            except:
                pass
        
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="❌ رفض", style=ButtonStyle.danger)
    async def refuse_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        
        current_player = self.game_manager.get_current_player(self.guild_id)
        
        if interaction.user != current_player:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="هذا ليس دورك",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        punishment = random.choice(UQUBAT)
        
        # Move to next player
        self.game_manager.next_turn(self.guild_id)
        next_player = self.game_manager.get_current_player(self.guild_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['punishment']} عقابك",
            description=punishment,
            color=COLORS['error']
        )
        
        if next_player:
            embed.add_field(
                name="الدور التالي",
                value=next_player.mention,
                inline=False
            )
        
        # Disable all buttons
        for item in self.children:
            try:
                item.disabled = True
            except:
                pass
        
        await interaction.edit_original_response(embed=embed, view=self)
    
    async def on_timeout(self):
        """Called when the view times out"""
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        
        # Move to next player on timeout
        self.game_manager.next_turn(self.guild_id)
