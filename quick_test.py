"""
Quick test script - enter your password as command line argument
Usage: python quick_test.py YOUR_PASSWORD
"""

import sys
from attendance_manager import AttendanceManager


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py YOUR_MONGODB_PASSWORD")
        print("Example: python quick_test.py MyPassword123")
        return
    
    password = sys.argv[1]
    
    # Replace placeholder with actual password
    mongo_uri = f"mongodb+srv://vineethrajannagari_db_user:{password}@cluster0.s78cfde.mongodb.net/?appName=cluster0"
    
    print("Testing MongoDB Atlas connection...")
    print(f"Connection: mongodb+srv://vineethrajannagari_db_user:***@cluster0.s78cfde.mongodb.net/?appName=cluster0")
    
    try:
        manager = AttendanceManager(mongo_uri, "college_attendance")
        print("SUCCESS: Connected to MongoDB Atlas!")
        
        # Quick test
        print("\nAdding a test student...")
        result = manager.add_student("Test User", "TEST999", "test@example.com", "B.Tech")
        print(result)
        
        print("\nFinding the test student...")
        student = manager.find_student_by_roll("TEST999")
        print(f"Found: {student['name'] if student else 'Not found'}")
        
        print("\nCleaning up...")
        manager.delete_student("TEST999")
        
        manager.close_connection()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
