from pydantic import BaseModel
from typing import Dict, List, Optional, Union

class Question(BaseModel):
    """Question model with question text and correct answer"""
    id: int
    question: str
    answer: str

class Player(BaseModel):
    """Player model with score and ready status"""
    id: str
    score: int = 0
    ready: bool = False

class Game(BaseModel):
    """Game model representing current game state"""
    id: str
    players: Dict[str, Player]
    current_question: Optional[Question] = None
    round: int = 0
    status: str = "waiting"  # waiting, active, finished

# WebSocket message models
class GameStartMessage(BaseModel):
    """Message sent when a game starts"""
    type: str = "game_start"
    game_id: str
    player_id: str
    message: str

class WaitingMessage(BaseModel):
    """Message sent when a player is waiting for an opponent"""
    type: str = "waiting"
    message: str

class QuestionMessage(BaseModel):
    """Message containing a question for the players"""
    type: str = "question"
    round: int
    question: str
    question_id: int

class AnswerSubmission(BaseModel):
    """Message sent by player when submitting an answer"""
    type: str = "answer"
    game_id: str
    player_id: str
    question_id: int
    answer: str

class AnswerResultMessage(BaseModel):
    """Message sent to player after answer submission"""
    type: str = "answer_result"
    correct: bool
    message: str

class OpponentAnswerMessage(BaseModel):
    """Message sent to notify about opponent's answer"""
    type: str = "opponent_answer"
    correct: bool
    message: str

class ScoreUpdateMessage(BaseModel):
    """Message with updated scores"""
    type: str = "score_update"
    scores: Dict[str, int]

class ReadyMessage(BaseModel):
    """Message sent by player when ready for next round"""
    type: str = "ready"
    game_id: str
    player_id: str

class OpponentLeftMessage(BaseModel):
    """Message sent when opponent disconnects"""
    type: str = "opponent_left"
    message: str

class GameEndMessage(BaseModel):
    """Message sent when game ends"""
    type: str = "game_end"
    winner: Optional[str] = None
    final_scores: Dict[str, int]
    message: str
