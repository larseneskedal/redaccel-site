# Complete Setup Guide

## Prerequisites

1. **Install Xcode Command Line Tools** (if not already installed):
   ```bash
   xcode-select --install
   ```
   Follow the prompts to install.

2. **Python 3** should be installed (comes with macOS)

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script:
```bash
./setup.sh
```

### Option 2: Manual Setup

1. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Create .env file**:
   ```bash
   cp config_template.txt .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Start the server**:
   ```bash
   python3 feedback_app.py
   ```

4. **Open in browser**:
   Navigate to: http://localhost:5000

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and paste it into your `.env` file

## Testing the Setup

Once everything is installed, you can test with:

```bash
python3 -c "from product_feedback_simulator import ProductFeedbackSimulator; print('✅ Setup successful!')"
```

## Troubleshooting

### If pip install fails:
- Make sure Xcode command line tools are installed
- Try: `python3 -m pip install --user -r requirements.txt`

### If the server won't start:
- Check that your `.env` file exists and has `OPENAI_API_KEY` set
- Make sure port 5000 is not in use

### If you get import errors:
- Make sure all dependencies are installed: `pip3 list`
- Reinstall: `pip3 install -r requirements.txt --force-reinstall`

## Next Steps

Once set up, read `QUICK_START_FEEDBACK.md` to learn how to use the tool!
