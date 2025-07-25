#!/usr/bin/env python3
"""
LearnCrafter MVP Setup Script
Helps configure the environment and test the application.
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'google.generativeai', 'supabase', 
        'beautifulsoup4', 'jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
    
    return len(missing_packages) == 0


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created")
        print("⚠️  Please update .env file with your actual API keys")
        return True
    else:
        print("❌ env.example file not found")
        return False


def check_env_variables():
    """Check if required environment variables are set."""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the required values")
        return False
    
    print("✅ All required environment variables are set")
    return True


def test_imports():
    """Test if the application can be imported."""
    try:
        from app.main import app
        print("✅ Application imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def run_health_check():
    """Run a quick health check of the application."""
    try:
        import uvicorn
        from app.main import app
        
        # Test the health endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 LearnCrafter MVP Setup (Gemini Edition)")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    print()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    check_dependencies()
    print()
    
    # Create .env file
    print("🔧 Setting up environment...")
    create_env_file()
    print()
    
    # Test imports
    print("🧪 Testing application...")
    if not test_imports():
        print("❌ Setup failed: Application cannot be imported")
        sys.exit(1)
    
    # Check environment variables
    print("🔑 Checking environment variables...")
    env_ok = check_env_variables()
    print()
    
    # Run health check
    print("🏥 Running health check...")
    health_ok = run_health_check()
    print()
    
    # Summary
    print("📋 Setup Summary")
    print("=" * 50)
    
    if env_ok and health_ok:
        print("✅ Setup completed successfully!")
        print("\n🎉 You can now run the application:")
        print("   uvicorn app.main:app --reload")
        print("\n📖 API documentation will be available at:")
        print("   http://localhost:8000/docs")
        print("\n🔑 Required API Keys:")
        print("   - Google Gemini API Key (https://makersuite.google.com/app/apikey)")
        print("   - Supabase URL and Key (https://supabase.com)")
    else:
        print("⚠️  Setup completed with warnings")
        if not env_ok:
            print("   - Please configure your environment variables")
        if not health_ok:
            print("   - Health check failed, check your configuration")
        
        print("\n🔧 Next steps:")
        print("   1. Get Google Gemini API Key from: https://makersuite.google.com/app/apikey")
        print("   2. Update .env file with your API keys")
        print("   3. Create Supabase project and run database schema")
        print("   4. Run: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main() 