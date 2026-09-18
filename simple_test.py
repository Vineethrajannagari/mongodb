"""
Simple test to check system status without hanging
"""

import sys


def test_dependencies():
    """Test if required dependencies are installed."""
    print("Testing Dependencies...")
    print("-" * 40)
    
    try:
        import pymongo
        print("[OK] PyMongo is installed")
        print(f"     Version: {pymongo.version}")
    except ImportError:
        print("[FAIL] PyMongo is NOT installed")
        print("       Install with: pip install pymongo")
        return False
    
    try:
        from dotenv import load_dotenv
        print("[OK] python-dotenv is installed")
    except ImportError:
        print("[FAIL] python-dotenv is NOT installed")
        print("       Install with: pip install python-dotenv")
        return False
    
    return True


def main():
    """Main test function."""
    print("=" * 40)
    print("System Status Check")
    print("=" * 40)
    print()
    
    deps_ok = test_dependencies()
    
    print()
    print("=" * 40)
    if deps_ok:
        print("Dependencies: OK")
        print("MongoDB: Not tested (connection may hang)")
        print()
        print("To run the system:")
        print("1. Ensure MongoDB is installed and running")
        print("2. Configure MONGO_URI in .env file")
        print("3. Run: python demo.py")
    else:
        print("Dependencies: FAILED")
        print("Please install missing dependencies first")
    print("=" * 40)


if __name__ == "__main__":
    main()
