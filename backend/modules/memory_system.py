import json
import os
from datetime import datetime
from typing import Dict, List
from backend.config import Config

class StudentMemory:
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.profile_path = os.path.join(
            Config.PROFILES_DIR, 
            f"{student_id}.json"
        )
        self.profile = self._load_or_create_profile()
    
    def _load_or_create_profile(self) -> dict:
        """Load existing profile or create new one"""
        
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        
        # Create new profile
        return {
            "student_id": self.student_id,
            "created_at": datetime.now().isoformat(),
            "topic_performance": {},
            "quiz_history": [],
            "interaction_count": 0,
            "weak_topics": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def save(self):
        """Save profile to disk"""
        os.makedirs(Config.PROFILES_DIR, exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    def update_quiz_result(self, topic: str, score: float, teaching_style: str):
        """Record quiz performance"""
        
        # Update quiz history
        self.profile["quiz_history"].append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "score": score,
            "teaching_style": teaching_style
        })
        
        # Update topic performance (moving average)
        if topic in self.profile["topic_performance"]:
            current = self.profile["topic_performance"][topic]
            self.profile["topic_performance"][topic] = 0.7 * current + 0.3 * score
        else:
            self.profile["topic_performance"][topic] = score
        
        # Update weak topics
        self._update_weak_topics()
        
        self.profile["interaction_count"] += 1
        self.profile["last_updated"] = datetime.now().isoformat()
        
        self.save()
    
    def _update_weak_topics(self):
        """Identify topics below mastery threshold"""
        weak = [
            topic for topic, score in self.profile["topic_performance"].items()
            if score < Config.WEAK_TOPIC_THRESHOLD
        ]
        self.profile["weak_topics"] = weak
    
    def get_mastery_level(self, topic: str) -> float:
        """Get current mastery for a topic"""
        return self.profile["topic_performance"].get(topic, 0.0)
    
    def get_recent_performance(self, n: int = 5) -> List[float]:
        """Get recent quiz scores"""
        recent = self.profile["quiz_history"][-n:]
        return [q["score"] for q in recent]