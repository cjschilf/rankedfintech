import asyncio
import json
import websockets
import sys
from typing import Dict

async def connect_to_game():
    """Simple WebSocket client for testing the game server"""
    uri = "ws://localhost:8000/ws/game"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")
        
        context = {"game_id": None, "player_id": None}
        
        # Handle incoming messages
        receive_task = asyncio.create_task(receive_messages(websocket, context))
        
        # Handle user inputs
        send_task = asyncio.create_task(send_messages(websocket, context))
        
        # Wait until one of the tasks completes
        await asyncio.gather(receive_task, send_task)

async def receive_messages(websocket, context: Dict):
    """Handle incoming messages from the server"""
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {message}")
            
            # Process different message types
            if data["type"] == "waiting":
                print(f"Status: {data['message']}")
            
            elif data["type"] == "game_start":
                print(f"Game started! {data['message']}")
                print(f"Your player ID: {data['player_id']}")
                print(f"Game ID: {data['game_id']}")
                context["player_id"] = data["player_id"]
                context["game_id"] = data["game_id"]
            
            elif data["type"] == "question":
                print(f"\nRound {data['round']}")
                print(f"Question: {data['question']}")
                print(f"Time limit: {data.get('time_limit', 30)} seconds")
                print("Type your answer...")
            
            elif data["type"] == "answer_result":
                if data["correct"]:
                    print(f"Correct! {data['message']}")
                else:
                    print(f"Wrong! {data['message']}")
            
            elif data["type"] == "opponent_answer":
                print(f"Opponent: {data['message']}")
            
            elif data["type"] == "score_update":
                print("Scores:")
                for player_id, score in data["scores"].items():
                    player_label = "You" if player_id == context["player_id"] else "Opponent"
                    print(f"- {player_label}: {score}")
            
            elif data["type"] == "round_over":
                print(f"Round complete: {data['message']}")
            
            elif data["type"] == "opponent_left":
                print(f"Game ended: {data['message']}")
                return
            
            elif data["type"] == "game_end":
                print(f"Game over! {data['message']}")
                print("Final Scores:")
                for player_id, score in data["final_scores"].items():
                    player_label = "You" if player_id == context["player_id"] else "Opponent"
                    print(f"- {player_label}: {score}")
                return
    
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server closed")
    except Exception as e:
        print(f"Error: {e}")

async def send_messages(websocket, context: Dict):
    """Handle user input and send messages to the server"""
    try:
        while True:
            # Wait for user input
            message = await asyncio.get_event_loop().run_in_executor(
                None, lambda: sys.stdin.readline().strip()
            )
            
            # Special commands
            if message == "/quit":
                print("Exiting...")
                break
            
            # Only send answers if we're in a game
            if context["game_id"] and context["player_id"] and message:
                data = {
                    "type": "answer",
                    "game_id": context["game_id"],
                    "player_id": context["player_id"],
                    "answer": message
                }
                await websocket.send(json.dumps(data))
                print(f"Sent: {json.dumps(data)}")
    
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server closed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_game())
    except KeyboardInterrupt:
        print("Client stopped")