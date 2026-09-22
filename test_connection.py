"""
Test script to check MongoDB connection and system setup
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os


def test_mongodb_connection():
    """Test if MongoDB is running and accessible."""
    print("Testing MongoDB Connection...")
    print("-" * 40)
    
    # Try local MongoDB first
    connection_strings = [
        "mongodb://localhost:27017/",
        "mongodb://127.0.0.1:27017/",
    ]
    
    # Add environment variable if set
    env_uri = os.getenv("MONGO_URI")
    if env_uri:
        connection_strings.insert(0, env_uri)
    
    for uri in connection_strings:
        try:
            print(f"Trying to connect to: {uri}")
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("[OK] MongoDB connection successful!")
            print(f"  Connected to: {uri}")
            
            # Get server info
            server_info = client.server_info()
            print(f"  MongoDB version: {server_info.get('version', 'unknown')}")
            
            # List databases
            databases = client.list_database_names()
            print(f"  Available databases: {', '.join(databases[:5])}...")
            
            client.close()
            return uri
            
        except ConnectionFailure as e:
            print(f"[FAIL] Connection failed: {e}")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
    
    return None


def test_dependencies():
    """Test if required dependencies are installed."""
    print("\nTesting Dependencies...")
    print("-" * 40)
    
    dependencies = [
        ("pymongo", "PyMongo"),
        ("dotenv", "python-dotenv")
    ]
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"[OK] {name} is installed")
        except ImportError:
            print(f"[FAIL] {name} is NOT installed")
            print(f"  Install with: pip install {name.lower()}")


def main():
    """Main test function."""
    print("=" * 40)
    print("MongoDB System Test")
    print("=" * 40)
    
    # Test dependencies
    test_dependencies()
    
    # Test MongoDB connection
    connection_uri = test_mongodb_connection()
    
    if connection_uri:
        print("\n" + "=" * 40)
        print("SUCCESS: System is ready to use!")
        print("=" * 40)
        print("\nYou can now run:")
        print("  python demo.py")
        print("  python attendance_manager.py")
        print(f"\nUsing connection string: {connection_uri}")
    else:
        print("\n" + "=" * 40)
        print("MongoDB is not accessible")
        print("=" * 40)
        print("\nPlease follow these steps:")
        print("1. Install MongoDB Community Server")
        print("   Download from: https://www.mongodb.com/try/download/community")
        print("2. Start MongoDB service:")
        print("   net start MongoDB")
        print("3. Or use MongoDB Atlas (cloud):")
        print("   https://www.mongodb.com/cloud/atlas")
        print("\nSee setup_guide.md for detailed instructions")


if __name__ == "__main__":
    main()
