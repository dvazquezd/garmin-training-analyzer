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
- 📊 **Data Visualizations**: Beautiful charts with matplotlib (weight evolution, activity distribution, HR zones, weekly volume)
- 📝 **Professional Reports**: Export in TXT, Markdown, JSON, and **interactive HTML** formats
- 🎨 **HTML Reports**: Responsive design with embedded charts, statistics cards, and modern styling
- 💾 **Smart Caching**: SQLite-based cache to reduce API calls and improve performance
- 🔄 **Rate Limiting**: Automatic retry with exponential backoff for API resilience
- ⚙️ **Highly Configurable**: Adjust analysis period, LLM models, parameters, and cache settings
- 🖥️ **CLI Arguments**: Full command-line interface support for all configuration options
- 🎨 **Custom Prompts**: External prompt management for easy customization
- 🧪 **Testing Suite**: Comprehensive tests with pytest

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

# Cache Settings (NEW!)
USE_CACHE=true            # Enable local cache (default: true)
CACHE_TTL_HOURS=24        # Cache expiration in hours
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
│   ├── garmin_client.py           # Garmin Connect client with cache & retry
│   ├── llm_analizer.py            # LLM analyzer
│   ├── prompt_manager.py          # Prompt management
│   ├── cache_manager.py           # SQLite-based cache system (NEW!)
│   ├── visualizations.py          # Matplotlib chart generator (NEW!)
│   └── html_reporter.py           # HTML report generator (NEW!)
│
├── prompts/                       # External prompts
│   ├── system_prompt.txt          # System instructions
│   └── user_prompt_template.txt  # User data template
│
├── tests/                         # Test suite (NEW!)
│   ├── conftest.py                # Pytest fixtures
│   ├── test_config.py             # Config tests
│   ├── test_garmin_client.py      # Client tests
│   └── test_prompt_manager.py     # Prompt tests
│
├── analysis_reports/              # Generated reports
│   ├── analisis_YYYYMMDD.txt      # Text format
│   ├── analisis_YYYYMMDD.md       # Markdown format
│   ├── datos_YYYYMMDD.json        # JSON format
│   ├── reporte_YYYYMMDD.html      # HTML format (NEW!)
│   ├── body_composition_*.png     # Weight & body fat charts (NEW!)
│   ├── activity_distribution_*.png # Activity pie chart (NEW!)
│   ├── weekly_volume_*.png        # Weekly volume bars (NEW!)
│   └── heart_rate_zones_*.png     # HR histogram (NEW!)
│
├── .cache/                        # Cache directory (NEW!)
│   └── garmin_cache.db            # SQLite cache database
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

#### Using Environment Variables
```bash
# Analyze last 60 days
export ANALYSIS_DAYS=60
python training_analyzer.py

# Use different LLM
export LLM_PROVIDER=openai
python training_analyzer.py
```

#### Using CLI Arguments (NEW!)
```bash
# Analyze specific period
python training_analyzer.py --days 60

# Use different provider and model
python training_analyzer.py --provider openai --model gpt-4o

# Override credentials
python training_analyzer.py --email user@example.com --password mypass

# Cache management
python training_analyzer.py --no-cache           # Disable cache
python training_analyzer.py --cache-ttl 48       # Cache expires in 48h
python training_analyzer.py --clear-cache        # Clear cache first

# Debug mode
python training_analyzer.py --debug

# Combine options
python training_analyzer.py --days 90 --provider anthropic --cache-ttl 12
```

#### View All Options
```bash
python training_analyzer.py --help
```

### Output Files

The analyzer generates multiple report formats in `analysis_reports/`:

1. **HTML Report** (`reporte_YYYYMMDD_HHMMSS.html`) **⭐ NEW!**
   - Interactive, responsive design
   - Embedded charts and visualizations
   - Statistics cards with key metrics
   - Activity table with all details
   - Beautiful gradient styling
   - **Best for sharing and viewing**

2. **Text Report** (`analisis_YYYYMMDD_HHMMSS.txt`)
   - Plain text format
   - Easy to read
   - Includes metadata

3. **Markdown Report** (`analisis_YYYYMMDD_HHMMSS.md`)
   - Formatted with tables
   - Activity summaries
   - Proper sectioning

4. **JSON Data** (`datos_YYYYMMDD_HHMMSS.json`)
   - Raw data export
   - All activities
   - Body composition
   - Analysis text

5. **Visualizations** (PNG charts) **⭐ NEW!**
   - `body_composition_*.png` - Weight and body fat % evolution
   - `activity_distribution_*.png` - Pie chart of activity types
   - `weekly_volume_*.png` - Bar charts of weekly distance and activity count
   - `heart_rate_zones_*.png` - Histogram of heart rate distribution

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

# Check cache statistics (NEW!)
python -m src.cache_manager

# Test visualizations (NEW!)
python -m src.visualizations

# Test HTML reporter (NEW!)
python -m src.html_reporter
```

### Code Structure

- **GarminClient**: Handles all Garmin Connect API interactions with caching and retry logic
- **LLMAnalyzer**: Manages LLM integration and prompt processing
- **PromptManager**: External prompt file management
- **Config**: Centralized configuration management
- **CacheManager**: SQLite-based caching system with TTL expiration (NEW!)
- **TrainingVisualizer**: Matplotlib chart generation for training data (NEW!)
- **HTMLReporter**: HTML report generator with responsive design (NEW!)

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

### Cache Issues

**Cache not working:**
- Check if `.cache/` directory exists and is writable
- Verify `USE_CACHE=true` in `.env`
- Run `--clear-cache` to reset

**Stale data:**
- Reduce `CACHE_TTL_HOURS` for more frequent updates
- Use `--no-cache` flag for one-time fresh data
- Run `--clear-cache` to force refresh

**View cache statistics:**
```bash
python -m src.cache_manager
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python training_analyzer.py

# Or use CLI flag
python training_analyzer.py --debug
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
- [matplotlib](https://matplotlib.org/) - Plotting library for visualizations
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine for HTML reports
- [pytest](https://pytest.org/) - Testing framework

## 📧 Contact

Your Name - [dvazquezd](mailto:dvazquezd@gmail.com)

Project Link: [https://github.com/your-username/garmin-training-analyzer](https://github.com/your-username/garmin-training-analyzer)

---

⭐️ If you find this project useful, consider giving it a star!
