import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Settings
    MODEL_NAME = "gemini-pro"
    
    # RL Settings
    LEARNING_RATE = 0.1
    DISCOUNT_FACTOR = 0.9
    EPSILON = 0.2
    
    # Teaching Styles
    TEACHING_STYLES = ["simple", "example_based", "analogy", "advanced"]
    
    # Performance Thresholds
    MASTERY_THRESHOLD = 0.7
    WEAK_TOPIC_THRESHOLD = 0.5
    
    # Paths
    DATA_DIR = "backend/data"
    PROFILES_DIR = f"{DATA_DIR}/student_profiles"