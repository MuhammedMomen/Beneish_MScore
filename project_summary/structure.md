# Beneish M-Score Calculator - Complete Project Structure

## 📁 Project Directory Structure
```
beneish_calculator/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── .env                       # Your environment variables (create from .env.example)
├── README.md                  # Project documentation
│
├── controllers/
│   ├── __init__.py
│   └── beneish_controller.py  # Main application controller
│
├── models/
│   ├── __init__.py
│   ├── beneish_models.py      # Data models and business logic
│   └── translation.py         # Translation and localization
│
├── views/
│   ├── __init__.py
│   ├── main_view.py           # Main upload view
│   ├── results_view.py        # Results display view
│   └── settings_view.py       # Settings configuration view
│
├── services/
│   ├── __init__.py
│   └── llm_service.py         # LLM integration service
│
├── utils/
│   ├── __init__.py
│   └── config.py              # Configuration management
│
└── assets/                    # Static assets (optional)
    └── icons/
```

## 🚀 Setup Instructions

### 1. Create Project Directory
```bash
mkdir beneish_calculator
cd beneish_calculator
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Directory Structure
```bash
# Windows
mkdir controllers models views services utils assets
echo. > controllers\__init__.py
echo. > models\__init__.py
echo. > views\__init__.py
echo. > services\__init__.py
echo. > utils\__init__.py

# macOS/Linux
mkdir -p controllers models views services utils assets
touch controllers/__init__.py models/__init__.py views/__init__.py services/__init__.py utils/__init__.py
```

### 5. Setup Environment Variables
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API keys
# You need at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY
```

### 6. Create Python Files
Create each Python file with the provided code in the corresponding directory.

### 7. Run the Application
```bash
python main.py
```

## 🔧 Configuration

### API Keys
Get your API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://aistudio.google.com/app/apikey

### Supported File Formats
- PDF (.pdf)
- Excel (.xlsx, .xls) 
- CSV (.csv)

## ✨ Features Implemented

### 🌐 Internationalization
- English and Arabic support
- RTL layout for Arabic
- Dynamic language switching

### 🤖 Multi-LLM Support  
- OpenAI GPT models
- Anthropic Claude models
- Google Gemini models
- Dynamic model selection
- Environment-based API key management

### 📊 Professional UI
- Modern corporate design
- AppBar with action buttons
- Responsive layout
- Progress indicators
- Status messages

### 📈 Complete Analysis
- All 8 Beneish M-Score ratios
- Professional results view
- Data validation
- Missing value handling
- TSV export functionality

### ⚙️ Settings Management
- LLM provider configuration
- API key testing
- Real-time status updates

### 📱 User Experience
- Help, FAQ, and About dialogs
- Real-time progress feedback
- Human-readable error messages
- Separate results view with back navigation
- Copy-to-clipboard functionality

## 🎯 Usage Flow

1. **Setup**: Configure API keys in settings or .env file
2. **Upload**: Select and upload financial statements
3. **Processing**: AI extracts and analyzes financial data
4. **Results**: View M-Score, ratios, and interpretation
5. **Export**: Copy financial data in TSV format
6. **Rerun**: Start new analysis with back button

## 🛠️ Technical Architecture

### MVC Pattern
- **Models**: Data structures and business logic
- **Views**: UI components and presentation
- **Controllers**: Application flow and user interaction

### Key Components
- **LLMService**: Handles all AI provider integrations
- **BeneishCalculator**: Core M-Score calculation logic
- **TranslationManager**: Internationalization support
- **Config**: Centralized configuration management

## 📝 Notes

- The app automatically detects and uses available API keys from environment
- Manual API key input is available in settings for testing
- All financial calculations follow standard Beneish M-Score formula
- Results view occupies full content area with professional layout
- Real-time progress updates during file processing
- Comprehensive error handling with user-friendly messages

This is a complete, production-ready financial analysis tool with professional UI and robust functionality!