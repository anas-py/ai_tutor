import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="wide")

API_URL = "http://localhost:8000"

# Session state
if "student_id" not in st.session_state:
    st.session_state.student_id = f"student_{datetime.now().timestamp()}"
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Sidebar
with st.sidebar:
    st.header("🎓 AI Tutor")
    st.write(f"**Student ID:** {st.session_state.student_id[:20]}...")
    st.divider()
    st.write("**Features:**")
    st.write("✅ Adaptive Teaching")
    st.write("✅ Smart Quizzes")
    st.write("✅ Progress Tracking")
    st.write("✅ RL Optimization")

# Main title
st.title("🎓 Self-Evolving Intelligent AI Tutor")
st.markdown("*Using GenAI, Reinforcement Learning & Long-Term Memory*")

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Learn", "📝 Quiz", "📊 Progress"])

# ===== LEARN TAB =====
with tab1:
    st.header("Ask Questions")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.selectbox(
            "Select Topic:",
            ["Neural Networks", "Supervised Learning", "Deep Learning", 
             "Reinforcement Learning", "Machine Learning Basics"]
        )
        
        question = st.text_area(
            "Your Question:",
            height=100,
            placeholder="E.g., What is backpropagation and how does it work?"
        )
        
        if st.button("Ask 🚀", type="primary", use_container_width=True):
            if question:
                with st.spinner("AI is thinking..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/ask",
                            json={
                                "student_id": st.session_state.student_id,
                                "question": question,
                                "topic": topic
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            st.success("✅ Answer:")
                            st.write(data["answer"])
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.info(f"📚 Teaching Style: **{data['teaching_style']}**")
                            with col_b:
                                st.info(f"📈 Your Mastery: **{data['mastery_level']*100:.0f}%**")
                        else:
                            st.error(f"Error: {response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Cannot connect to backend. Make sure it's running on port 8000")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a question")
    
    with col2:
        st.info("**💡 Tips:**\n\n"
                "• Be specific in your questions\n"
                "• Ask for examples if needed\n"
                "• The AI adapts to your level!\n"
                "• Try different topics")

# ===== QUIZ TAB =====
with tab2:
    st.header("Take a Quiz")
    
    if st.session_state.current_quiz is None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            quiz_topic = st.selectbox(
                "Select Topic for Quiz:",
                ["Neural Networks", "Supervised Learning", "Deep Learning"]
            )
            
            num_questions = st.slider("Number of Questions:", 3, 10, 5)
            
            if st.button("Generate Quiz 📝", type="primary", use_container_width=True):
                with st.spinner("Generating personalized quiz..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate_quiz",
                            json={
                                "student_id": st.session_state.student_id,
                                "topic": quiz_topic,
                                "num_questions": num_questions
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            st.session_state.current_quiz = response.json()
                            st.session_state.quiz_answers = {}
                            st.rerun()
                        else:
                            st.error("Failed to generate quiz")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            st.info("**📝 Quiz Info:**\n\n"
                    "• Adaptive difficulty\n"
                    "• Based on your mastery\n"
                    "• Helps improve weak areas\n"
                    "• Instant feedback")
    
    else:
        # Display quiz
        quiz = st.session_state.current_quiz
        st.subheader(f"Quiz: {quiz['topic']}")
        st.write(f"**Difficulty:** {quiz['difficulty'].title()}")
        st.divider()
        
        correct_answers = {}
        
        for idx, q in enumerate(quiz["questions"]):
            st.write(f"**Question {idx+1}:** {q['question']}")
            
            answer = st.radio(
                f"Select your answer:",
                options=list(q['options'].keys()),
                format_func=lambda x: f"{x}: {q['options'][x]}",
                key=f"q_{idx}"
            )
            
            st.session_state.quiz_answers[idx] = answer
            correct_answers[idx] = q['correct_answer']
            
            st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Quiz ✅", type="primary", use_container_width=True):
                with st.spinner("Evaluating..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/submit_quiz",
                            json={
                                "student_id": st.session_state.student_id,
                                "topic": quiz['topic'],
                                "answers": st.session_state.quiz_answers,
                                "correct_answers": correct_answers
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success(f"🎉 {result['feedback']}")
                            st.write(f"**Score:** {result['score']*100:.0f}%")
                            st.write(f"**New Mastery Level:** {result['new_mastery']*100:.0f}%")
                            
                            # Show explanations
                            st.subheader("Explanations:")
                            for idx, q in enumerate(quiz["questions"]):
                                user_ans = st.session_state.quiz_answers.get(idx)
                                correct_ans = q['correct_answer']
                                
                                if user_ans == correct_ans:
                                    st.success(f"Q{idx+1}: ✅ Correct!")
                                else:
                                    st.error(f"Q{idx+1}: ❌ Your answer: {user_ans}, Correct: {correct_ans}")
                                
                                st.write(f"*{q['explanation']}*")
                                st.divider()
                            
                            # Reset quiz
                            st.session_state.current_quiz = None
                            st.session_state.quiz_answers = {}
                        else:
                            st.error("Failed to submit quiz")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("Cancel Quiz ❌", use_container_width=True):
                st.session_state.current_quiz = None
                st.session_state.quiz_answers = {}
                st.rerun()

# ===== PROGRESS TAB =====
with tab3:
    st.header("Your Learning Progress")
    
    if st.button("Refresh Progress 🔄"):
        st.rerun()
    
    try:
        response = requests.get(
            f"{API_URL}/progress/{st.session_state.student_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Topic Performance
            if data["topic_performance"]:
                st.subheader("📊 Topic Mastery")
                
                topics = list(data["topic_performance"].keys())
                scores = [data["topic_performance"][t]*100 for t in topics]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=topics,
                        y=scores,
                        marker_color='lightblue',
                        text=[f"{s:.0f}%" for s in scores],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    yaxis_title="Mastery %",
                    yaxis_range=[0, 100],
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Take some quizzes to see your progress!")
            
            # Weak Topics
            st.subheader("⚠️ Areas for Improvement")
            if data["weak_topics"]:
                for topic in data["weak_topics"]:
                    st.warning(f"📌 {topic}")
            else:
                st.success("✅ No weak topics - Great job!")
            
            # Quiz History
            if data["quiz_history"]:
                st.subheader("📈 Learning Progress Over Time")
                
                history = data["quiz_history"][-10:]  # Last 10
                dates = [h["timestamp"][:10] for h in history]
                scores = [h["score"]*100 for h in history]
                
                fig = go.Figure(data=[
                    go.Scatter(
                        x=list(range(len(scores))),
                        y=scores,
                        mode='lines+markers',
                        line=dict(color='green', width=2),
                        marker=dict(size=8)
                    )
                ])
                fig.update_layout(
                    xaxis_title="Quiz Number",
                    yaxis_title="Score %",
                    yaxis_range=[0, 100],
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Interactions", data["total_interactions"])
            with col2:
                st.metric("Topics Studied", len(data["topic_performance"]))
            with col3:
                if data["quiz_history"]:
                    avg_score = sum(q["score"] for q in data["quiz_history"]) / len(data["quiz_history"])
                    st.metric("Average Score", f"{avg_score*100:.0f}%")
                else:
                    st.metric("Average Score", "N/A")
        
        else:
            st.error("Could not load progress data")
    
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown("*Developed by Mohd Anas (24MAM023) | Supervisor: Prof. Jahiruddin*")