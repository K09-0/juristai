#!/usr/bin/env python3
import os
import sys

print("="*50)
print("JuristAI Configuration Test")
print("="*50)

print(f"\nPython version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("\nEnvironment variables loaded from .env")
except:
    print("\nWarning: python-dotenv not available, reading from system env")

print("\nConfiguration:")
print(f"  SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')[:50]}")
print(f"  SUPABASE_KEY: {'SET' if os.getenv('SUPABASE_KEY') else 'NOT SET'}")
print(f"  ENV: {os.getenv('ENV', 'NOT SET')}")
print(f"  PORT: {os.getenv('PORT', '8000')}")
print(f"  CORS_ORIGINS: {os.getenv('CORS_ORIGINS', 'NOT SET')}")

print("\n" + "="*50)
print("Configuration test completed!")
print("="*50)
