import random
from typing import Dict, List, Optional
import json
import os

class QuestionService:
    def __init__(self, questions_file: Optional[str] = None):
        """
        Initialize the question service.
        
        Args:
            questions_file: Path to a JSON file containing questions. 
                           If None, uses built-in sample questions.
        """
        self.questions = []
        
        if questions_file and os.path.exists(questions_file):
            self.load_questions_from_file(questions_file)
        else:
            self.load_sample_questions()
    
    def load_questions_from_file(self, file_path: str) -> None:
        """Load questions from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Validate the loaded questions
            for q in data:
                if isinstance(q, dict) and 'question' in q and 'answer' in q:
                    if 'id' not in q:
                        q['id'] = len(self.questions) + 1
                    self.questions.append(q)
                    
            print(f"Loaded {len(self.questions)} questions from {file_path}")
        except Exception as e:
            print(f"Error loading questions from file: {e}")
            # Fallback to sample questions
            self.load_sample_questions()
    
    def load_sample_questions(self) -> None:
        """Load built-in sample questions"""
        self.questions = [
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
            },
            {
                "id": 6,
                "question": "What is the square root of 64?",
                "answer": "8"
            },
            {
                "id": 7,
                "question": "What is the chemical symbol for gold?",
                "answer": "Au"
            },
            {
                "id": 8, 
                "question": "What is the first element on the periodic table?",
                "answer": "Hydrogen"
            },
            {
                "id": 9,
                "question": "Who wrote 'Romeo and Juliet'?",
                "answer": "Shakespeare"
            },
            {
                "id": 10,
                "question": "What is the smallest prime number?",
                "answer": "2"
            }
        ]
        print(f"Loaded {len(self.questions)} sample questions")
    
    def get_random_question(self) -> Dict:
        """
        Get a random question from the database.
        
        Returns:
            A copy of a random question dictionary
        """
        if not self.questions:
            return {"id": 0, "question": "No questions available", "answer": "None"}
        
        return random.choice(self.questions).copy()
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: The ID of the question to retrieve
            
        Returns:
            The question dictionary or None if not found
        """
        for question in self.questions:
            if question["id"] == question_id:
                return question.copy()
        
        return None
    
    def validate_answer(self, question_id: int, answer: str) -> bool:
        """
        Check if an answer is correct for a given question.
        
        Args:
            question_id: The ID of the question
            answer: The answer to check
            
        Returns:
            True if the answer is correct, False otherwise
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return False
        
        # Simple string comparison (case insensitive)
        return answer.lower().strip() == question["answer"].lower().strip()
    
    def add_question(self, question: str, answer: str) -> Dict:
        """
        Add a new question to the database.
        
        Args:
            question: The question text
            answer: The correct answer
            
        Returns:
            The created question dictionary
        """
        next_id = max([q["id"] for q in self.questions], default=0) + 1
        new_question = {
            "id": next_id,
            "question": question,
            "answer": answer
        }
        
        self.questions.append(new_question)
        return new_question.copy()
    
    def get_all_questions(self) -> List[Dict]:
        """
        Get all questions.
        
        Returns:
            A list of all question dictionaries
        """
        return [q.copy() for q in self.questions]
    
    def count(self) -> int:
        """
        Get the number of questions.
        
        Returns:
            The number of questions in the database
        """
        return len(self.questions)

# Usage example
if __name__ == "__main__":
    service = QuestionService()
    question = service.get_random_question()
    print(f"Random question: {question['question']}")
    print(f"Answer: {question['answer']}")
