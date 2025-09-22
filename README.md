# Beneish M-Score Financial Analysis Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)]()

A sophisticated desktop application for detecting potential earnings manipulation in financial statements using the Beneish M-Score model. This tool combines AI-powered data extraction with proven financial analysis techniques to help auditors, analysts, and investors assess the likelihood of earnings manipulation.

## 🎯 What is the Beneish M-Score?

The Beneish M-Score is a mathematical model created by Professor Messod Beneish that uses eight financial ratios to identify companies that may have manipulated their earnings. A score greater than -1.78 suggests a higher probability of earnings manipulation.

### The Eight Key Ratios:
1. **DSRI** - Days Sales in Receivables Index
2. **GMI** - Gross Margin Index  
3. **AQI** - Asset Quality Index
4. **SGI** - Sales Growth Index
5. **DEPI** - Depreciation Index
6. **SGAI** - Sales General and Administrative Expenses Index
7. **LVGI** - Leverage Index
8. **TATA** - Total Accruals to Total Assets

## ✨ Key Features

### 🤖 AI-Powered Analysis
- **Multiple AI Providers**: Support for OpenAI GPT, Anthropic Claude, and Google Gemini
- **Intelligent Data Extraction**: Automatically identifies and extracts financial metrics from documents
- **Context-Aware Processing**: Understands financial statement structure and terminology

### 📄 Multi-Format Support
- **PDF Processing**: Extract data from financial statement PDFs
- **Excel Integration**: Direct import from .xlsx and .xls files
- **CSV Support**: Import structured financial data
- **Smart Recognition**: Automatically detects data format and structure

### 🎨 User-Friendly Interface
- **Modern Desktop App**: Built with Flet for cross-platform compatibility
- **Multilingual Support**: Available in English and Arabic
- **Intuitive Navigation**: Clean, professional interface design
- **Real-time Progress**: Live updates during analysis process

### 📊 Comprehensive Analysis
- **Risk Assessment**: Clear low/high risk categorization
- **Detailed Explanations**: Educational content for each financial ratio
- **Results Export**: Copy extracted data for further analysis
- **Visual Indicators**: Color-coded risk levels and progress tracking

## 🚀 Quick Start Guide

### For Non-Technical Users

#### Step 1: Installation
1. Ensure you have Python 3.8 or higher installed on your computer
2. Download the project files to your computer
3. Open a command prompt/terminal in the project folder
4. Run: `pip install -r requirements.txt`

#### Step 2: Get API Keys
You'll need at least one API key from these providers:
- **OpenAI**: Visit [platform.openai.com](https://platform.openai.com) → Create account → Generate API key
- **Anthropic**: Visit [console.anthropic.com](https://console.anthropic.com) → Create account → Generate API key  
- **Google Gemini**: Visit [ai.google.dev](https://ai.google.dev) → Create account → Generate API key

#### Step 3: Configuration
1. Create a file named `.env` in the project folder
2. Add your API key(s):
```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
```

#### Step 4: Run the Application
1. In the command prompt, type: `python main.py`
2. The application window will open
3. Go to Settings (gear icon) to configure your AI provider
4. Upload your financial statement file
5. Wait for analysis to complete
6. Review the results and M-Score assessment

### For Technical Users

#### Prerequisites
- Python 3.8+
- pip package manager
- API key for at least one supported LLM provider

#### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Beneish_MScore

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

#### Environment Configuration
Create a `.env` file with the following variables:
```bash
# Required: At least one API key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GOOGLE_GEMINI_API_KEY=...  # Alternative for Gemini

# Optional: Default configurations
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4
DEFAULT_LANGUAGE=en
```

## 📖 User Guide

### Basic Workflow

1. **Launch Application**
   - Run `python main.py`
   - The main interface will appear

2. **Configure Settings** (First Time)
   - Click the settings icon (⚙️) in the top-right
   - Select your preferred AI provider
   - Choose the AI model
   - Set your preferred language
   - Click "Save Settings"

3. **Upload Financial Data**
   - Click "Upload File" on the main screen
   - Select your financial statement (PDF, Excel, or CSV)
   - Supported formats: .pdf, .xlsx, .xls, .csv

4. **AI Analysis Process**
   - The system will automatically extract financial data
   - Progress indicators show the analysis status
   - This may take 30-120 seconds depending on file complexity

5. **Review Results**
   - View the calculated M-Score
   - Check the risk assessment (Low Risk < -1.78 < High Risk)
   - Examine individual ratio calculations
   - Read explanations for each financial ratio

6. **Export Data** (Optional)
   - Use the "Copy Data" button to export extracted financial metrics
   - Paste into Excel or other applications for further analysis

### Understanding the Results

#### M-Score Interpretation
- **Score < -1.78**: Lower probability of earnings manipulation
- **Score > -1.78**: Higher probability of earnings manipulation
- **Score > 0**: Significant red flags present

#### Individual Ratios
Each ratio compares current year to previous year metrics:
- **Values > 1.0**: Potential concern (varies by ratio)
- **Trend Analysis**: Look for multiple ratios showing deterioration
- **Context Matters**: Consider industry norms and economic conditions

### Troubleshooting

#### Common Issues

**"API Key Error"**
- Verify your API key is correctly entered in settings
- Check that the API key has sufficient credits/quota
- Ensure the selected provider matches your API key

**"File Processing Error"**
- Ensure the file contains financial statement data
- Try a different file format (PDF → Excel or vice versa)
- Check that financial data is clearly structured in the document

**"Incomplete Data Extraction"**
- The AI may not have found all required financial metrics
- Try uploading a more complete financial statement
- Consider manually entering missing data points

**"Application Won't Start"**
- Verify Python 3.8+ is installed: `python --version`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Ensure you're in the correct project directory

#### Getting Help
- Use the Help button (❓) in the application for built-in guidance
- Check the FAQ section within the app
- Review error messages for specific guidance

## 🏗️ Technical Architecture

### System Design
The application follows a Model-View-Controller (MVC) architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Views       │    │   Controllers   │    │     Models      │
│                 │    │                 │    │                 │
│ • main_view.py  │◄──►│ beneish_        │◄──►│ • beneish_      │
│ • results_view  │    │   controller.py │    │   models.py     │
│ • settings_view │    │                 │    │ • translation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Services     │
                       │                 │
                       │ • llm_service   │
                       │ • file_service  │
                       └─────────────────┘
```

### Key Components

#### Controllers (`controllers/`)
- **beneish_controller.py**: Main application controller, handles navigation and coordination

#### Models (`models/`)
- **beneish_models.py**: Core M-Score calculation logic and data structures
- **translation.py**: Multilingual support and localization

#### Views (`views/`)
- **main_view.py**: Primary user interface and file upload
- **results_view.py**: Results display and data visualization
- **settings_view.py**: Configuration and preferences management

#### Services (`services/`)
- **llm_service.py**: AI provider integration and data extraction
- **file_service.py**: File processing and format handling

#### Utilities (`utils/`)
- **config.py**: Environment configuration and settings management

### Dependencies

#### Core Framework
- **Flet**: Modern UI framework for Python desktop applications
- **Python 3.8+**: Core runtime environment

#### AI Integration
- **OpenAI**: GPT models for data extraction and analysis
- **Anthropic**: Claude models for advanced reasoning
- **Google Generative AI**: Gemini models for comprehensive analysis

#### File Processing
- **PyPDF2/pdfplumber**: PDF document processing
- **openpyxl**: Excel file handling (.xlsx, .xls)
- **pandas**: Data manipulation and CSV processing

#### Additional Libraries
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for API communications

## 🔧 Development

### Project Structure
```
Beneish_MScore/
├── controllers/           # Application controllers
│   └── beneish_controller.py
├── models/               # Data models and business logic
│   ├── beneish_models.py
│   └── translation.py
├── services/             # External service integrations
│   ├── llm_service.py
│   └── file_service.py
├── utils/                # Utility functions
│   └── config.py
├── views/                # UI components
│   ├── main_view.py
│   ├── results_view.py
│   └── settings_view.py
├── original/             # Research materials
├── project_summary/      # Documentation
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── .env                 # Environment configuration
└── README.md           # This file
```

### Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd Beneish_MScore
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

3. **Development Run**
```bash
python main.py
```

### Code Style Guidelines
- **Python**: Follow PEP 8 conventions
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Documentation**: Comprehensive docstrings for all public methods
- **Error Handling**: Robust exception handling with user-friendly messages

### Testing
- Manual testing procedures for UI components
- Integration testing for AI provider connections
- File processing validation across multiple formats
- Cross-platform compatibility testing

## 📚 Educational Resources

### Understanding Financial Ratios

#### DSRI (Days Sales in Receivables Index)
- **Purpose**: Measures changes in accounts receivable relative to sales
- **Red Flag**: Significant increase may indicate revenue manipulation
- **Calculation**: (Receivables/Sales)ₜ ÷ (Receivables/Sales)ₜ₋₁

#### GMI (Gross Margin Index)
- **Purpose**: Compares gross margins between periods
- **Red Flag**: Declining margins may pressure management to manipulate
- **Calculation**: Gross Marginₜ₋₁ ÷ Gross Marginₜ

#### AQI (Asset Quality Index)
- **Purpose**: Measures changes in asset quality
- **Red Flag**: Increase in non-current assets other than PPE
- **Calculation**: Asset Qualityₜ ÷ Asset Qualityₜ₋₁

### Academic Background
The Beneish M-Score model was developed by Professor Messod Beneish at Indiana University. The model has been extensively validated in academic research and is widely used by:
- External auditors for risk assessment
- Investment analysts for due diligence
- Regulatory bodies for enforcement actions
- Academic researchers studying earnings management

### Practical Applications
- **Investment Analysis**: Screen potential investments for earnings quality
- **Audit Planning**: Identify high-risk clients requiring additional scrutiny
- **Regulatory Review**: Detect patterns suggesting financial statement fraud
- **Academic Research**: Study earnings management trends and patterns

## 🤝 Contributing

We welcome contributions to improve the Beneish M-Score Financial Analysis Tool!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation for any changes
- Ensure cross-platform compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Professor Messod Beneish** for developing the M-Score model
- **Flet Team** for the excellent Python UI framework
- **AI Providers** (OpenAI, Anthropic, Google) for powerful language models
- **Open Source Community** for the various libraries and tools used

## 📞 Support

For support, questions, or feedback:
- Open an issue on GitHub
- Check the built-in help system (❓ button in the app)
- Review the FAQ section within the application

---

**Version**: v1.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready

*This tool is for educational and analytical purposes. Always consult with qualified financial professionals for investment decisions.*