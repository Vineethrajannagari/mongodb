from pymongo import MongoClient
from urllib.parse import quote_plus
import socket

# Test DNS resolution first
try:
    host = "cluster0.s78cfde.mongodb.net"
    ip = socket.gethostbyname(host)
    print(f"DNS resolution successful: {host} -> {ip}")
except socket.gaierror as e:
    print(f"DNS resolution failed for {host}: {e}")
    print("\nDNS ISSUE DETECTED!")
    print("Please try these solutions:")
    print("1. Change your DNS servers to Google's public DNS (8.8.8.8 and 8.8.4.4)")
    print("2. Restart your computer after changing DNS settings")
    print("3. If on corporate network, try a different network (like mobile hotspot)")
    print("4. Check if your firewall is blocking MongoDB Atlas domains")
    exit(1)

# Your MongoDB credentials (update with actual password)
username = "vineethrajannagari_db_user"
password = "<Vineeth@123>"  # Replace with your actual password

# URL-encode them
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Use the encoded values in your connection string
db_url = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.s78cfde.mongodb.net/?appName=cluster0"

print(f"Attempting to connect to MongoDB Atlas...")
print(f"Connection string: mongodb+srv://{encoded_username}:***@cluster0.s78cfde.mongodb.net/?appName=cluster0")

# Create MongoClient with SSL configuration
mongo_client = MongoClient(
    db_url,
    ssl=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=30000
)

print("MongoClient created successfully")

# Test the connection
try:
    # Force a connection attempt
    mongo_client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Connection test failed: {e}")
    print("Please check your MongoDB Atlas credentials and network access settings.")

# Your existing database code
student_database = mongo_client['movies']
python_department = student_database['TFI']
some_cursor = python_department.find()

for item in some_cursor:
    print(item)

student_database = mongo_client['movies']

python_department = student_database['TFI']

some_cursor = python_department.find()


# print(list(some_cursor))

for item in some_cursor:
  print(item)