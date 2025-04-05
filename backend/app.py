import asyncio
import json
import uuid
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from pydantic import BaseModel
from question_service import QuestionService

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

# Initialize question service
question_service = QuestionService()

# Game state management
class GameState:
    def __init__(self):
        self.waiting_player: Optional[WebSocket] = None
        self.active_games: Dict[str, Dict] = {}
        self.player_to_game: Dict[str, str] = {}
        self.ws_to_player: Dict[WebSocket, str] = {}  # Map websocket to player_id
        
    def create_game(self, player1: WebSocket, player2: WebSocket) -> tuple:
        """
        Create a new game with two players.
        
        Returns:
            tuple: (game_id, player1_id, player2_id)
        """
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
            "status": "waiting",
            "round_finished": False
        }
        
        # Map players to game
        self.player_to_game[player1_id] = game_id
        self.player_to_game[player2_id] = game_id
        
        # Map websockets to player IDs for easier lookup
        self.ws_to_player[player1] = player1_id
        self.ws_to_player[player2] = player2_id
        
        # Return game ID and player IDs
        return game_id, player1_id, player2_id
    
    def get_player_id_from_ws(self, websocket: WebSocket) -> Optional[str]:
        """Get player ID from websocket"""
        return self.ws_to_player.get(websocket)
    
    def get_game(self, game_id: str) -> Optional[Dict]:
        return self.active_games.get(game_id)
        
    def remove_game(self, game_id: str) -> None:
        if game_id in self.active_games:
            # Get websockets to remove from mapping
            game = self.active_games[game_id]
            for player_id, player_data in game["players"].items():
                ws = player_data["websocket"]
                if ws in self.ws_to_player:
                    del self.ws_to_player[ws]
            
            # Clean up player mappings
            for player_id in list(self.player_to_game.keys()):
                if self.player_to_game.get(player_id) == game_id:
                    del self.player_to_game[player_id]
            
            # Remove game
            del self.active_games[game_id]
            
    def get_opponent(self, game_id: str, player_id: str) -> Optional[str]:
        """Get opponent's player ID"""
        game = self.get_game(game_id)
        if game and "players" in game:
            for pid in game["players"]:
                if pid != player_id:
                    return pid
        return None
    
    def get_game_from_player_id(self, player_id: str) -> Optional[str]:
        """Get game ID from player ID"""
        return self.player_to_game.get(player_id)

# Initialize game state
game_state = GameState()

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
                    # Get player ID after matching
                    player_id = game_state.get_player_id_from_ws(websocket)
                    if player_id:
                        game_id = game_state.get_game_from_player_id(player_id)
                    break
        else:
            # Match with waiting player
            waiting_websocket = game_state.waiting_player
            game_state.waiting_player = None
            
            # Create a new game - IMPORTANT: Order matters here!
            game_id, waiting_player_id, current_player_id = game_state.create_game(waiting_websocket, websocket)
            
            # Assign the current player's ID
            player_id = current_player_id
            
            # Notify waiting player (player 1)
            await waiting_websocket.send_json({
                "type": "game_start",
                "game_id": game_id,
                "player_id": waiting_player_id,
                "message": "Game starting! You are Player 1."
            })
            
            # Notify current player (player 2)
            await websocket.send_json({
                "type": "game_start", 
                "game_id": game_id,
                "player_id": current_player_id,
                "message": "Game starting! You are Player 2."
            })
            
            # Start the first round
            await start_new_round(game_id)
        
        # Main message processing loop
        while True:
            data = await websocket.receive_json()
            
            # Update player ID and game ID from message if available
            if "player_id" in data:
                player_id = data["player_id"]
                if "game_id" in data:
                    game_id = data["game_id"]
                else:
                    game_id = game_state.get_game_from_player_id(player_id)
            
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
                game = game_state.get_game(game_id)
                if game and opponent_id in game["players"]:
                    opponent_data = game["players"].get(opponent_id)
                    if opponent_data and opponent_data["websocket"]:
                        await opponent_data["websocket"].send_json({
                            "type": "opponent_left", 
                            "message": "Your opponent has left the game."
                        })
            
            # Clean up game
            game_state.remove_game(game_id)
    finally:
        # Additional cleanup
        if websocket in game_state.ws_to_player:
            del game_state.ws_to_player[websocket]

async def start_new_round(game_id: str):
    game = game_state.get_game(game_id)
    if not game:
        return
    
    # Increment round counter
    game["round"] += 1
    
    # Reset round_finished flag
    game["round_finished"] = False
    
    # Get a random question from MongoDB
    db_question = question_service.get_random_question()
    
    # Store question and answer for verification
    game["current_question"] = {
        "id": str(db_question.get("_id", "")),
        "answer": db_question.get("answer", ""),
        "time_limit": db_question.get("time", 30)
    }
    
    # Reset player ready states
    for player_data in game["players"].values():
        player_data["ready"] = False
    
    # Send question to both players
    for player_id, player_data in game["players"].items():
        await player_data["websocket"].send_json({
            "type": "question",
            "round": game["round"],
            "question": db_question.get("question", ""),
            "question_id": str(db_question.get("_id", "")),
            "time_limit": db_question.get("time", 30)
        })

async def process_answer(data, player_id: str, game_id: str):
    game = game_state.get_game(game_id)
    if not game or not game["current_question"] or not player_id or player_id not in game["players"]:
        return

    # Get the submitted answer
    submitted_answer = data.get("answer", "").strip().lower()
    correct_answer = game["current_question"]["answer"].strip().lower()

    # Log answer processing for debugging
    print(f"Processing answer: Player {player_id} submitted '{submitted_answer}', correct is '{correct_answer}'")
    print(f"Round finished: {game.get('round_finished', False)}")

    # Prevent processing if the round is already finished
    if game.get("round_finished", False):
        await game["players"][player_id]["websocket"].send_json({
            "type": "answer_result",
            "correct": submitted_answer == correct_answer,
            "message": "The round is already complete."
        })
        return

    # Verify answer
    if submitted_answer == correct_answer:
        # Mark round as finished
        game["round_finished"] = True
        
        # Correct answer - increment score
        game["players"][player_id]["score"] += 1
        print(f"Player {player_id} score increased to {game['players'][player_id]['score']}")

        # Send result to the player who answered
        await game["players"][player_id]["websocket"].send_json({
            "type": "answer_result",
            "correct": True,
            "message": "Correct answer!"
        })

        # Notify opponent
        opponent_id = game_state.get_opponent(game_id, player_id)
        if opponent_id and opponent_id in game["players"]:
            await game["players"][opponent_id]["websocket"].send_json({
                "type": "opponent_answer",
                "correct": True,
                "message": "Your opponent answered correctly!"
            })

        # Send updated scores to both players
        scores = {pid: pdata["score"] for pid, pdata in game["players"].items()}
        for p_id, p_data in game["players"].items():
            await p_data["websocket"].send_json({
                "type": "score_update",
                "scores": scores
            })

        # Notify both players that the round is over
        for p_data in game["players"].values():
            await p_data["websocket"].send_json({
                "type": "round_over",
                "message": "Round complete! Get ready for the next question."
            })

        # Delay before starting next round so clients can display the results
        await asyncio.sleep(3)

        # Start new round
        await start_new_round(game_id)
    else:
        # Incorrect answer; only send feedback to the player who answered
        await game["players"][player_id]["websocket"].send_json({
            "type": "answer_result",
            "correct": False,
            "message": "Incorrect answer. Try again!"
        })

async def mark_player_ready(player_id: str, game_id: str):
    game = game_state.get_game(game_id)
    if not game or player_id not in game["players"]:
        return
    
    # Mark player as ready
    game["players"][player_id]["ready"] = True
    
    # Check if all players are ready
    all_ready = all(player["ready"] for player in game["players"].values())
    if all_ready:
        # Start a new round
        await start_new_round(game_id)

# Close MongoDB connection when the app shuts down
@app.on_event("shutdown")
async def shutdown_event():
    question_service.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)