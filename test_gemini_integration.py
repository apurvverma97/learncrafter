#!/usr/bin/env python3
"""
Simple test to verify Gemini integration works.
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_import():
    """Test if Gemini can be imported and configured."""
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        
        # Test configuration (without real API key)
        try:
            genai.configure(api_key="test_key")
            print("✅ Gemini configuration works")
        except Exception as e:
            print(f"⚠️  Configuration test: {e}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import Google Generative AI: {e}")
        return False

def test_app_structure():
    """Test if the app structure is intact."""
    try:
        from app.core.config import settings
        print("✅ App configuration loaded")
        
        from app.services.llm_service import LLMService
        print("✅ LLM Service imported")
        
        from app.services.prompt_service import PromptService
        print("✅ Prompt Service imported")
        
        from app.services.validation_service import ValidationService
        print("✅ Validation Service imported")
        
        return True
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_prompt_generation():
    """Test prompt generation without requiring LLM."""
    try:
        from app.services.prompt_service import PromptService
        from app.models.schemas import ConceptGenerationRequest
        
        prompt_service = PromptService()
        
        # Create a test concept request
        test_concept = ConceptGenerationRequest(
            title="Test Concept",
            description="A test concept for verification",
            module_context="Test Module",
            learning_objectives=["Learn something", "Understand basics"],
            prerequisites=["Basic knowledge"]
        )
        
        # Generate prompt
        prompt = prompt_service.generate_concept_prompt(test_concept)
        
        if prompt and len(prompt) > 100:
            print("✅ Prompt generation works")
            print(f"   Generated prompt length: {len(prompt)} characters")
            return True
        else:
            print("❌ Prompt generation failed - prompt too short")
            return False
            
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Gemini Integration")
    print("=" * 40)
    
    tests = [
        ("Gemini Import", test_gemini_import),
        ("App Structure", test_app_structure),
        ("Prompt Generation", test_prompt_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! Ready to run the application.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 