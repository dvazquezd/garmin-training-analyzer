# 🏃‍♂️ Garmin Training Analyzer

> AI-powered sports training analysis system that integrates Garmin Connect with LLMs (Claude, GPT-4, Gemini) to generate personalized reports and data-driven recommendations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Garmin Connect](https://img.shields.io/badge/Garmin-Connect-00A1E0.svg)](https://connect.garmin.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.txt)

## 🎯 Features

- 🔗 **Garmin Connect Integration**: Automatically extracts activities, health metrics, and body composition data
- 🤖 **Multi-LLM Support**: Works with Claude (Anthropic), GPT-4 (OpenAI), and Gemini (Google)
- 📊 **Intelligent Analysis**: Generates personalized insights about your training
- 📈 **Body Composition Tracking**: Monitor weight, body fat %, muscle mass, and more
- 📝 **Professional Reports**: Export in TXT, Markdown, and JSON formats
- ⚙️ **Highly Configurable**: Adjust analysis period, LLM models, and parameters
- 🎨 **Custom Prompts**: External prompt management for easy customization

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Garmin Library](#-garmin-library-reference)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Garmin Connect account
- API Key from at least one LLM provider (Anthropic/OpenAI/Google)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/garmin-training-analyzer.git
cd garmin-training-analyzer
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run the analyzer**
```bash
python training_analyzer.py
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Garmin Credentials
GARMIN_EMAIL=your_email@garmin.com
GARMIN_PASSWORD=your_password

# LLM Provider (anthropic, openai, google)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Analysis Parameters
ANALYSIS_DAYS=60           # Days to analyze (default: 30)
MAX_TOKENS=3000           # Max response tokens
TEMPERATURE=0.7           # Model temperature
```

### Switching LLM Providers

```bash
# For Claude (Anthropic)
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# For GPT-4 (OpenAI)
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o

# For Gemini (Google)
LLM_PROVIDER=google
GOOGLE_MODEL=gemini-2.0-flash-exp
```

### Custom Prompts

Edit the prompt files in `prompts/` directory:
- `system_prompt.txt` - Main analysis instructions
- `user_prompt_template.txt` - User data template

## 📁 Project Structure

```
garmin-training-analyzer/
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── garmin_client.py           # Garmin Connect client
│   ├── llm_analizer.py            # LLM analyzer
│   └── prompt_manager.py          # Prompt management
│
├── prompts/                       # External prompts
│   ├── system_prompt.txt          # System instructions
│   └── user_prompt_template.txt  # User data template
│
├── analysis_reports/              # Generated reports
│   ├── analisis_YYYYMMDD.txt      # Text format
│   ├── analisis_YYYYMMDD.md       # Markdown format
│   └── datos_YYYYMMDD.json        # JSON format
│
├── training_analyzer.py           # Main script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔌 Garmin Library Reference

This project uses [`garminconnect`](https://github.com/cyberjunky/python-garminconnect) Python library for Garmin Connect API integration.

### Key Methods Used

#### Authentication
```python
from garminconnect import Garmin

client = Garmin(email, password)
client.login()
```

#### Activities
```python
# Get activities by date range
activities = client.get_activities_by_date(
    start_date="2025-09-03",
    end_date="2025-11-02"
)

# Get activity details
details = client.get_activity(activity_id)

# Get activity splits
splits = client.get_activity_splits(activity_id)
```

#### Body Composition
```python
# Get body composition (weight, body fat %)
composition = client.get_body_composition(
    startdate="2025-09-03",
    enddate="2025-11-02"
)

# Returns dict with keys like:
# - dateWeightList: list of measurements
# - weight: in grams
# - bodyFat: percentage
# - muscleMass: in grams
# - bmi: Body Mass Index
```

#### Health Metrics
```python
# Daily stats
stats = client.get_stats("2025-11-02")

# Heart rate data
hr_data = client.get_heart_rates("2025-11-02")

# Body Battery
battery = client.get_body_battery("2025-11-02")
```

#### User Profile
```python
# Get user info
name = client.get_full_name()
units = client.get_unit_system()  # metric/imperial
```

### Important Notes

- **Body Composition Data**: Weight comes in **grams**, needs conversion to kg
- **Date Format**: Always use `YYYY-MM-DD` format
- **Rate Limiting**: Respect Garmin's API limits
- **Data Structure**: Some endpoints return nested dictionaries - check keys like `dateWeightList`

### Library Version

This project uses `garminconnect==0.2.30`. Check [changelog](https://github.com/cyberjunky/python-garminconnect/releases) for updates.

## 💻 Usage

### Basic Usage

```bash
# Run with default settings (last 30 days)
python training_analyzer.py
```

### Advanced Usage

```bash
# Analyze last 60 days
export ANALYSIS_DAYS=60
python training_analyzer.py

# Use different LLM
export LLM_PROVIDER=openai
python training_analyzer.py
```

### Output Files

The analyzer generates three types of reports in `analysis_reports/`:

1. **Text Report** (`analisis_YYYYMMDD_HHMMSS.txt`)
   - Plain text format
   - Easy to read
   - Includes metadata

2. **Markdown Report** (`analisis_YYYYMMDD_HHMMSS.md`)
   - Formatted with tables
   - Activity summaries
   - Proper sectioning

3. **JSON Data** (`datos_YYYYMMDD_HHMMSS.json`)
   - Raw data export
   - All activities
   - Body composition
   - Analysis text

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Diagnostics

```bash
# Verify Garmin connection and body composition data
python scripts/diagnostico_body_comp.py

# Verify prompt configuration
python -m src.prompt_manager

# Verify general configuration
python -m src.config
```

### Code Structure

- **GarminClient**: Handles all Garmin Connect API interactions
- **LLMAnalyzer**: Manages LLM integration and prompt processing
- **PromptManager**: External prompt file management
- **Config**: Centralized configuration management

## 📊 Example Report

```markdown
# 📊 Training Analysis Report

**Athlete:** David García
**Period:** Last 60 days (Sep 03 - Nov 02)
**Activities:** 45 workouts

## 1. EXECUTIVE SUMMARY
Your training shows consistent progression with...

## 2. VOLUME ANALYSIS
Total distance: 312.4 km
Weekly average: 39.1 km/week
Training load: Moderate to High

## 3. HEART RATE ZONES
Average HR: 145 bpm
Max HR recorded: 182 bpm
Zone 2 dominance: 65% of training

## 4. BODY COMPOSITION EVOLUTION
Initial weight: 75.5 kg
Final weight: 74.2 kg
Body fat: 18.5% → 17.8%
Muscle mass: Maintained

## 5. RECOMMENDATIONS
✅ Volume: Maintain current load
⚠️ Variety: Add strength training
🎯 Recovery: Increase rest days
```

## 🐛 Troubleshooting

### Common Issues

**Body composition not showing:**
- Check if you have a connected scale in Garmin Connect
- Verify measurements exist in the analysis period
- Increase `ANALYSIS_DAYS` if measurements are sparse

**Authentication errors:**
- Verify Garmin credentials in `.env`
- Check for special characters in password
- Try logging in on Garmin Connect web

**LLM errors:**
- Verify API key is valid
- Check token limits
- Ensure provider is correctly set

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python training_analyzer.py
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Python library for Garmin Connect
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [Anthropic](https://www.anthropic.com/) - Claude API
- [OpenAI](https://openai.com/) - GPT API
- [Google](https://ai.google.dev/) - Gemini API

## 📧 Contact

Your Name - [dvazquezd](mailto:dvazquezd@gmail.com)

Project Link: [https://github.com/your-username/garmin-training-analyzer](https://github.com/your-username/garmin-training-analyzer)

---

⭐️ If you find this project useful, consider giving it a star!
