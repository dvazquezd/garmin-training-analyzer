"""
Configuration verification script.
Checks all settings and dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.prompt_manager import PromptManager


def check_environment():
    """Check environment variables."""
    print("=" * 70)
    print("ENVIRONMENT VARIABLES")
    print("=" * 70)

    # Garmin
    print("\n📱 Garmin Connect:")
    print(f"   Email: {'✅ Set' if Config.GARMIN_EMAIL else '❌ Missing'}")
    print(f"   Password: {'✅ Set' if Config.GARMIN_PASSWORD else '❌ Missing'}")

    # LLM
    print(f"\n🤖 LLM Configuration:")
    print(f"   Provider: {Config.LLM_PROVIDER}")
    llm_config = Config.get_llm_config()
    print(f"   Model: {llm_config.get('model', 'Unknown')}")
    print(f"   API Key: {'✅ Set' if llm_config.get('api_key') else '❌ Missing'}")

    # Parameters
    print(f"\n⚙️  Analysis Parameters:")
    print(f"   Days: {Config.ANALYSIS_DAYS}")
    print(f"   Max tokens: {Config.MAX_TOKENS}")
    print(f"   Temperature: {Config.TEMPERATURE}")

    # Paths
    print(f"\n📁 Paths:")
    print(f"   Output dir: {Config.OUTPUT_DIR}")
    print(f"   Output exists: {'✅' if Config.OUTPUT_DIR.exists() else '❌'}")
    print(f"   Training plan: {Config.TRAINING_PLAN_PATH}")

    # Validation
    is_valid, errors = Config.validate()
    print(f"\n{'✅ Configuration valid' if is_valid else '❌ Configuration has errors'}")
    if errors:
        for error in errors:
            print(f"   - {error}")


def check_prompts():
    """Check prompt configuration."""
    print("\n" + "=" * 70)
    print("PROMPTS CONFIGURATION")
    print("=" * 70)

    is_valid, errors = PromptManager.validate_prompts()

    if is_valid:
        print("\n✅ Prompts valid")
        info = PromptManager.get_prompts_info()

        print("\n📄 System Prompt:")
        print(f"   File: {info['system_prompt']['file']}")
        print(f"   Length: {info['system_prompt']['length']} chars")
        print(f"   Lines: {info['system_prompt']['lines']}")

        print("\n📝 User Prompt Template:")
        print(f"   File: {info['user_template']['file']}")
        print(f"   Length: {info['user_template']['length']} chars")
        print(f"   Lines: {info['user_template']['lines']}")
        print(f"   Placeholders: {info['user_template']['placeholders']}")
    else:
        print("\n❌ Prompt errors:")
        for error in errors:
            print(f"   - {error}")


def check_dependencies():
    """Check Python dependencies."""
    print("\n" + "=" * 70)
    print("DEPENDENCIES")
    print("=" * 70)

    required = [
        ('garminconnect', '0.2.30'),
        ('anthropic', '0.71.0'),
        ('langchain', '1.0.1'),
        ('python-dotenv', '1.1.1'),
    ]

    print("\n📦 Checking packages...")
    for package, expected_version in required:
        try:
            if package == 'python-dotenv':
                import dotenv
                version = dotenv.__version__ if hasattr(dotenv, '__version__') else 'unknown'
            else:
                mod = __import__(package.replace('-', '_'))
                version = mod.__version__ if hasattr(mod, '__version__') else 'unknown'

            status = '✅' if version == expected_version else '⚠️'
            print(f"   {status} {package}: {version} (expected: {expected_version})")
        except ImportError:
            print(f"   ❌ {package}: Not installed")


def check_directories():
    """Check directory structure."""
    print("\n" + "=" * 70)
    print("DIRECTORY STRUCTURE")
    print("=" * 70)

    base_dir = Path(__file__).parent.parent

    required_dirs = [
        ('src', 'Source code'),
        ('prompts', 'Prompt files'),
        ('analysis_reports', 'Output reports'),
    ]

    print("\n📁 Checking directories...")
    for dir_name, description in required_dirs:
        dir_path = base_dir / dir_name
        exists = dir_path.exists()
        print(f"   {'✅' if exists else '❌'} {dir_name}/ - {description}")
        if exists and dir_path.is_dir():
            files = list(dir_path.iterdir())
            print(f"      Files: {len(files)}")


def main():
    """Run all checks."""
    print("\n🔍 CONFIGURATION VERIFICATION\n")

    check_environment()
    check_prompts()
    check_dependencies()
    check_directories()

    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETED")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   1. Fix any ❌ errors shown above")
    print("   2. Run: python training_analyzer.py")
    print("   3. Check output in analysis_reports/\n")


if __name__ == "__main__":
    main()
