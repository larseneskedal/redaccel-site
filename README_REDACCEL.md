# Redaccel Website - Auto-Start Guide

## Automatic Server Startup

The Redaccel server is configured to run automatically. Here are the options:

### Option 1: Auto-start Script (Recommended)
Run this once to start the server in the background:
```bash
./auto_start_redaccel.sh
```

The server will start automatically and keep running.

### Option 2: VS Code/Cursor Auto-Start
The server is configured to auto-start when you open the project folder in VS Code/Cursor.

### Option 3: Manual Start
If you need to start manually:
```bash
python3 redaccel_app.py
```

### Check Server Status
```bash
curl http://localhost:5001
```

### Stop Server
```bash
pkill -f "python3 redaccel_app.py"
```

### View Logs
```bash
tail -f redaccel_server.log
```

## Access the Site

- **Local**: http://localhost:5001
- **Network**: http://192.168.10.57:5001 (your IP may vary)

## Pages Available

- `/` - Homepage
- `/blog` - Blog posts
- `/about` - About page
- `/pricing` - Pricing plans
- `/#contact` - Contact form
