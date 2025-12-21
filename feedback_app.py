"""
Flask web application for Product Feedback Simulator.
"""
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from product_feedback_simulator import ProductFeedbackSimulator, Persona
from mrr_estimator import MRREstimator
from website_analyzer import WebsiteAnalyzer
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Initialize components
simulator = None
mrr_estimator = None
website_analyzer = None


def init_components():
    """Initialize feedback simulator, MRR estimator, and website analyzer."""
    global simulator, mrr_estimator, website_analyzer
    try:
        simulator = ProductFeedbackSimulator()
        mrr_estimator = MRREstimator()
        website_analyzer = WebsiteAnalyzer()
        return True, None
    except Exception as e:
        return False, str(e)


@app.route('/')
def index():
    """Main page."""
    return render_template('feedback_dashboard.html')


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Simulate product feedback from multiple personas."""
    if simulator is None:
        success, error = init_components()
        if not success:
            return jsonify({'error': f'Initialization error: {error}'}), 500
    
    data = request.json
    product_name = data.get('product_name', '').strip()
    product_description = data.get('product_description', '').strip()
    product_features = data.get('product_features', [])
    pricing = data.get('pricing', '').strip()
    target_audience = data.get('target_audience', '').strip()
    persona_types = data.get('persona_types', None)
    num_users_per_persona = int(data.get('num_users_per_persona', 2))  # Default to 2 for speed
    
    if not product_name or not product_description:
        return jsonify({'error': 'Product name and description are required'}), 400
    
    if not product_features:
        return jsonify({'error': 'At least one product feature is required'}), 400
    
    try:
        aggregated_feedback = simulator.simulate_multiple_personas(
            product_name=product_name,
            product_description=product_description,
            product_features=product_features,
            pricing=pricing if pricing else None,
            target_audience=target_audience if target_audience else None,
            persona_types=persona_types,
            num_users_per_persona=num_users_per_persona
        )
        
        return jsonify({'success': True, 'feedback': aggregated_feedback})
    except Exception as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            return jsonify({'error': 'Simulation timed out. Try with fewer users per persona (2 recommended).'}), 500
        return jsonify({'error': error_msg}), 500


@app.route('/api/estimate-mrr', methods=['POST'])
def estimate_mrr():
    """Estimate MRR based on feedback and pricing."""
    if mrr_estimator is None:
        success, error = init_components()
        if not success:
            return jsonify({'error': f'Initialization error: {error}'}), 500
    
    data = request.json
    aggregated_feedback = data.get('feedback', {})
    pricing_tiers = data.get('pricing_tiers', [])
    target_market_size = int(data.get('target_market_size', 10000))
    
    if not pricing_tiers:
        return jsonify({'error': 'At least one pricing tier is required'}), 400
    
    try:
        mrr_estimate = mrr_estimator.estimate_mrr(
            aggregated_feedback=aggregated_feedback,
            pricing_tiers=pricing_tiers,
            target_market_size=target_market_size
        )
        
        arr_estimate = mrr_estimator.estimate_arr(mrr_estimate)
        
        return jsonify({
            'success': True,
            'mrr_estimate': mrr_estimate,
            'arr_estimate': arr_estimate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/personas', methods=['GET'])
def get_personas():
    """Get available personas."""
    personas = Persona.get_all_personas()
    persona_info = {}
    
    for persona_type in personas:
        info = Persona.get_persona_info(persona_type)
        persona_info[persona_type] = info
    
    return jsonify({
        'success': True,
        'personas': persona_info
    })


@app.route('/api/analyze-website', methods=['POST'])
def analyze_website():
    """Analyze a website and extract product information."""
    if website_analyzer is None:
        success, error = init_components()
        if not success:
            return jsonify({'error': f'Initialization error: {error}'}), 500
    
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        product_info = website_analyzer.analyze_website(url)
        return jsonify({'success': True, 'product_info': product_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-config', methods=['GET'])
def check_config():
    """Check if configuration is set up."""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return jsonify({
        'openai_configured': openai_configured
    })


if __name__ == '__main__':
    # Try to initialize on startup
    init_components()
    print("\n" + "="*60)
    print("🚀 Product Feedback Simulator - Web Server Starting")
    print("="*60)
    print("\n📍 Server running at: http://localhost:5000")
    print("📝 Open this URL in your browser to use the tool")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
