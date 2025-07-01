import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List
import time

# Import custom utilities
from utils.pdf_processor import PDFProcessor, QuizGenerator
from utils.fluid_calculator import FluidCalculator

# Try to import the appropriate LLM client
try:
    from utils.llm_client import LLMClient
    USE_LOCAL_LLM = True
except:
    USE_LOCAL_LLM = False

try:
    from utils.cloud_llm_client import CloudLLMClient
    USE_CLOUD_LLM = True
except:
    USE_CLOUD_LLM = False

# Page configuration
st.set_page_config(
    page_title="KKH Nursing Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
def load_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #2a5298;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #1976d2;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        border-left-color: #388e3c;
    }
    
    .fluid-result {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 0.5rem 0;
    }
    
    .quiz-container {
        background-color: #fafafa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .score-display {
        background: linear-gradient(45deg, #4caf50, #8bc34a);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
    
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    
    if 'quiz_index' not in st.session_state:
        st.session_state.quiz_index = 0
    
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = []
    
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    
    # Initialize appropriate LLM client
    if 'llm_client' not in st.session_state:
        if USE_CLOUD_LLM:
            st.session_state.llm_client = CloudLLMClient()
            st.session_state.llm_type = "cloud"
        elif USE_LOCAL_LLM:
            st.session_state.llm_client = LLMClient()
            st.session_state.llm_type = "local"
        else:
            st.session_state.llm_client = None
            st.session_state.llm_type = "none"
    
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()

# Simple fallback LLM for when no client is available
class FallbackLLM:
    def generate_response(self, question, context):
        return {
            "success": True,
            "response": f"Based on the available context: {context[:200]}...\n\nI can provide information from the knowledge base, but for a more interactive experience, please configure an AI model (LM Studio locally or OpenAI API for cloud deployment)."
        }
    
    def test_connection(self):
        return {
            "connected": False,
            "status": "No AI model configured - using fallback responses"
        }

# Knowledge base management
@st.cache_data
def load_or_create_knowledge_base():
    """Load existing knowledge base or create new one"""
    pdf_path = "data/KKH Information file.pdf"
    knowledge_path = "embedded_knowledge.json"
    
    if not os.path.exists(pdf_path):
        st.error(f"PDF file not found: {pdf_path}")
        return None
    
    try:
        processor = PDFProcessor()
        
        # Check if knowledge base exists and is recent
        if os.path.exists(knowledge_path):
            knowledge_base = processor.load_knowledge_base(knowledge_path)
            if knowledge_base:
                return knowledge_base
        
        # Create new knowledge base
        with st.spinner("Processing PDF and creating knowledge base... This may take a few minutes."):
            knowledge_base = processor.save_knowledge_base(pdf_path, knowledge_path)
        
        return knowledge_base
    
    except Exception as e:
        st.error(f"Error processing knowledge base: {str(e)}")
        st.info("This might be due to missing dependencies. For local development, ensure all packages in requirements.txt are installed.")
        return None

# Display setup instructions
def display_setup_info():
    """Display setup information if no LLM is configured"""
    if st.session_state.llm_client is None:
        st.markdown("""
        <div class="info-box">
        <h4>🔧 Setup Required</h4>
        <p><strong>For Local Development:</strong></p>
        <ul>
        <li>Install LM Studio and load OpenHermes-2.5-Mistral-7B model</li>
        <li>Start LM Studio server on localhost:1234</li>
        <li>Install requirements: <code>pip install -r requirements.txt</code></li>
        </ul>
        
        <p><strong>For Cloud Deployment:</strong></p>
        <ul>
        <li>Add OpenAI API key to Streamlit secrets</li>
        <li>The app will automatically use cloud API</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# Chat functionality
def display_chat_interface():
    """Display the main chat interface"""
    st.markdown('<div class="main-header"><h1>🏥 KKH Nursing Chatbot</h1><p>Your AI assistant for nursing information and support</p></div>', unsafe_allow_html=True)
    
    # Display setup info if needed
    if st.session_state.llm_type == "none":
        display_setup_info()
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>KKH Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask me anything about nursing, patient care, or hospital procedures:",
            height=100,
            placeholder="Type your question here..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            submit_button = st.form_submit_button("Send", type="primary")
        
        with col2:
            clear_button = st.form_submit_button("Clear Chat")
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        if submit_button and user_input.strip():
            handle_user_input(user_input.strip())

def handle_user_input(user_input: str):
    """Process user input and generate response"""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Get relevant context from knowledge base
    if st.session_state.knowledge_base:
        try:
            relevant_context = st.session_state.pdf_processor.find_relevant_chunk(
                user_input, 
                st.session_state.knowledge_base
            )
        except Exception as e:
            relevant_context = "Error retrieving context from knowledge base."
    else:
        relevant_context = "Knowledge base not available."
    
    # Generate response using LLM
    with st.spinner("Generating response..."):
        if st.session_state.llm_client:
            llm_response = st.session_state.llm_client.generate_response(
                user_input, 
                relevant_context
            )
        else:
            # Use fallback
            fallback = FallbackLLM()
            llm_response = fallback.generate_response(user_input, relevant_context)
    
    if llm_response.get("success", False):
        response_text = llm_response["response"]
    else:
        response_text = llm_response.get("response", "Sorry, I couldn't generate a response.")
    
    # Add assistant response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now(),
        "context_used": relevant_context[:100] + "..." if len(relevant_context) > 100 else relevant_context
    })
    
    st.rerun()

# Fluid calculator sidebar
def display_fluid_calculator():
    """Display fluid calculator in sidebar"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("💧 Pediatric Fluid Calculator")
    
    with st.sidebar.form("fluid_calculator"):
        weight = st.number_input("Weight (kg)", min_value=0.1, max_value=150.0, value=10.0, step=0.1)
        age = st.number_input("Age (years)", min_value=0.0, max_value=18.0, value=5.0, step=0.1)
        
        scenario = st.selectbox(
            "Select Scenario:",
            [
                "Maintenance",
                "Resuscitation", 
                "Mild Dehydration (5%)",
                "Moderate Dehydration (10%)",
                "Severe Dehydration (15%)"
            ]
        )
        
        calculate_button = st.form_submit_button("Calculate", type="primary")
        
        if calculate_button:
            calculate_fluids(weight, age, scenario)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def calculate_fluids(weight: float, age: float, scenario: str):
    """Calculate and display fluid requirements"""
    calculator = FluidCalculator()
    
    if scenario == "Maintenance":
        result = calculator.maintenance_holliday_segar(weight)
    elif scenario == "Resuscitation":
        result = calculator.resuscitation_fluid(weight)
    elif scenario in ["Mild Dehydration (5%)", "Moderate Dehydration (10%)", "Severe Dehydration (15%)"]:
        result = calculator.dehydration_assessment(weight, age, scenario)
    else:
        st.sidebar.error("Unknown scenario selected")
        return
    
    if "error" in result:
        st.sidebar.error(result["error"])
        return
    
    # Display results
    st.sidebar.markdown('<div class="fluid-result">', unsafe_allow_html=True)
    st.sidebar.markdown(f"**{result['method']}**")
    
    if "ml_per_day" in result:
        st.sidebar.markdown(f"• **Daily:** {result['ml_per_day']} mL/day")
        st.sidebar.markdown(f"• **Hourly:** {result['ml_per_hour']} mL/hour")
    
    if "bolus_ml" in result:
        st.sidebar.markdown(f"• **Bolus:** {result['bolus_ml']} mL")
    
    if "total_ml_per_hour" in result:
        st.sidebar.markdown(f"• **Total/hour:** {result['total_ml_per_hour']} mL/hour")
        st.sidebar.markdown(f"• **Total/day:** {result['total_ml_per_day']} mL/day")
    
    st.sidebar.markdown(f"*{result.get('details', '')}*")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Simplified quiz functionality that works without full PDF processing
def display_simple_quiz():
    """Display a simplified quiz that doesn't require PDF processing"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("📚 Nursing Knowledge Quiz")
    
    # Sample questions for demonstration
    sample_questions = [
        {
            "question": "What is the normal heart rate range for a newborn?",
            "options": ["60-100 bpm", "100-150 bpm", "120-160 bpm", "150-200 bpm"],
            "answer": "120-160 bpm",
            "type": "multiple_choice"
        },
        {
            "question": "Pediatric patients require weight-based medication dosing.",
            "options": ["True", "False"],
            "answer": "True",
            "type": "true_false"
        },
        {
            "question": "What is the first step in pediatric resuscitation?",
            "answer": "Assess responsiveness and breathing",
            "type": "open_ended"
        }
    ]
    
    if not st.session_state.quiz_started:
        if st.sidebar.button("Start Sample Quiz", type="primary"):
            st.session_state.quiz_questions = sample_questions
            st.session_state.quiz_started = True
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_answers = []
            st.rerun()
    else:
        display_current_question()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def display_current_question():
    """Display current quiz question"""
    if st.session_state.quiz_index >= len(st.session_state.quiz_questions):
        display_quiz_results()
        return
    
    current_q = st.session_state.quiz_questions[st.session_state.quiz_index]
    total_questions = len(st.session_state.quiz_questions)
    
    st.sidebar.markdown(f"**Question {st.session_state.quiz_index + 1} of {total_questions}**")
    st.sidebar.markdown(f"**{current_q['question']}**")
    
    with st.sidebar.form(f"quiz_question_{st.session_state.quiz_index}"):
        if current_q["type"] == "true_false":
            user_answer = st.radio("Select your answer:", current_q["options"], key=f"answer_{st.session_state.quiz_index}")
        elif current_q["type"] == "multiple_choice":
            user_answer = st.radio("Select your answer:", current_q["options"], key=f"answer_{st.session_state.quiz_index}")
        else:  # open_ended
            user_answer = st.text_area("Your answer:", key=f"answer_{st.session_state.quiz_index}")
        
        col1, col2 = st.columns(2)
        with col1:
            next_button = st.form_submit_button("Next")
        with col2:
            skip_button = st.form_submit_button("Skip")
        
        if next_button or skip_button:
            # Score the answer
            if user_answer and user_answer.strip():
                if current_q["type"] in ["true_false", "multiple_choice"]:
                    if user_answer == current_q["answer"]:
                        st.session_state.quiz_score += 1
                        correct = True
                    else:
                        correct = False
                else:  # open_ended - give partial credit
                    st.session_state.quiz_score += 0.5
                    correct = True
            else:
                correct = False
            
            st.session_state.quiz_answers.append({
                "question": current_q["question"],
                "user_answer": user_answer,
                "correct_answer": current_q["answer"],
                "correct": correct
            })
            
            st.session_state.quiz_index += 1
            st.rerun()

def display_quiz_results():
    """Display final quiz results"""
    total_questions = len(st.session_state.quiz_questions)
    percentage = (st.session_state.quiz_score / total_questions) * 100 if total_questions > 0 else 0
    
    st.sidebar.markdown(f'<div class="score-display">Quiz Complete!<br>Score: {st.session_state.quiz_score:.1f}/{total_questions}<br>({percentage:.1f}%)</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("Retake Quiz"):
        st.session_state.quiz_started = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_answers = []
        st.rerun()

# System status sidebar
def display_system_status():
    """Display system status information"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("🔧 System Status")
    
    # LLM connection status
    if st.sidebar.button("Test AI Connection"):
        with st.sidebar:
            with st.spinner("Testing connection..."):
                if st.session_state.llm_client:
                    status = st.session_state.llm_client.test_connection()
                else:
                    status = {"connected": False, "status": "No AI client configured"}
        
        if status["connected"]:
            st.sidebar.success("✅ AI Model Connected")
        else:
            st.sidebar.error(f"❌ {status['status']}")
    
    # Display LLM type
    if st.session_state.llm_type == "local":
        st.sidebar.info("🏠 Using Local LM Studio")
    elif st.session_state.llm_type == "cloud":
        st.sidebar.info("☁️ Using Cloud API")
    else:
        st.sidebar.warning("⚠️ No AI Model Configured")
    
    # Knowledge base status
    if st.session_state.knowledge_base:
        metadata = st.session_state.knowledge_base.get("metadata", {})
        st.sidebar.success("✅ Knowledge Base Loaded")
        st.sidebar.caption(f"Total chunks: {metadata.get('total_chunks', 'Unknown')}")
    else:
        st.sidebar.warning("⚠️ Knowledge Base Not Available")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Main application
def main():
    """Main application function"""
    # Load CSS and initialize
    load_css()
    initialize_session_state()
    
    # Load knowledge base
    if not st.session_state.knowledge_base:
        st.session_state.knowledge_base = load_or_create_knowledge_base()
    
    # Main content area
    display_chat_interface()
    
    # Sidebar content
    display_fluid_calculator()
    display_simple_quiz()
    display_system_status()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**KKH Nursing Chatbot v1.0**")
    st.sidebar.caption("Built with ❤️ for KK Women's and Children's Hospital")

if __name__ == "__main__":
    main()
