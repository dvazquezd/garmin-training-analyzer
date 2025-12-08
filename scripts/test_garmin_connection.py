"""
Test Garmin Connect connection and basic functionality.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.garmin_client import GarminClient
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """Test Garmin connection."""

    load_dotenv()

    print("=" * 70)
    print("GARMIN CONNECT TEST")
    print("=" * 70)

    # Check credentials
    print("\n1. Checking credentials...")
    if not Config.GARMIN_EMAIL or not Config.GARMIN_PASSWORD:
        print("   ❌ Credentials not set")
        print("   Please configure GARMIN_EMAIL and GARMIN_PASSWORD in .env")
        return
    print(f"   ✅ Email: {Config.GARMIN_EMAIL}")

    # Connect
    print("\n2. Connecting to Garmin...")
    client = GarminClient(Config.GARMIN_EMAIL, Config.GARMIN_PASSWORD)
    if not client.connect():
        print("   ❌ Connection failed")
        print("   Check your credentials and internet connection")
        return
    print("   ✅ Connected successfully")

    # Get profile
    print("\n3. Fetching user profile...")
    profile = client.get_user_profile()
    if profile:
        print(f"   ✅ Name: {profile.get('name', 'Unknown')}")
        print(f"   ✅ Unit system: {profile.get('unit_system', 'Unknown')}")
    else:
        print("   ⚠️  Could not fetch profile")

    # Get recent activities
    print("\n4. Fetching recent activities (last 7 days)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    activities = client.get_activities(start_date, end_date)
    if activities:
        print(f"   ✅ Found {len(activities)} activities")
        if len(activities) > 0:
            latest = activities[0]
            print(f"\n   Latest activity:")
            print(f"      Name: {latest.get('activityName', 'Unknown')}")
            print(f"      Type: {latest.get('activityType', {}).get('typeKey', 'Unknown')}")
            print(f"      Date: {latest.get('startTimeLocal', 'Unknown')}")
            if 'distance' in latest:
                print(f"      Distance: {latest['distance']/1000:.2f} km")
            if 'duration' in latest:
                print(f"      Duration: {latest['duration']/60:.0f} min")
    else:
        print("   ⚠️  No activities found in last 7 days")

    # Get body composition
    print("\n5. Checking body composition data...")
    body_comp = client.get_body_composition(start_date, end_date)
    if body_comp and len(body_comp) > 0:
        print(f"   ✅ Found {len(body_comp)} measurements")
        latest = body_comp[0]
        if 'weight' in latest:
            weight = latest['weight']
            weight_kg = weight / 1000 if weight > 500 else weight
            print(f"      Latest weight: {weight_kg:.1f} kg")
        if 'bodyFat' in latest:
            print(f"      Body fat: {latest['bodyFat']:.1f}%")
    else:
        print("   ⚠️  No body composition data found")
        print("   This is normal if you don't have a connected scale")

    # Get devices
    print("\n6. Fetching connected devices...")
    devices = client.get_devices()
    if devices:
        print(f"   ✅ Found {len(devices)} device(s)")
        for device in devices[:3]:  # Show max 3
            print(f"      - {device.get('productDisplayName', 'Unknown device')}")
    else:
        print("   ⚠️  No devices found")

    print("\n" + "=" * 70)
    print("✅ GARMIN CONNECTION TEST COMPLETED")
    print("=" * 70)
    print("\nYour Garmin Connect integration is working!")
    print("You can now run: python training_analyzer.py\n")


if __name__ == "__main__":
    main()
