import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List
import requests

# Import basic utilities
from utils.fluid_calculator import FluidCalculator

# Page configuration
st.set_page_config(
    page_title="KKH Nursing Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple PDF text extractor (without ML dependencies)
class SimplePDFProcessor:
    def __init__(self):
        self.chunks = []
    
    def extract_simple_text(self, pdf_path: str):
        """Simple text extraction without embeddings"""
        try:
            import pdfplumber
            text_chunks = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Simple chunking by paragraphs
                        paragraphs = text.split('\n\n')
                        for para in paragraphs:
                            if len(para.strip()) > 50:
                                text_chunks.append(para.strip())
            return text_chunks
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            return []
    
    def simple_search(self, query: str, chunks: List[str]) -> str:
        """Simple keyword-based search"""
        query_words = query.lower().split()
        best_chunk = ""
        best_score = 0
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        return best_chunk if best_chunk else "No relevant information found."

# Simple LLM client for OpenAI
class SimpleOpenAIClient:
    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
    
    def _get_api_key(self):
        try:
            return st.secrets["OPENAI_API_KEY"]
        except:
            return os.getenv("OPENAI_API_KEY")
    
    def generate_response(self, question: str, context: str) -> Dict:
        if not self.api_key:
            return {
                "success": False,
                "response": "Please configure OpenAI API key in Streamlit secrets to use AI features."
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful nursing chatbot for KKH Hospital. Answer based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context}\n\nQuestion: {question}"
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"]
                }
            else:
                return {
                    "success": False,
                    "response": f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {str(e)}"
            }

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
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'knowledge_chunks' not in st.session_state:
        st.session_state.knowledge_chunks = []
    
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = SimplePDFProcessor()
    
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = SimpleOpenAIClient()

# Load knowledge base
@st.cache_data
def load_knowledge_base():
    """Load PDF content without embeddings"""
    pdf_path = "data/KKH Information file.pdf"
    
    if not os.path.exists(pdf_path):
        st.error(f"PDF file not found: {pdf_path}")
        return []
    
    processor = SimplePDFProcessor()
    chunks = processor.extract_simple_text(pdf_path)
    return chunks

# Chat interface
def display_chat_interface():
    st.markdown('<div class="main-header"><h1>🏥 KKH Nursing Chatbot</h1><p>Your AI assistant for nursing information and support</p></div>', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><strong>KKH Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Ask me anything about nursing:", height=100)
        
        col1, col2 = st.columns([1, 1])
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
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Find relevant context
    relevant_context = st.session_state.pdf_processor.simple_search(
        user_input, 
        st.session_state.knowledge_chunks
    )
    
    # Generate response
    with st.spinner("Generating response..."):
        response = st.session_state.llm_client.generate_response(user_input, relevant_context)
    
    # Add assistant response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response.get("response", "Sorry, I couldn't generate a response."),
        "timestamp": datetime.now()
    })
    
    st.rerun()

# Fluid calculator
def display_fluid_calculator():
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("💧 Pediatric Fluid Calculator")
    
    with st.sidebar.form("fluid_calculator"):
        weight = st.number_input("Weight (kg)", min_value=0.1, max_value=150.0, value=10.0, step=0.1)
        age = st.number_input("Age (years)", min_value=0.0, max_value=18.0, value=5.0, step=0.1)
        
        scenario = st.selectbox(
            "Select Scenario:",
            ["Maintenance", "Resuscitation", "Mild Dehydration (5%)", "Moderate Dehydration (10%)", "Severe Dehydration (15%)"]
        )
        
        if st.form_submit_button("Calculate", type="primary"):
            calculator = FluidCalculator()
            
            if scenario == "Maintenance":
                result = calculator.maintenance_holliday_segar(weight)
            elif scenario == "Resuscitation":
                result = calculator.resuscitation_fluid(weight)
            else:
                dehydration_percent = {"Mild Dehydration (5%)": 5, "Moderate Dehydration (10%)": 10, "Severe Dehydration (15%)": 15}
                result = calculator.deficit_calculation(weight, dehydration_percent[scenario])
            
            if "error" not in result:
                st.sidebar.markdown('<div class="fluid-result">', unsafe_allow_html=True)
                st.sidebar.markdown(f"**{result['method']}**")
                
                if "ml_per_day" in result:
                    st.sidebar.markdown(f"• **Daily:** {result['ml_per_day']} mL/day")
                    st.sidebar.markdown(f"• **Hourly:** {result['ml_per_hour']} mL/hour")
                
                if "bolus_ml" in result:
                    st.sidebar.markdown(f"• **Bolus:** {result['bolus_ml']} mL")
                
                st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Simple quiz
def display_simple_quiz():
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("📚 Nursing Knowledge Quiz")
    
    sample_questions = [
        {
            "question": "What is the normal heart rate range for a newborn?",
            "options": ["60-100 bpm", "100-150 bpm", "120-160 bpm", "150-200 bpm"],
            "answer": "120-160 bpm"
        },
        {
            "question": "Pediatric patients require weight-based medication dosing.",
            "options": ["True", "False"],
            "answer": "True"
        }
    ]
    
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
    
    if not st.session_state.quiz_started:
        if st.sidebar.button("Start Quiz", type="primary"):
            st.session_state.quiz_started = True
            st.session_state.quiz_questions = sample_questions
            st.rerun()
    else:
        if st.session_state.quiz_index < len(sample_questions):
            q = sample_questions[st.session_state.quiz_index]
            st.sidebar.markdown(f"**Question {st.session_state.quiz_index + 1}:**")
            st.sidebar.markdown(q["question"])
            
            with st.sidebar.form(f"quiz_{st.session_state.quiz_index}"):
                answer = st.radio("Select answer:", q["options"])
                if st.form_submit_button("Next"):
                    if answer == q["answer"]:
                        st.session_state.quiz_score += 1
                    st.session_state.quiz_index += 1
                    st.rerun()
        else:
            st.sidebar.success(f"Quiz Complete! Score: {st.session_state.quiz_score}/{len(sample_questions)}")
            if st.sidebar.button("Restart Quiz"):
                st.session_state.quiz_started = False
                st.session_state.quiz_score = 0
                st.session_state.quiz_index = 0
                st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Main application
def main():
    load_css()
    initialize_session_state()
    
    # Load knowledge base
    if not st.session_state.knowledge_chunks:
        with st.spinner("Loading knowledge base..."):
            st.session_state.knowledge_chunks = load_knowledge_base()
    
    # Display interface
    display_chat_interface()
    display_fluid_calculator()
    display_simple_quiz()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**KKH Nursing Chatbot v1.0**")
    st.sidebar.caption("Built with ❤️ for KK Women's and Children's Hospital")

if __name__ == "__main__":
    main()
