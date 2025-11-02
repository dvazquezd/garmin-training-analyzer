"""
Diagnostic script for body composition data from Garmin Connect.
Tests connection and displays body composition structure.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.garmin_client import GarminClient
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run body composition diagnostic."""
    
    load_dotenv()
    
    print("=" * 70)
    print("BODY COMPOSITION DIAGNOSTIC")
    print("=" * 70)
    
    # 1. Verify credentials
    print("\n1. Verifying credentials...")
    if not Config.GARMIN_EMAIL or not Config.GARMIN_PASSWORD:
        print("   ❌ Credentials not configured")
        print("   Please set GARMIN_EMAIL and GARMIN_PASSWORD in .env")
        return
    print(f"   ✅ Email: {Config.GARMIN_EMAIL}")
    
    # 2. Connect
    print("\n2. Connecting to Garmin...")
    client = GarminClient(Config.GARMIN_EMAIL, Config.GARMIN_PASSWORD)
    if not client.connect():
        print("   ❌ Connection failed")
        return
    print("   ✅ Connected")
    
    # 3. Get body composition
    print("\n3. Fetching body composition data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=Config.ANALYSIS_DAYS)
    
    print(f"   Date range: {start_date.date()} to {end_date.date()}")
    print(f"   Days: {Config.ANALYSIS_DAYS}")
    
    body_comp = client.get_body_composition(start_date, end_date)
    
    print(f"\n4. Results:")
    print(f"   Type: {type(body_comp)}")
    print(f"   Count: {len(body_comp) if body_comp else 0}")
    
    if body_comp and len(body_comp) > 0:
        print("\n   ✅ DATA FOUND")
        print(f"\n   First measurement:")
        print(json.dumps(body_comp[0], indent=4, ensure_ascii=False))
        
        # Verify key fields
        first = body_comp[0]
        print(f"\n   Available fields:")
        for key in sorted(first.keys()):
            value = first[key]
            print(f"      - {key}: {value}")
            
        # Show summary
        print(f"\n   📊 Summary:")
        print(f"      Total measurements: {len(body_comp)}")
        if 'weight' in first:
            weight = first['weight']
            weight_kg = weight / 1000 if weight > 500 else weight
            print(f"      Latest weight: {weight_kg:.1f} kg")
        if 'bodyFat' in first:
            print(f"      Latest body fat: {first['bodyFat']:.1f}%")
        if 'bmi' in first:
            print(f"      Latest BMI: {first['bmi']:.1f}")
            
    else:
        print("\n   ❌ NO DATA FOUND")
        print("\n   Possible causes:")
        print("   1. No connected scale in Garmin Connect")
        print("   2. No measurements in this period")
        print("   3. Date range is too short")
        
        # Try with 90 days
        print("\n5. Trying with 90 days...")
        start_date_90 = end_date - timedelta(days=90)
        body_comp_90 = client.get_body_composition(start_date_90, end_date)
        
        if body_comp_90 and len(body_comp_90) > 0:
            print(f"   ✅ Found {len(body_comp_90)} measurements with 90 days")
            print(f"   Suggestion: Set ANALYSIS_DAYS=90 in your .env file")
        else:
            print("   ❌ Still no data with 90 days")
            print("\n   Next steps:")
            print("   - Verify you have a scale connected in Garmin Connect")
            print("   - Check that weight measurements appear in the app/web")
            print("   - Try syncing your scale")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
