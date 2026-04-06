import requests
from backend.config import Config
import json

class GenAIModule:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash"  # Best model for your project
    
    def generate_explanation(self, question: str, topic: str, 
                            teaching_style: str, mastery_level: float) -> str:
        """Generate personalized explanation"""
        
        style_prompts = {
            "simple": "Explain in very simple terms, as if teaching a beginner. Avoid jargon.",
            "example_based": "Teach through 2-3 concrete examples with step-by-step breakdown.",
            "analogy": "Use real-world analogies and metaphors to explain the concept.",
            "advanced": "Provide detailed technical explanation with formulas and advanced concepts."
        }
        
        prompt = f"""You are an AI tutor teaching {topic}.

Student's current mastery level: {mastery_level*100:.0f}%
Teaching approach: {style_prompts.get(teaching_style, style_prompts['simple'])}

Question: {question}

Provide a clear, educational explanation:"""

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"Sorry, I couldn't generate a response. Error: {response.status_code}"
        except Exception as e:
            return f"Sorry, there was an error: {str(e)}"
    
    def generate_quiz(self, topic: str, difficulty: str, num_questions: int = 5) -> list:
        """Generate quiz questions"""
        
        prompt = f"""Generate {num_questions} multiple-choice questions for {topic} at {difficulty} difficulty level.

Return ONLY valid JSON in this exact format (no markdown, no extra text):
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation of the answer"
  }}
]

Make questions educational and clear. Return ONLY the JSON array."""

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Remove markdown code blocks if present
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                try:
                    questions = json.loads(text)
                    return questions
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {e}")
                    print(f"Text received: {text[:200]}...")
                    return self._fallback_questions(topic)
            else:
                return self._fallback_questions(topic)
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return self._fallback_questions(topic)
    
    def _fallback_questions(self, topic: str) -> list:
        """Fallback questions if JSON parsing fails"""
        return [
            {
                "question": f"What is a fundamental concept in {topic}?",
                "options": {
                    "A": "A computational model that learns from data",
                    "B": "A programming language",
                    "C": "A database system",
                    "D": "A hardware component"
                },
                "correct_answer": "A",
                "explanation": "This is a core concept in the field of machine learning and AI."
            },
            {
                "question": f"Which of the following is commonly used in {topic}?",
                "options": {
                    "A": "Neural networks and algorithms",
                    "B": "Only spreadsheets",
                    "C": "Manual calculations",
                    "D": "Physical models"
                },
                "correct_answer": "A",
                "explanation": "Modern approaches rely heavily on computational methods and algorithms."
            },
            {
                "question": f"What is an important application of {topic}?",
                "options": {
                    "A": "Pattern recognition and prediction",
                    "B": "Building websites only",
                    "C": "Creating documents",
                    "D": "Managing files"
                },
                "correct_answer": "A",
                "explanation": "These techniques are widely used for analyzing data and making predictions."
            }
        ]