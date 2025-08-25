"""
Basic tests for the AI Personal Email Assistant.
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.config.settings import Settings
        from src.utils.logger import get_logger
        from src.utils.email_parser import clean_email_body
        
        print("✅ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_email_parsing():
    """Test email parsing utilities."""
    from src.utils.email_parser import clean_email_body, extract_email_addresses
    
    # Test email cleaning
    dirty_email = """
    Hi there,
    
    This is a test email with lots of extra     spaces
    and
    
    
    multiple newlines.
    
    Best regards,
    John
    --
    Sent from my iPhone
    """
    
    clean_text = clean_email_body(dirty_email)
    print(f"✅ Email cleaning: '{dirty_email[:50]}...' -> '{clean_text[:50]}...'")
    
    # Test email extraction
    text_with_emails = "Contact me at john@example.com or support@company.org"
    emails = extract_email_addresses(text_with_emails)
    print(f"✅ Email extraction: Found {emails}")
    
    return True

def test_settings():
    """Test settings configuration."""
    from src.config.settings import Settings
    
    # Test with default values
    settings = Settings()
    print(f"✅ Settings loaded: Database URL = {settings.database_url}")
    print(f"   Auto reply enabled: {settings.auto_reply_enabled}")
    print(f"   Max emails fetch: {settings.max_emails_fetch}")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Running AI Personal Email Assistant Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Email Parsing Test", test_email_parsing), 
        ("Settings Test", test_settings),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())