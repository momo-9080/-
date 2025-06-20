from typing import Dict, List, Optional
import discord
from config import MAX_PLAYERS

class GameManager:
    def __init__(self):
        # Dictionary to store game data per guild
        # Structure: {guild_id: {"started": bool, "players": List[discord.Member], "current_turn": int}}
        self.games: Dict[int, dict] = {}
    
    def start_game(self, guild_id: int) -> bool:
        """Start a new game in the specified guild"""
        if guild_id in self.games and self.games[guild_id]["started"]:
            return False
        
        self.games[guild_id] = {
            "started": True,
            "players": [],
            "current_turn": 0
        }
        return True
    
    def end_game(self, guild_id: int) -> bool:
        """End the game in the specified guild"""
        if guild_id in self.games:
            del self.games[guild_id]
            return True
        return False
    
    def is_game_started(self, guild_id: int) -> bool:
        """Check if a game is started in the specified guild"""
        return guild_id in self.games and self.games[guild_id]["started"]
    
    def add_player(self, guild_id: int, player: discord.Member) -> bool:
        """Add a player to the game queue"""
        if not self.is_game_started(guild_id):
            return False
        
        game = self.games[guild_id]
        
        # Check if player is already in queue
        if any(p.id == player.id for p in game["players"]):
            return False
        
        # Check if queue is full
        if len(game["players"]) >= MAX_PLAYERS:
            return False
        
        game["players"].append(player)
        return True
    
    def remove_player(self, guild_id: int, player_id: int) -> bool:
        """Remove a player from the game queue"""
        if not self.is_game_started(guild_id):
            return False
        
        game = self.games[guild_id]
        
        # Find and remove the player
        for i, player in enumerate(game["players"]):
            if player.id == player_id:
                # If removing current player, adjust current_turn
                if i <= game["current_turn"] and game["current_turn"] > 0:
                    game["current_turn"] -= 1
                
                game["players"].pop(i)
                
                # Reset turn if no players left
                if not game["players"]:
                    game["current_turn"] = 0
                # Adjust turn if it's out of bounds
                elif game["current_turn"] >= len(game["players"]):
                    game["current_turn"] = 0
                
                return True
        
        return False
    
    def is_player_in_queue(self, guild_id: int, player_id: int) -> bool:
        """Check if a player is in the game queue"""
        if not self.is_game_started(guild_id):
            return False
        
        game = self.games[guild_id]
        return any(p.id == player_id for p in game["players"])
    
    def get_current_player(self, guild_id: int) -> Optional[discord.Member]:
        """Get the current player whose turn it is"""
        if not self.is_game_started(guild_id):
            return None
        
        game = self.games[guild_id]
        if not game["players"]:
            return None
        
        return game["players"][game["current_turn"]]
    
    def next_turn(self, guild_id: int) -> Optional[discord.Member]:
        """Move to the next player's turn"""
        if not self.is_game_started(guild_id):
            return None
        
        game = self.games[guild_id]
        if not game["players"]:
            return None
        
        game["current_turn"] = (game["current_turn"] + 1) % len(game["players"])
        return game["players"][game["current_turn"]]
    
    def get_players(self, guild_id: int) -> List[discord.Member]:
        """Get the list of players in the queue"""
        if not self.is_game_started(guild_id):
            return []
        
        return self.games[guild_id]["players"]
    
    def get_player_count(self, guild_id: int) -> int:
        """Get the number of players in the queue"""
        if not self.is_game_started(guild_id):
            return 0
        
        return len(self.games[guild_id]["players"])
    
    def get_player_position(self, guild_id: int, player_id: int) -> Optional[int]:
        """Get the position of a player in the queue (0-indexed)"""
        if not self.is_game_started(guild_id):
            return None
        
        game = self.games[guild_id]
        for i, player in enumerate(game["players"]):
            if player.id == player_id:
                return i
        
        return None
    
    def clear_all_games(self):
        """Clear all games (useful for bot restart)"""
        self.games.clear()
