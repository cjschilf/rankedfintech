import random
from typing import Dict, List, Optional
import json
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class QuestionService:
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the question service with MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string. If None, uses environment variable or default.
        """
        # Use provided connection string, environment variable, or default
        self.connection_string = connection_string or os.environ.get(
            "MONGODB_URI", 
            "mongodb+srv://colinschilf2025:SuA1Cw1uBUOMCcZq@rankedfintech.veidnzl.mongodb.net/?appName=RankedFintech"
        )
        
        # Connect to MongoDB
        self.client = MongoClient(self.connection_string, server_api=ServerApi('1'))
        self.db = self.client["rankedfintech"]
        self.questions_collection = self.db["problems"]
        
        # Check if we have questions in the database, load samples if empty
        if self.count() == 0:
            print("No questions found in database. Loading sample questions...")
            self._load_sample_questions()
    
    def _load_sample_questions(self) -> None:
        """Load built-in sample questions into the database if it's empty"""
        sample_questions = [
            {
                "question": "What is 2 + 2?",
                "answer": "4",
                "time": 10
            },
            {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "time": 15
            },
            {
                "question": "How many planets are in our solar system?",
                "answer": "8",
                "time": 15
            },
            {
                "question": "What is 7 * 8?",
                "answer": "56",
                "time": 10
            },
            {
                "question": "What is the largest ocean on Earth?",
                "answer": "Pacific",
                "time": 15
            },
            {
                "question": "What is the square root of 64?",
                "answer": "8",
                "time": 10
            },
            {
                "question": "What is the chemical symbol for gold?",
                "answer": "Au",
                "time": 15
            },
            {
                "question": "What is the first element on the periodic table?",
                "answer": "Hydrogen",
                "time": 15
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "answer": "Shakespeare",
                "time": 15
            },
            {
                "question": "What is the smallest prime number?",
                "answer": "2",
                "time": 10
            }
        ]
        
        # Insert sample questions into the database
        self.questions_collection.insert_many(sample_questions)
        print(f"Loaded {len(sample_questions)} sample questions into the database")
    
    def get_random_question(self) -> Dict:
        """
        Get a random question from the database.
        
        Returns:
            A random question dictionary
        """
        # Use MongoDB's $sample aggregation to get a random document
        random_question = list(self.questions_collection.aggregate([
            {"$sample": {"size": 1}}
        ]))
        
        if not random_question:
            return {"_id": "0", "question": "No questions available", "answer": "None", "time": 10}
        
        return random_question[0]
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: The MongoDB ID of the question to retrieve
            
        Returns:
            The question dictionary or None if not found
        """
        from bson.objectid import ObjectId
        
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(question_id)
            question = self.questions_collection.find_one({"_id": object_id})
            return question
        except Exception as e:
            print(f"Error retrieving question: {e}")
            return None
    
    def validate_answer(self, question_id: str, answer: str) -> bool:
        """
        Check if an answer is correct for a given question.
        
        Args:
            question_id: The MongoDB ID of the question
            answer: The answer to check
            
        Returns:
            True if the answer is correct, False otherwise
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return False
        
        # Simple string comparison (case insensitive)
        return answer.lower().strip() == question["answer"].lower().strip()
    
    def add_question(self, question: str, answer: str, time: int = 30) -> Dict:
        """
        Add a new question to the database.
        
        Args:
            question: The question text
            answer: The correct answer
            time: Time limit in seconds (default 30)
            
        Returns:
            The created question dictionary with MongoDB _id
        """
        new_question = {
            "question": question,
            "answer": answer,
            "time": time
        }
        
        result = self.questions_collection.insert_one(new_question)
        # Get the inserted document with the _id field
        inserted_question = self.questions_collection.find_one({"_id": result.inserted_id})
        return inserted_question
    
    def get_all_questions(self, limit: int = 100, skip: int = 0) -> List[Dict]:
        """
        Get all questions with pagination.
        
        Args:
            limit: Maximum number of questions to return
            skip: Number of questions to skip (for pagination)
            
        Returns:
            A list of question dictionaries
        """
        cursor = self.questions_collection.find().limit(limit).skip(skip)
        return list(cursor)
    
    def count(self) -> int:
        """
        Get the number of questions.
        
        Returns:
            The number of questions in the database
        """
        return self.questions_collection.count_documents({})
    
    def close(self):
        """Close the MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()

# Usage example
if __name__ == "__main__":
    service = QuestionService()
    
    # Print the total count
    print(f"Total questions in database: {service.count()}")
    
    # Get a random question
    question = service.get_random_question()
    print(f"\nRandom question: {question['question']}")
    print(f"Answer: {question['answer']}")
    print(f"Time limit: {question['time']} seconds")
    print(f"MongoDB ID: {question['_id']}")
    
    # Clean up
    service.close()