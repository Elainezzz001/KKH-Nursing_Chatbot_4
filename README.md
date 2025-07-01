# KKH Nursing Chatbot

A comprehensive Streamlit-based medical chatbot designed for KK Women's and Children's Hospital nursing staff.

## Features

### 🤖 AI-Powered Chatbot
- PDF knowledge base processing using `pdfplumber`
- Semantic search with `intfloat/multilingual-e5-large-instruct` embeddings
- Integration with OpenHermes-2.5-Mistral-7B via LM Studio
- Contextual responses based on hospital documentation

### 💧 Pediatric Fluid Calculator
- Holliday-Segar maintenance fluid calculation
- Resuscitation fluid calculations (20mL/kg bolus)
- Dehydration deficit calculations (5%, 10%, 15%)
- Real-time calculations in mL/day and mL/hour

### 📚 Nursing Knowledge Quiz
- Auto-generated questions from PDF content
- Multiple choice, True/False, and open-ended questions
- Score tracking and detailed result analysis
- Retake functionality

### 💬 Chat Interface
- Clean, modern UI with custom CSS styling
- Chat history persistence
- Real-time responses
- Error handling and connection status

## Setup Instructions

### Prerequisites
1. **LM Studio** - Download and install from [LM Studio](https://lmstudio.ai/)
2. **Python 3.8+** - Ensure Python is installed
3. **Git** - For cloning the repository

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd "FYP Nursing Chatbot 4"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up LM Studio:**
   - Download and load the OpenHermes-2.5-Mistral-7B model
   - Start the local server on `localhost:1234`
   - Ensure the model is running and accessible

4. **Prepare the knowledge base:**
   - Ensure `data/KKH Information file.pdf` exists
   - The app will automatically process the PDF on first run

### Running the Application

1. **Start LM Studio server** (must be running before starting the app)

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **Access the application:**
   - Open your browser to `http://localhost:8501`
   - Wait for the PDF processing to complete (first run only)

## Project Structure

```
FYP Nursing Chatbot 4/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── data/
│   └── KKH Information file.pdf # Knowledge base PDF
├── logo/
│   └── photo_2025-06-16_15-57-21.jpg # Hospital logo
├── utils/
│   ├── __init__.py            # Package initialization
│   ├── pdf_processor.py       # PDF processing and embeddings
│   ├── fluid_calculator.py    # Pediatric fluid calculations
│   └── llm_client.py          # LM Studio API client
└── embedded_knowledge.json    # Generated knowledge base (auto-created)
```

## Usage Guide

### Chat Interface
1. Type your nursing-related questions in the chat input
2. The system will find relevant information from the PDF knowledge base
3. Receive contextual answers from the AI model
4. Chat history is preserved during your session

### Fluid Calculator
1. Navigate to the sidebar "Pediatric Fluid Calculator"
2. Enter patient weight (kg) and age (years)
3. Select the appropriate scenario:
   - **Maintenance**: Holliday-Segar method
   - **Resuscitation**: 20mL/kg bolus
   - **Dehydration**: Choose severity (5%, 10%, 15%)
4. Click "Calculate" to see results in mL/day and mL/hour

### Knowledge Quiz
1. Click "Start Quiz" in the sidebar
2. Answer 15 auto-generated questions
3. Questions include multiple choice, true/false, and open-ended
4. View your score and detailed results
5. Retake the quiz anytime

## Deployment on Streamlit.io

### Preparation
1. **Create a GitHub repository** with your code
2. **Update requirements.txt** to include only necessary packages
3. **Add secrets** for any API keys (if needed)

### Deploy Steps
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file path: `app.py`
5. Add any necessary secrets in the Advanced settings

### Important Notes for Deployment
- **LM Studio Integration**: The local LM Studio integration won't work on Streamlit.io
- **Alternative for Cloud**: Consider using OpenAI API or Hugging Face Inference API
- **PDF Processing**: May take longer on cloud due to resource limitations
- **File Persistence**: Use Streamlit's caching mechanisms effectively

### Cloud Alternative Setup
To make this work on Streamlit.io, you'll need to:

1. **Replace LM Studio** with a cloud-based LLM API
2. **Update `utils/llm_client.py`** to use OpenAI API or similar
3. **Add API keys** to Streamlit secrets
4. **Test locally** before deploying

## Troubleshooting

### Common Issues

1. **LM Studio Connection Failed**
   - Ensure LM Studio is running on localhost:1234
   - Check that OpenHermes model is loaded
   - Verify no firewall blocking

2. **PDF Processing Slow**
   - Large PDFs take time to process
   - Embedding generation is compute-intensive
   - Wait for "Knowledge base loaded" confirmation

3. **Import Errors**
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+)

4. **Quiz Not Loading**
   - Wait for PDF processing to complete
   - Ensure knowledge base is successfully created

### Performance Tips
- Keep PDF size reasonable (< 50MB)
- LM Studio works better with sufficient RAM (8GB+)
- Use SSD storage for faster embedding processing

## Customization

### Adding New Features
- Extend `utils/` modules for new functionality
- Add new sidebar sections in `app.py`
- Customize CSS styling in the `load_css()` function

### Modifying Calculations
- Update `utils/fluid_calculator.py` for new formulas
- Add new scenarios or age-specific calculations

### Changing AI Model
- Update `utils/llm_client.py` for different LLM endpoints
- Modify system prompts for specialized responses

## License

This project is developed for educational and medical training purposes at KK Women's and Children's Hospital.

## Support

For technical support or questions:
- Check the troubleshooting section
- Review Streamlit documentation
- Ensure all dependencies are correctly installed
