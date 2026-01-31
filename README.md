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

## 🏗️ Architecture & Design Principles

This project follows professional software engineering practices with a focus on maintainability, testability, and clean code.

### Template-Based Architecture

The HTML report generation uses a **template-based architecture** that separates presentation from logic:

- **HTML templates** ([src/templates/report_template.html](src/templates/report_template.html)) define the report structure using Jinja2 syntax
- **CSS stylesheets** ([src/templates/report_styles.css](src/templates/report_styles.css)) handle all styling separately
- **Python code** ([src/html_reporter.py](src/html_reporter.py)) focuses solely on data processing and template rendering

This separation provides several benefits:
- **Easier maintenance**: Update styling without touching Python code
- **Better testability**: Template logic can be tested independently
- **Improved readability**: No 590+ line methods with embedded HTML strings
- **SOLID compliance**: Single Responsibility Principle - each file has one clear purpose

### SOLID Principles

The codebase adheres to SOLID principles:

- **Single Responsibility**: Each class/module has one well-defined purpose (e.g., `GarminClient` handles API, `HTMLReporter` handles reporting)
- **Open/Closed**: New features added through extension, not modification (e.g., new LLM providers via abstraction)
- **Liskov Substitution**: LLM providers are interchangeable through common interfaces
- **Interface Segregation**: Clients depend only on interfaces they use
- **Dependency Inversion**: High-level modules depend on abstractions, not concrete implementations

### Clean Code & DRY Practices

Code quality standards enforced throughout:

- **Functions < 50 lines**: Small, focused functions that do one thing well
- **Descriptive naming**: Clear variable and function names that explain intent
- **DRY (Don't Repeat Yourself)**: Shared logic extracted into reusable functions
- **Type hints**: Full type annotations for better IDE support and error catching
- **Google-style docstrings**: Comprehensive documentation for all public APIs

### Separation of Concerns

The architecture maintains clear boundaries:

- **Logic layer** (`src/*.py`): Business logic, data processing, API integration
- **Presentation layer** (`src/templates/`): HTML structure and styling
- **Data layer** (`.cache/`, `analysis_reports/`): Persistence and output
- **Configuration layer** (`.env`, `prompts/`): External configuration

For detailed engineering standards and workflow guidelines, see [openspec/agents.md](openspec/agents.md).

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Architecture & Design Principles](#️-architecture--design-principles)
- [Code Quality Standards](#-code-quality-standards)
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
│   ├── cache_manager.py           # SQLite-based cache system
│   ├── visualizations.py          # Matplotlib chart generator
│   ├── html_reporter.py           # HTML report generator
│   └── templates/                 # Jinja2 templates for HTML reports
│       ├── report_template.html   # HTML report structure
│       └── report_styles.css      # Report styling
│
├── prompts/                       # External prompts
│   ├── system_prompt.txt          # System instructions
│   └── user_prompt_template.txt  # User data template
│
├── tests/                         # Test suite
│   ├── conftest.py                # Pytest fixtures
│   ├── test_config.py             # Config tests
│   ├── test_garmin_client.py      # Client tests
│   └── test_prompt_manager.py     # Prompt tests
│
├── openspec/                      # Spec-driven development
│   ├── specs/                     # Main capability specifications
│   ├── changes/                   # Active changes and proposals
│   └── agents.md                  # Engineering standards and principles
│
├── analysis_reports/              # Generated reports
│   ├── analisis_YYYYMMDD.txt      # Text format
│   ├── analisis_YYYYMMDD.md       # Markdown format
│   ├── datos_YYYYMMDD.json        # JSON format
│   ├── reporte_YYYYMMDD.html      # HTML format
│   ├── body_composition_*.png     # Weight & body fat charts
│   ├── activity_distribution_*.png # Activity pie chart
│   ├── weekly_volume_*.png        # Weekly volume bars
│   └── heart_rate_zones_*.png     # HR histogram
│
├── .cache/                        # Cache directory
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

## ✨ Code Quality Standards

This project maintains high code quality standards to ensure maintainability and reliability.

### Quality Metrics

- **Pylint Score**: 10.00/10 for refactored modules (e.g., [src/html_reporter.py](src/html_reporter.py))
- **Code Coverage**: Comprehensive test coverage with pytest
- **Type Safety**: Full type hints throughout the codebase

### Testing Approach

The project uses **pytest** with a robust testing strategy:

- **Fixtures** (`tests/conftest.py`): Reusable test data and mock objects
- **Mocking**: External dependencies (Garmin API, LLM providers) are mocked for reliable tests
- **Unit Tests**: Each module has dedicated test coverage
- **Integration Tests**: End-to-end workflows validated

Run tests with:
```bash
pytest tests/
```

### Code Style Standards

All code follows strict style guidelines:

- **Google-style docstrings**: All public functions, classes, and modules documented
- **Type hints**: Full type annotations using Python 3.11+ syntax
- **PEP 8 compliance**: Enforced via pylint
- **Naming conventions**: Descriptive names that explain intent
- **Function size**: Functions kept under 50 lines per Clean Code principles

### Engineering Principles

The codebase adheres to principles defined in [openspec/agents.md](openspec/agents.md):

- **SOLID principles** for object-oriented design
- **Clean Code** practices (small functions, meaningful names, DRY)
- **KISS** (Keep It Simple, Stupid) - avoid over-engineering
- **YAGNI** (You Aren't Gonna Need It) - implement only what's needed

### Quality Expectations for Contributors

When contributing to this project:

1. **Maintain pylint score**: New code should achieve 10/10 or explain exceptions
2. **Add tests**: All new features require test coverage
3. **Document with docstrings**: Use Google-style format
4. **Follow existing patterns**: Match the architectural style
5. **Keep functions small**: Refactor if functions exceed 50 lines

### Recent Quality Improvements

**Template Refactoring (2026-01)**: Refactored HTML report generation
- **Before**: 776-line file with 590+ line method containing embedded HTML/CSS
- **After**: 208-line file using external Jinja2 templates
- **Impact**: 69% code reduction, improved maintainability, achieved 10/10 pylint
- **See**: [src/templates/](src/templates/) for separated presentation layer

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

### OpenSpec Workflow

This project uses **OpenSpec** - a spec-driven development workflow that improves code quality through structured planning and clear requirements.

#### What is OpenSpec?

OpenSpec is a systematic approach to software changes that ensures:
- Clear understanding of requirements before coding
- Documented design decisions
- Testable specifications
- Traceable implementation tasks

#### The Workflow

Changes follow a structured artifact sequence:

1. **Proposal** - Define why the change is needed and what will change
2. **Design** - Document technical decisions and architecture
3. **Specs** - Write testable requirements with scenarios
4. **Tasks** - Break down implementation into checkboxed items
5. **Implementation** - Work through tasks with full context
6. **Archive** - Preserve the change history

#### Creating a Change

Start a new spec-driven change:

```bash
# Using OpenSpec CLI (if available)
openspec new change "add-feature-name"

# Or create directory structure manually
mkdir -p openspec/changes/add-feature-name
```

Then create artifacts in sequence: `proposal.md` → `design.md` → `specs/` → `tasks.md`

#### When to Use OpenSpec

**Use the full workflow for:**
- New features or significant enhancements
- Architectural changes
- Changes affecting multiple modules
- Any work where design decisions need documentation

**Simple fixes can skip the workflow:**
- Typo corrections
- Small bug fixes in isolated code
- Documentation-only updates

#### Benefits

OpenSpec provides helpful structure that:
- Prevents over-engineering through clear scope
- Surfaces design issues early (before coding)
- Creates searchable documentation of decisions
- Makes onboarding easier with traceable history
- Improves code review with clear context

For complete workflow details and engineering standards, see [openspec/agents.md](openspec/agents.md).

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

Project Link: [https://github.com/dvazquezd/garmin-training-analyzer](https://github.com/dvazquezd/garmin-training-analyzer)

---

⭐️ If you find this project useful, consider giving it a star!
