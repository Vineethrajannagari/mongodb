"""
Helper script to configure .env file with MongoDB Atlas connection string
"""

import os


def configure_env():
    """Interactive helper to set up .env file"""
    print("=" * 60)
    print("MongoDB Atlas Connection Setup")
    print("=" * 60)
    print()
    print("Follow these steps in MongoDB Atlas:")
    print("1. Go to Database -> Connect -> Connect your application")
    print("2. Select Python driver")
    print("3. Copy the connection string")
    print()
    
    print("Your connection string will look like:")
    print("mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority")
    print()
    
    print("Paste your connection string below (replace <username> and <password> with actual values):")
    
    connection_string = input("Connection string: ").strip()
    
    if not connection_string:
        print("No connection string provided. Exiting.")
        return
    
    # Basic validation
    if not connection_string.startswith("mongodb"):
        print("Warning: Connection string doesn't start with 'mongodb'")
        proceed = input("Continue anyway? (y/n): ").lower()
        if proceed != 'y':
            return
    
    # Write to .env file
    env_content = f"MONGO_URI={connection_string}\n"
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        print()
        print("=" * 60)
        print("SUCCESS! .env file created")
        print("=" * 60)
        print(f"Connection string saved to: {os.path.abspath('.env')}")
        print()
        print("You can now run:")
        print("  python demo.py")
        print()
        print("IMPORTANT: Never commit .env file to version control!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating .env file: {e}")


if __name__ == "__main__":
    configure_env()
