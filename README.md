# Redaccel Website Build

Website for Redaccel with blog, pricing, and about pages.

## Features

- 🏠 Homepage
- 📝 Blog with multiple articles
- 💰 Pricing page
- ℹ️ About page
- 🎨 Modern design

## Quick Start

1. **Open this project in Cursor:**
   - File → Open Folder...
   - Navigate to: `/Users/johanlarsen/Redaccel-Website-Build`
   - Click "Open"

2. **Set up environment:**
   Create a `.env` file in the project root with your Hostinger email credentials:
   ```bash
   # Hostinger Email Configuration
   MAIL_SERVER=smtp.hostinger.com
   MAIL_PORT=465
   MAIL_USERNAME=contact@redaccel.com
   MAIL_PASSWORD=your_email_password_here
   MAIL_DEFAULT_SENDER=contact@redaccel.com
   ```
   
   **Important:** Replace `your_email_password_here` with your actual Hostinger email password.
   
   The contact form will send all inquiries to `contact@redaccel.com` using these SMTP settings.

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python3 redaccel_app.py
   # Or use the start script:
   ./start_redaccel.sh
   ```

## Project Files

- `redaccel_app.py` - Main Flask application
- `templates/redaccel.html` - Homepage
- `templates/blog.html` - Blog listing
- `templates/blog/*.html` - Blog articles
- `templates/pricing.html` - Pricing page
- `templates/about.html` - About page
- `static/css/redaccel.css` - Styling
- `static/js/redaccel.js` - JavaScript

## This is a Separate Project

This project is completely independent. Opening it in Cursor will show only this project's files.

