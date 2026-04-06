from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn

from backend.modules.genai_module import GenAIModule
from backend.modules.memory_system import StudentMemory
from backend.modules.rl_policy import QLearningPolicy

app = FastAPI(title="AI Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
genai = GenAIModule()

class QuestionRequest(BaseModel):
    student_id: str
    question: str
    topic: str

class QuizRequest(BaseModel):
    student_id: str
    topic: str
    difficulty: Optional[str] = "intermediate"
    num_questions: int = 5

class QuizSubmission(BaseModel):
    student_id: str
    topic: str
    answers: Dict[int, str]  # {question_index: selected_answer}
    correct_answers: Dict[int, str]

@app.get("/")
async def root():
    return {"message": "AI Tutor API is running!", "status": "ok"}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    """Answer student question with adaptive teaching"""
    
    # Load student memory
    memory = StudentMemory(req.student_id)
    mastery = memory.get_mastery_level(req.topic)
    recent_scores = memory.get_recent_performance()
    
    # Get optimal teaching style from RL
    rl_policy = QLearningPolicy(req.student_id)
    teaching_style = rl_policy.select_action(mastery, recent_scores)
    
    # Generate explanation
    explanation = genai.generate_explanation(
        question=req.question,
        topic=req.topic,
        teaching_style=teaching_style,
        mastery_level=mastery
    )
    
    return {
        "answer": explanation,
        "teaching_style": teaching_style,
        "mastery_level": mastery,
        "topic": req.topic
    }

@app.post("/generate_quiz")
async def generate_quiz(req: QuizRequest):
    """Generate adaptive quiz"""
    
    memory = StudentMemory(req.student_id)
    mastery = memory.get_mastery_level(req.topic)
    
    # Determine difficulty based on mastery
    if mastery < 0.4:
        difficulty = "beginner"
    elif mastery < 0.7:
        difficulty = "intermediate"
    else:
        difficulty = "advanced"
    
    questions = genai.generate_quiz(req.topic, difficulty, req.num_questions)
    
    return {
        "quiz_id": f"{req.student_id}_{req.topic}",
        "topic": req.topic,
        "difficulty": difficulty,
        "questions": questions
    }

@app.post("/submit_quiz")
async def submit_quiz(submission: QuizSubmission):
    """Evaluate quiz and update RL policy"""
    
    # Calculate score
    total = len(submission.answers)
    correct = sum(
        1 for idx, ans in submission.answers.items()
        if ans == submission.correct_answers.get(idx)
    )
    score = correct / total if total > 0 else 0
    
    # Update memory
    memory = StudentMemory(submission.student_id)
    previous_scores = memory.get_recent_performance()
    previous_score = previous_scores[-1] if previous_scores else 0
    
    memory.update_quiz_result(
        topic=submission.topic,
        score=score,
        teaching_style="simple"  # Get from request if needed
    )
    
    # Update RL policy
    rl_policy = QLearningPolicy(submission.student_id)
    reward = rl_policy.compute_reward(previous_score, score)
    
    new_mastery = memory.get_mastery_level(submission.topic)
    new_scores = memory.get_recent_performance()
    
    rl_policy.update_q_value(reward, new_mastery, new_scores)
    
    return {
        "score": score,
        "correct": correct,
        "total": total,
        "feedback": f"You got {correct}/{total} correct!",
        "new_mastery": new_mastery
    }

@app.get("/progress/{student_id}")
async def get_progress(student_id: str):
    """Get student progress"""
    
    memory = StudentMemory(student_id)
    
    return {
        "student_id": student_id,
        "topic_performance": memory.profile["topic_performance"],
        "quiz_history": memory.profile["quiz_history"],
        "weak_topics": memory.profile["weak_topics"],
        "total_interactions": memory.profile["interaction_count"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)