import asyncio
import json
import uuid
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state management
class GameState:
    def __init__(self):
        self.waiting_player: Optional[WebSocket] = None
        self.active_games: Dict[str, Dict] = {}
        self.player_to_game: Dict[str, str] = {}
        
    def create_game(self, player1: WebSocket, player2: WebSocket) -> str:
        # Generate unique game ID
        game_id = str(uuid.uuid4())
        
        # Create player IDs
        player1_id = str(uuid.uuid4())
        player2_id = str(uuid.uuid4())
        
        # Initialize game state
        self.active_games[game_id] = {
            "players": {
                player1_id: {"websocket": player1, "score": 0, "ready": False},
                player2_id: {"websocket": player2, "score": 0, "ready": False}
            },
            "current_question": None,
            "round": 0,
            "status": "waiting"
        }
        
        # Map players to game
        self.player_to_game[player1_id] = game_id
        self.player_to_game[player2_id] = game_id
        
        # Return game ID
        return game_id, player1_id, player2_id
    
    def get_game(self, game_id: str) -> Optional[Dict]:
        return self.active_games.get(game_id)
        
    def remove_game(self, game_id: str) -> None:
        if game_id in self.active_games:
            # Clean up player mappings
            for player_id in list(self.player_to_game.keys()):
                if self.player_to_game.get(player_id) == game_id:
                    del self.player_to_game[player_id]
            # Remove game
            del self.active_games[game_id]
            
    def get_opponent(self, game_id: str, player_id: str) -> Optional[str]:
        game = self.get_game(game_id)
        if game:
            for pid in game["players"]:
                if pid != player_id:
                    return pid
        return None

# Initialize game state
game_state = GameState()

# Sample questions database
questions = [
    {
        "id": 1,
        "question": "What is 2 + 2?",
        "answer": "4"
    },
    {
        "id": 2,
        "question": "What is the capital of France?",
        "answer": "Paris"
    },
    {
        "id": 3,
        "question": "How many planets are in our solar system?",
        "answer": "8"
    },
    {
        "id": 4,
        "question": "What is 7 * 8?",
        "answer": "56"
    },
    {
        "id": 5,
        "question": "What is the largest ocean on Earth?",
        "answer": "Pacific"
    }
]

def get_random_question():
    return random.choice(questions).copy()

@app.get("/")
async def root():
    return {"message": "1v1 Realtime Quiz Game API"}

@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Player initialization
    player_id = None
    game_id = None
    
    try:
        # Check if there's a waiting player
        if game_state.waiting_player is None:
            # This player will wait for another
            game_state.waiting_player = websocket
            await websocket.send_json({"type": "waiting", "message": "Waiting for opponent..."})
            
            # Wait until matched or disconnected
            while True:
                await asyncio.sleep(1)
                if websocket != game_state.waiting_player:
                    break
        else:
            # Match with waiting player
            opponent_websocket = game_state.waiting_player
            game_state.waiting_player = None
            
            # Create a new game
            game_id, player_id, opponent_id = game_state.create_game(opponent_websocket, websocket)
            
            # Notify both players
            await opponent_websocket.send_json({
                "type": "game_start",
                "game_id": game_id,
                "player_id": opponent_id,
                "message": "Game starting! You are Player 1."
            })
            
            await websocket.send_json({
                "type": "game_start", 
                "game_id": game_id,
                "player_id": player_id,
                "message": "Game starting! You are Player 2."
            })
            
            # Start the first round
            await start_new_round(game_id)
        
        # Main message processing loop
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "answer":
                await process_answer(data, player_id, game_id)
            elif data["type"] == "ready":
                await mark_player_ready(player_id, game_id)
    
    except WebSocketDisconnect:
        # Handle player disconnect
        if websocket == game_state.waiting_player:
            game_state.waiting_player = None
        elif game_id:
            # Notify opponent and end game
            opponent_id = game_state.get_opponent(game_id, player_id)
            if opponent_id:
                opponent_data = game_state.active_games[game_id]["players"].get(opponent_id)
                if opponent_data and opponent_data["websocket"]:
                    await opponent_data["websocket"].send_json({
                        "type": "opponent_left", 
                        "message": "Your opponent has left the game."
                    })
            
            # Clean up game
            game_state.remove_game(game_id)

async def start_new_round(game_id: str):
    game = game_state.get_game(game_id)
    if not game:
        return
    
    # Increment round counter
    game["round"] += 1
    
    # Select a random question (remove answer for sending to clients)
    question = get_random_question()
    correct_answer = question.pop("answer")
    
    # Store question and answer for verification
    game["current_question"] = {
        "id": question["id"],
        "answer": correct_answer
    }
    
    # Reset player ready states
    for player_data in game["players"].values():
        player_data["ready"] = False
    
    # Send question to both players
    for player_id, player_data in game["players"].items():
        await player_data["websocket"].send_json({
            "type": "question",
            "round": game["round"],
            "question": question["question"],
            "question_id": question["id"]
        })

async def process_answer(data, player_id: str, game_id: str):
    game = game_state.get_game(game_id)
    if not game or not game["current_question"]:
        return
    
    # Verify answer
    if data["answer"].lower() == game["current_question"]["answer"].lower():
        # Correct answer - increment score
        game["players"][player_id]["score"] += 1
        
        # Send result to the player who answered
        await game["players"][player_id]["websocket"].send_json({
            "type": "answer_result",
            "correct": True,
            "message": "Correct answer!"
        })
        
        # Notify opponent
        opponent_id = game_state.get_opponent(game_id, player_id)
        if opponent_id:
            await game["players"][opponent_id]["websocket"].send_json({
                "type": "opponent_answer",
                "correct": True,
                "message": "Your opponent answered correctly!"
            })
        
        # Send updated scores
        scores = {pid: pdata["score"] for pid, pdata in game["players"].items()}
        for p_data in game["players"].values():
            await p_data["websocket"].send_json({
                "type": "score_update",
                "scores": scores
            })
        
        # Start next round after a brief delay
        await asyncio.sleep(2)
        await start_new_round(game_id)
    else:
        # Incorrect answer
        await game["players"][player_id]["websocket"].send_json({
            "type": "answer_result",
            "correct": False,
            "message": "Incorrect answer. Try again!"
        })

async def mark_player_ready(player_id: str, game_id: str):
    game = game_state.get_game(game_id)
    if not game:
        return
    
    # Mark player as ready
    game["players"][player_id]["ready"] = True
    
    # Check if all players are ready
    all_ready = all(player["ready"] for player in game["players"].values())
    if all_ready:
        # Start a new round
        await start_new_round(game_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
