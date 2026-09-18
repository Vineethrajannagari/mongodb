# MongoDB Atlas Setup Guide

MongoDB Atlas is a cloud database service with a free tier - no installation required!

## Quick Setup Steps

### 1. Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" 
3. Sign up with email or Google/GitHub account
4. Verify your email address

### 2. Create a Free Cluster
1. After logging in, click "Build a Database"
2. Choose "M0 Sandbox" (FREE tier - 512MB storage)
3. Select a cloud provider (AWS, Google Cloud, or Azure)
4. Choose a region (pick one closest to you for better performance)
5. Name your cluster (default is fine)
6. Click "Create"

### 3. Create Database User
1. Wait for cluster to be created (takes 2-5 minutes)
2. Go to "Database Access" in left sidebar
3. Click "Add New Database User"
4. Username: Choose a username (e.g., "admin")
5. Password: Create a strong password (SAVE THIS - you'll need it!)
6. Privileges: "Read and write to any database"
7. Click "Create User"

### 4. Configure Network Access
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

### 5. Get Connection String
1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select driver: "Python" and version: "3.6 or later"
5. Copy the connection string

It will look like:
```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### 6. Configure Your .env File
1. Create a file named `.env` in your project folder
2. Replace `<username>` and `<password>` in the connection string with your actual credentials
3. Paste the connection string into your .env file:

```
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

Example:
```
MONGO_URI=mongodb+srv://admin:MySecurePassword123@cluster0.abc12.mongodb.net/?retryWrites=true&w=majority
```

### 7. Test the Connection
Run the demo:
```bash
python demo.py
```

## Important Notes

- **Security**: Your password will be visible in the .env file - never commit this to git
- **Free Tier Limits**: 512MB storage, shared RAM, suitable for development/testing
- **Connection**: First connection may take 10-30 seconds as the cluster spins up
- **Firewall**: If connection fails, check that your IP is whitelisted in Network Access

## Troubleshooting

**Connection Timeout**: 
- Check cluster status (might be "Paused" - click to resume)
- Verify your IP is whitelisted
- Ensure username/password are correct

**Authentication Error**:
- Double-check password in connection string
- Make sure database user has proper permissions

**Cluster Paused**:
- Free clusters pause after inactivity
- Click "Resume" in Atlas dashboard

## Connection String Format

The final connection string in your .env file should NOT have angle brackets:
```
MONGO_URI=mongodb+srv://admin:ActualPassword123@cluster0.abc12.mongodb.net/?retryWrites=true&w=majority
```

NOT:
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```
