# MongoDB Setup Guide for Windows

MongoDB is not currently installed or running on your system. Follow these steps to set it up:

## Option 1: Install MongoDB Community Server (Recommended)

1. **Download MongoDB**:
   - Go to https://www.mongodb.com/try/download/community
   - Select Windows version
   - Choose the MSI installer
   - Download and run the installer

2. **During Installation**:
   - Choose "Complete" installation
   - Install MongoDB as a Service (recommended)
   - Install MongoDB Compass (optional GUI tool)
   - Complete the installation

3. **Start MongoDB Service**:
   ```powershell
   # Open PowerShell as Administrator
   net start MongoDB
   ```

4. **Verify Installation**:
   ```powershell
   mongod --version
   ```

## Option 2: Use MongoDB Atlas (Cloud - Free)

If you prefer not to install MongoDB locally:

1. **Create a free MongoDB Atlas account**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free
   - Create a free cluster (M0 free tier)

2. **Get Connection String**:
   - In Atlas, go to Database → Connect
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

3. **Update .env file**:
   ```
   MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
   ```

## Option 3: Use Docker (If you have Docker installed)

```powershell
# Pull MongoDB image
docker pull mongo

# Run MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo

# Verify it's running
docker ps
```

## After MongoDB is Running

Once MongoDB is installed and running, you can test the system:

```powershell
# Run the demo
python demo.py

# Or run the main module
python attendance_manager.py
```

## Quick Test Connection

You can test if MongoDB is accessible with this simple Python script:

```python
from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/')
    client.admin.command('ping')
    print("MongoDB is running and accessible!")
except Exception as e:
    print(f"Cannot connect to MongoDB: {e}")
```

## Troubleshooting

**If MongoDB service won't start**:
- Check Windows Services: `services.msc`
- Look for "MongoDB" service
- Ensure it's set to "Automatic" startup type

**If connection fails**:
- Check firewall settings
- Verify MongoDB is listening on port 27017
- Check connection string in .env file

**If you get authentication errors**:
- For local MongoDB: No auth usually needed
- For Atlas: Ensure username/password are correct in connection string
