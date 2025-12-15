"""
Flask web application for Redaccel marketing website.
"""
from flask import Flask, render_template, request, jsonify
import socket
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_local_ip():
    """Get the local IP address for external access."""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

@app.route('/')
def index():
    """Main marketing page."""
    return render_template('redaccel.html')

@app.route('/pricing')
def pricing():
    """Pricing page."""
    return render_template('pricing.html')

@app.route('/blog')
def blog():
    """Blog page."""
    return render_template('blog.html')

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

def send_email(name, email, company, message):
    """Send email using SMTP."""
    try:
        # Get email configuration from environment
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        smtp_username = os.getenv('MAIL_USERNAME', '')
        smtp_password = os.getenv('MAIL_PASSWORD', '')
        sender_email = os.getenv('MAIL_DEFAULT_SENDER', smtp_username or 'contact@redaccel.com')
        recipient_email = 'contact@redaccel.com'
        
        # If no credentials are set, try to send anyway (might work with some SMTP servers)
        if not smtp_username or not smtp_password:
            print("Warning: Email credentials not configured. Attempting to send without authentication.")
            # For some SMTP servers, you might be able to send without auth
            # But Gmail requires authentication
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Reply-To'] = email
        msg['Subject'] = f'New Contact Form Submission from {name}'
        
        # Email body
        email_body = f"""New contact form submission from Redaccel website:

Name: {name}
Email: {email}
Company: {company if company else 'Not provided'}

Message:
{message}

---
This email was sent from the Redaccel contact form.
"""
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Connect to server and send email
        if smtp_port == 465:
            # SSL connection
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # TLS connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        # Login if credentials are provided
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        return False, error_msg

@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submission."""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        company = data.get('company', '').strip()
        message = data.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Name, email, and message are required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        # Send email
        success, error = send_email(name, email, company, message)
        
        if success:
            return jsonify({'success': True, 'message': 'Message sent successfully! We\'ll get back to you soon.'})
        else:
            # Provide helpful error message
            error_message = 'Failed to send message. '
            if 'authentication' in error.lower() or 'login' in error.lower():
                error_message += 'Email server authentication failed. Please check your email configuration.'
            elif 'connection' in error.lower() or 'refused' in error.lower():
                error_message += 'Could not connect to email server. Please check your internet connection.'
            else:
                error_message += 'Please try again later or contact us directly at contact@redaccel.com'
            
            return jsonify({'success': False, 'error': error_message}), 500
        
    except Exception as e:
        print(f"Error in contact endpoint: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    import sys
    import atexit
    
    # Auto-start in background if requested
    if '--background' in sys.argv or '--bg' in sys.argv:
        import subprocess
        import os
        script_path = os.path.abspath(__file__)
        subprocess.Popen([sys.executable, script_path], 
                        stdout=open('redaccel_server.log', 'a'),
                        stderr=subprocess.STDOUT,
                        start_new_session=True)
        print("✅ Server starting in background...")
        print("📍 Access at: http://localhost:5002")
        print("📝 Logs: tail -f redaccel_server.log")
        sys.exit(0)
    
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print("🚀 Redaccel Marketing Website - Server Starting")
    print("="*60)
    print("\n📍 Server running at:")
    print(f"   Local:  http://localhost:5002")
    print(f"   Network: http://{local_ip}:5002")
    print("\n📝 Open either URL in your browser to view the site")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    # Register cleanup function
    def cleanup():
        print("\n🛑 Server shutting down...")
    
    atexit.register(cleanup)
    
    app.run(debug=True, host='0.0.0.0', port=5002, use_reloader=False)
