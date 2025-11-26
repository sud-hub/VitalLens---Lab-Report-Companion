"""
Quick setup script for Gemini API configuration.

This script helps you set up your .env file with the Gemini API key.
"""

import os
from pathlib import Path


def setup_gemini_api():
    """Interactive setup for Gemini API key."""
    
    print("=" * 60)
    print("Health Monitor - Gemini API Setup")
    print("=" * 60)
    print()
    
    # Check if .env exists
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if not env_path.exists():
        print("📋 No .env file found. Creating from .env.example...")
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found!")
            return
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Check if GEMINI_API_KEY is already set
    has_gemini_key = False
    gemini_key_value = ""
    
    for line in lines:
        if line.strip().startswith("GEMINI_API_KEY="):
            has_gemini_key = True
            gemini_key_value = line.split("=", 1)[1].strip()
            break
    
    if has_gemini_key and gemini_key_value and gemini_key_value != "your-gemini-api-key-here":
        print(f"✅ Gemini API key is already configured")
        print(f"   Current key: {gemini_key_value[:10]}...{gemini_key_value[-4:]}")
        print()
        response = input("Do you want to update it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print()
    print("📝 To get your Gemini API key:")
    print("   1. Visit: https://makersuite.google.com/app/apikey")
    print("   2. Click 'Create API Key'")
    print("   3. Copy the generated key")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Update .env file
    updated_lines = []
    key_updated = False
    
    for line in lines:
        if line.strip().startswith("GEMINI_API_KEY="):
            updated_lines.append(f"GEMINI_API_KEY={api_key}\n")
            key_updated = True
        else:
            updated_lines.append(line)
    
    # If key wasn't in file, add it
    if not key_updated:
        updated_lines.append(f"\n# Gemini API Configuration\n")
        updated_lines.append(f"GEMINI_API_KEY={api_key}\n")
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print()
    print("✅ Gemini API key configured successfully!")
    print()
    print("Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run the server: uvicorn app.main:app --reload")
    print("  3. Upload a medical report to test!")
    print()


if __name__ == "__main__":
    try:
        setup_gemini_api()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
