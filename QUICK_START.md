# Quick Start Guide

## Starting the Web Server

### Option 1: Using the startup script (Recommended)
```bash
./start_server.sh
```

### Option 2: Direct Python command
```bash
python3 app.py
```

### Option 3: If you have a virtual environment
```bash
source venv/bin/activate  # or: . venv/bin/activate
python app.py
```

## After Starting

Once you see the message "Server running at: http://localhost:5000", open your web browser and go to:

**http://localhost:5000**

## Troubleshooting

### Port 5000 already in use?
If you get an error about port 5000 being in use, you can:
1. Kill the process using port 5000:
   ```bash
   lsof -ti:5000 | xargs kill -9
   ```
2. Or change the port in `app.py` (line 95) to a different port like 5001

### Dependencies not installed?
```bash
pip3 install -r requirements.txt
```

### Configuration errors?
Make sure you have a `.env` file with your API credentials. See `config_template.txt` for the format.

### Still having issues?
1. Make sure Python 3.7+ is installed: `python3 --version`
2. Check that all dependencies are installed
3. Verify your `.env` file exists and has correct values
4. Check the terminal output for specific error messages

