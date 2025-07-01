# Installation and Deployment Guide

## 🚀 Quick Start

### Option 1: Windows (Automated)
1. Double-click `start.bat`
2. Wait for dependencies to install
3. Access the app at `http://localhost:8501`

### Option 2: Manual Installation

#### Prerequisites
- Python 3.8 or higher
- Git (optional)
- 8GB+ RAM recommended for local AI model

#### Steps
1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd "FYP Nursing Chatbot 4"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up LM Studio (for local AI)**
   - Download [LM Studio](https://lmstudio.ai/)
   - Load OpenHermes-2.5-Mistral-7B model
   - Start server on localhost:1234

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🌐 Deployment on Streamlit.io

### Preparation
1. **Create GitHub repository** with your code
2. **Remove/modify local-only features**:
   - LM Studio integration won't work on cloud
   - Large file processing may timeout

### Deploy Steps
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file: `app_deployment.py` (cloud-optimized version)
5. Add secrets for OpenAI API:
   ```toml
   OPENAI_API_KEY = "your-api-key"
   ```

### Cloud-Specific Configuration
For cloud deployment, use `app_deployment.py` which includes:
- Fallback AI responses without local model
- Simplified quiz functionality
- Better error handling for missing dependencies
- OpenAI API integration

## 🔧 Configuration Options

### Local Development
- Use `app.py` for full functionality
- Requires LM Studio with OpenHermes model
- Full PDF processing and embedding generation

### Cloud Deployment
- Use `app_deployment.py` for cloud compatibility
- Requires OpenAI API key
- Simplified features to work within cloud constraints

## 📋 Feature Checklist

### Core Features
- ✅ PDF knowledge base loading
- ✅ Semantic search and embeddings
- ✅ Pediatric fluid calculator
- ✅ Nursing knowledge quiz
- ✅ Chat interface with history

### AI Integration
- ✅ Local LM Studio support (OpenHermes)
- ✅ Cloud OpenAI API support
- ✅ Fallback responses without AI

### Deployment Ready
- ✅ Streamlit.io compatible
- ✅ Environment variable support
- ✅ Error handling and graceful degradation

## 🐛 Troubleshooting

### Common Issues

1. **Import errors during startup**
   ```bash
   pip install -r requirements.txt
   ```

2. **LM Studio connection failed**
   - Ensure LM Studio is running on port 1234
   - Check firewall settings
   - Verify OpenHermes model is loaded

3. **PDF processing takes too long**
   - Large PDFs require more time
   - Consider chunking large documents
   - Use cloud deployment for better resources

4. **Quiz not generating questions**
   - Wait for PDF processing to complete
   - Check if knowledge base was created successfully
   - Use sample quiz in deployment version

### Performance Tips
- Close other applications to free RAM
- Use SSD storage for faster file processing
- Ensure stable internet for cloud APIs

## 📈 Scaling and Customization

### Adding New Features
1. **Medical calculators**: Extend `utils/fluid_calculator.py`
2. **AI models**: Modify `utils/llm_client.py`
3. **PDF processors**: Update `utils/pdf_processor.py`
4. **UI components**: Add to main `app.py`

### Custom Styling
- Modify CSS in `load_css()` function
- Add new color schemes
- Customize component layouts

### Data Sources
- Replace PDF in `data/` folder
- Update knowledge base processing
- Add multiple document support

## 🔒 Security Considerations

### API Keys
- Never commit API keys to repository
- Use environment variables or Streamlit secrets
- Rotate keys regularly

### Data Privacy
- Medical information should be handled securely
- Consider HIPAA compliance for real deployment
- Implement user authentication if needed

### Production Deployment
- Use HTTPS in production
- Implement rate limiting
- Add logging and monitoring
- Regular security updates

## 📞 Support

For technical issues:
1. Check this guide first
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Test with minimal configuration

For feature requests or bugs:
- Document the issue clearly
- Include error messages
- Specify your environment (local/cloud)

## 🔄 Updates and Maintenance

### Regular Updates
- Update Python packages: `pip install -r requirements.txt --upgrade`
- Update AI models in LM Studio
- Refresh PDF knowledge base as needed

### Monitoring
- Check application logs
- Monitor resource usage
- Test all features regularly
- Backup configuration and data
