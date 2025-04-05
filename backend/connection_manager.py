from fastapi import WebSocket
from typing import Dict, List, Set, Optional
import uuid

class ConnectionManager:
    """
    Manages WebSocket connections and player sessions
    """
    
    def __init__(self):
        # Active connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Waiting for match
        self.waiting_player: Optional[str] = None
        
        # Game mappings
        self.player_to_game: Dict[str, str] = {}
        self.game_to_players: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        Register a new WebSocket connection and return a player ID
        
        Args:
            websocket: The WebSocket connection
            
        Returns:
            A unique player ID
        """
        await websocket.accept()
        player_id = str(uuid.uuid4())
        self.active_connections[player_id] = websocket
        return player_id
    
    def disconnect(self, player_id: str) -> None:
        """
        Remove a WebSocket connection
        
        Args:
            player_id: The player ID to disconnect
        """
        if player_id in self.active_connections:
            del self.active_connections[player_id]
        
        # Clean up waiting player
        if self.waiting_player == player_id:
            self.waiting_player = None
        
        # Clean up game associations
        game_id = self.player_to_game.get(player_id)
        if game_id:
            if game_id in self.game_to_players:
                self.game_to_players[game_id].discard(player_id)
                if not self.game_to_players[game_id]:
                    del self.game_to_players[game_id]
            del self.player_to_game[player_id]
    
    async def send_personal_message(self, message: Dict, player_id: str) -> bool:
        """
        Send a message to a specific player
        
        Args:
            message: The message to send
            player_id: The player ID to send to
            
        Returns:
            True if the message was sent, False otherwise
        """
        if player_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[player_id]
        await websocket.send_json(message)
        return True
    
    async def broadcast_to_game(self, message: Dict, game_id: str, exclude: Optional[str] = None) -> None:
        """
        Broadcast a message to all players in a game
        
        Args:
            message: The message to send
            game_id: The game ID
            exclude: Optional player ID to exclude from the broadcast
        """
        if game_id not in self.game_to_players:
            return
        
        for player_id in self.game_to_players[game_id]:
            if exclude and player_id == exclude:
                continue
            
            await self.send_personal_message(message, player_id)
    
    def set_waiting_player(self, player_id: str) -> None:
        """
        Set a player as waiting for a match
        
        Args:
            player_id: The player ID
        """
        self.waiting_player = player_id
    
    def get_waiting_player(self) -> Optional[str]:
        """
        Get the player ID currently waiting for a match
        
        Returns:
            The player ID or None if no player is waiting
        """
        return self.waiting_player
    
    def create_game(self, player1_id: str, player2_id: str) -> str:
        """
        Create a new game with two players
        
        Args:
            player1_id: The first player ID
            player2_id: The second player ID
            
        Returns:
            A unique game ID
        """
        game_id = str(uuid.uuid4())
        
        # Associate players with game
        self.player_to_game[player1_id] = game_id
        self.player_to_game[player2_id] = game_id
        
        # Associate game with players
        self.game_to_players[game_id] = {player1_id, player2_id}
        
        # Clear waiting player if needed
        if self.waiting_player in (player1_id, player2_id):
            self.waiting_player = None
        
        return game_id
    
    def get_game_id(self, player_id: str) -> Optional[str]:
        """
        Get the game ID for a player
        
        Args:
            player_id: The player ID
            
        Returns:
            The game ID or None if the player is not in a game
        """
        return self.player_to_game.get(player_id)
    
    def get_opponent(self, player_id: str) -> Optional[str]:
        """
        Get the opponent player ID for a player
        
        Args:
            player_id: The player ID
            
        Returns:
            The opponent player ID or None if no opponent
        """
        game_id = self.get_game_id(player_id)
        if not game_id or game_id not in self.game_to_players:
            return None
        
        players = self.game_to_players[game_id]
        for pid in players:
            if pid != player_id:
                return pid
        
        return None
    
    def is_player_active(self, player_id: str) -> bool:
        """
        Check if a player is still connected
        
        Args:
            player_id: The player ID
            
        Returns:
            True if the player is active, False otherwise
        """
        return player_id in self.active_connections
