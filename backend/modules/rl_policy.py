import numpy as np
import json
import os
from backend.config import Config

class QLearningPolicy:
    """Q-Learning for teaching style optimization"""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.q_table_path = os.path.join(
            Config.PROFILES_DIR,
            f"{student_id}_qtable.json"
        )
        
        # State space: 4 mastery bins × 3 trend bins = 12 states
        self.actions = Config.TEACHING_STYLES
        self.q_table = self._load_or_initialize_qtable()
        
        self.alpha = Config.LEARNING_RATE
        self.gamma = Config.DISCOUNT_FACTOR
        self.epsilon = Config.EPSILON
        
        self.last_state = None
        self.last_action = None
    
    def _load_or_initialize_qtable(self) -> dict:
        """Load or create Q-table"""
        
        if os.path.exists(self.q_table_path):
            with open(self.q_table_path, 'r') as f:
                return json.load(f)
        
        # Initialize Q-table
        q_table = {}
        for mastery_bin in range(4):
            for trend_bin in range(3):
                state = f"{mastery_bin}_{trend_bin}"
                q_table[state] = {action: 0.0 for action in self.actions}
        
        return q_table
    
    def _discretize_state(self, mastery: float, recent_scores: list) -> str:
        """Convert continuous state to discrete state"""
        
        # Bin mastery level
        if mastery < 0.25:
            mastery_bin = 0
        elif mastery < 0.5:
            mastery_bin = 1
        elif mastery < 0.75:
            mastery_bin = 2
        else:
            mastery_bin = 3
        
        # Calculate performance trend
        if len(recent_scores) >= 2:
            trend = recent_scores[-1] - recent_scores[-2]
            if trend < -0.1:
                trend_bin = 0  # Declining
            elif trend > 0.1:
                trend_bin = 2  # Improving
            else:
                trend_bin = 1  # Stable
        else:
            trend_bin = 1  # Stable (default)
        
        return f"{mastery_bin}_{trend_bin}"
    
    def select_action(self, mastery: float, recent_scores: list) -> str:
        """Epsilon-greedy action selection"""
        
        state = self._discretize_state(mastery, recent_scores)
        
        if np.random.random() < self.epsilon:
            # Explore
            action = np.random.choice(self.actions)
        else:
            # Exploit
            q_values = self.q_table[state]
            action = max(q_values, key=q_values.get)
        
        self.last_state = state
        self.last_action = action
        
        return action
    
    def update_q_value(self, reward: float, next_mastery: float, next_scores: list):
        """Q-Learning update"""
        
        if self.last_state is None or self.last_action is None:
            return
        
        next_state = self._discretize_state(next_mastery, next_scores)
        
        current_q = self.q_table[self.last_state][self.last_action]
        max_next_q = max(self.q_table[next_state].values())
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        self.q_table[self.last_state][self.last_action] = new_q
        
        # Save Q-table
        os.makedirs(Config.PROFILES_DIR, exist_ok=True)
        with open(self.q_table_path, 'w') as f:
            json.dump(self.q_table, f, indent=2)
    
    def compute_reward(self, previous_score: float, current_score: float) -> float:
        """Compute reward based on improvement"""
        
        improvement = current_score - previous_score
        
        if improvement > 0.2:
            return 10.0
        elif improvement > 0:
            return 5.0
        elif improvement > -0.1:
            return -2.0
        else:
            return -5.0