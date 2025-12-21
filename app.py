"""
Flask web application for Reddit Comment Tool.
"""
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from reddit_scraper import RedditScraper
from comment_generator import CommentGenerator
from website_scraper import WebsiteScraper
from demo_mode import generate_demo_posts
from datetime import datetime
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)

# Initialize components
scraper = None
generator = None
website_scraper = WebsiteScraper()
demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

def init_components():
    """Initialize Reddit scraper and comment generator."""
    global scraper, generator
    try:
        scraper = RedditScraper()
    except Exception as e:
        scraper = None
        print(f"Warning: Reddit scraper initialization failed: {e}")
    
    try:
        generator = CommentGenerator()
    except Exception as e:
        generator = None
        print(f"Warning: Comment generator initialization failed: {e}")
    
    return True, None


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/scrape-website', methods=['POST'])
def scrape_website():
    """Scrape website to understand what's being promoted."""
    data = request.json
    website_url = data.get('website_url', '').strip()
    
    if not website_url:
        return jsonify({'error': 'Website URL is required'}), 400
    
    try:
        website_info = website_scraper.scrape_website(website_url)
        return jsonify({'success': True, 'website_info': website_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    """Search for Reddit posts."""
    data = request.json
    keyword = data.get('keyword', '').strip()
    top_n = int(data.get('number', 5))
    use_demo = data.get('use_demo', False) or demo_mode
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    # Use demo mode if Reddit API not configured or demo requested
    if use_demo or scraper is None:
        try:
            init_components()
            if scraper is None:
                # Use demo mode
                posts = generate_demo_posts(keyword, top_n)
                return jsonify({
                    'success': True, 
                    'posts': posts,
                    'demo_mode': True,
                    'message': 'Using demo mode - Reddit API not configured. Get credentials at: https://www.reddit.com/prefs/apps'
                })
        except:
            # Fallback to demo mode
            posts = generate_demo_posts(keyword, top_n)
            return jsonify({
                'success': True, 
                'posts': posts,
                'demo_mode': True,
                'message': 'Using demo mode - Reddit API not configured. Get credentials at: https://www.reddit.com/prefs/apps'
            })
    
    # Try real Reddit API
    try:
        prioritize_traffic = data.get('prioritize_traffic', True)
        posts = scraper.get_top_posts(keyword, top_n=top_n, prioritize_traffic=prioritize_traffic)
        
        # Convert datetime objects to strings for JSON serialization
        for post in posts:
            if isinstance(post.get('created_utc'), datetime):
                post['created_utc'] = post['created_utc'].isoformat()
        
        return jsonify({'success': True, 'posts': posts, 'demo_mode': False})
    except Exception as e:
        error_msg = str(e)
        # If Reddit API fails, fall back to demo mode
        if '401' in error_msg or 'unauthorized' in error_msg.lower() or '403' in error_msg:
            posts = generate_demo_posts(keyword, top_n)
            return jsonify({
                'success': True,
                'posts': posts,
                'demo_mode': True,
                'message': 'Reddit API authentication failed. Using demo mode. Get credentials at: https://www.reddit.com/prefs/apps'
            })
        else:
            return jsonify({'error': error_msg, 'details': 'Check server logs for more information'}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate comments for posts."""
    if generator is None:
        init_components()
        if generator is None:
            return jsonify({'error': 'OpenAI API not configured. Please check your .env file with OPENAI_API_KEY'}), 500
    
    data = request.json
    posts = data.get('posts', [])
    comment_count = int(data.get('comment_count', 1))
    promotion_target = data.get('promotion_target', '').strip()
    promotion_context = data.get('promotion_context', '').strip()
    website_info = data.get('website_info', None)
    
    if not posts:
        return jsonify({'error': 'No posts provided'}), 400
    
    try:
        comments_dict = generator.generate_multiple_comments(
            posts,
            count=comment_count,
            promotion_target=promotion_target if promotion_target else None,
            promotion_context=promotion_context if promotion_context else None,
            website_info=website_info
        )
        
        return jsonify({'success': True, 'comments': comments_dict})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-posts', methods=['POST'])
def generate_posts():
    """Generate post ideas and subreddit suggestions for a product."""
    if generator is None:
        init_components()
        if generator is None:
            return jsonify({'error': 'OpenAI API not configured. Please check your .env file with OPENAI_API_KEY'}), 500

    data = request.json
    product_url = data.get('product_url', '').strip()
    context = data.get('context', '').strip()
    count = max(3, min(int(data.get('count', 5)), 10))

    if not product_url:
        return jsonify({'error': 'Product URL is required'}), 400

    # Scrape site to understand product
    website_info = website_scraper.scrape_website(product_url)
    domain = website_info.get('domain', '')

    prompt = f"""
You are helping to write natural Reddit posts for a product.

Product URL: {product_url}
Domain / brand name to use when mentioning the product: {domain}

Website info:
Title: {website_info.get('title','')}
Description: {website_info.get('description','')}
Summary: {website_info.get('summary','')}

Extra context from user: {context or "None"}

TASK 1: Generate {count} different Reddit post ideas that feel natural and human-written.

STRICT RULES ABOUT MENTIONS:
- At least 3 of the posts MUST explicitly mention the product/brand using the domain or brand name above.
- When you mention the product, use the brand name or domain exactly as given in the \"Domain / brand name\" line.
- Those product mentions must appear only once in the text of that post (no repeating the brand name).
- The remaining posts MUST NOT mention the product or brand at all (they should be about the problem, story, or situation only).

LENGTH & VARIETY:
- At least 2 of the posts should be longer, \"effortful\" posts (e.g. mini case studies or detailed experiences).
  * For these, write 2-4 short paragraphs or 6-10 natural sentences.
- The other posts can be shorter (e.g. 1-3 short paragraphs or 3-6 sentences; some can be simple questions).

TONE & STYLE:
- Mix formats: questions, mini case studies, asking for tips, soft recommendations, personal stories.
- All posts must sound like real Reddit content, not marketing copy.
- Do NOT use obvious ad language (no "check out", "special offer", "limited time", etc.).

For each post, return:
- title: the Reddit post title
- body: the Reddit post body (respecting the length guidelines above)
- type: e.g. "case study", "question", "recommendation", "story"

TASK 2: Suggest 5 subreddits that are good targets for this kind of product.
- Value low/medium moderation (marketing allowed or tolerated)
- High relevance to the problem / audience
- Reasonable size and activity (not tiny, not dead)

Return strict JSON with this structure:
{{
  "posts": [
    {{"title": "...", "body": "...", "type": "..."}},
    ...
  ],
  "subreddits": [
    {{"name": "subreddit_name", "reason": "why it fits"}},
    ...
  ]
}}
"""

    try:
        resp = generator.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write natural Reddit content and JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=800,
        )
        import json

        content = resp.choices[0].message.content.strip()
        # Best-effort parse
        json_start = content.find("{")
        json_obj = json.loads(content[json_start:])
        return jsonify(
            {
                "success": True,
                "posts": json_obj.get("posts", []),
                "subreddits": json_obj.get("subreddits", []),
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error generating posts: {e}"}), 500


@app.route('/api/generate-thread-comments', methods=['POST'])
def generate_thread_comments():
    """Generate a mix of natural-looking comments for a given thread."""
    if generator is None:
        init_components()
        if generator is None:
            return jsonify({'error': 'OpenAI API not configured. Please check your .env file with OPENAI_API_KEY'}), 500

    data = request.json
    thread_url = data.get('thread_url', '').strip()
    thread_content = data.get('thread_content', '').strip()
    count = max(5, min(int(data.get('count', 10)), 15))

    if not thread_url and not thread_content:
        return jsonify({'error': 'Provide thread_url or thread_content'}), 400

    # If URL provided, we could scrape basic info in future; for now we just pass it through
    parsed = urlparse(thread_url) if thread_url else None

    prompt = f"""
You are simulating a realistic Reddit thread.

Thread URL (if any): {thread_url or "N/A"}
Thread content (title + body): {thread_content or "N/A"}

Generate {count} comments that make this thread look like a normal, active Reddit discussion.

The comments should:
- Not all be promotional (most should be neutral, curious, opinionated, or helpful)
- Mix roles: some questions, some answers, some recommendations, some short reactions, some mild disagreements, some sharing experiences
- A few can very subtly mention a product or solution, but keep it natural and not salesy
- Use typical Reddit tone (casual, varied lengths, some very short, some a bit longer)

Return strict JSON like:
{{
  "comments": [
    {{"role": "question", "text": "..."}},
    {{"role": "answer", "text": "..."}},
    ...
  ]
}}
"""
    try:
        resp = generator.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate realistic multi-user Reddit threads and output JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.95,
            max_tokens=800,
        )
        import json

        content = resp.choices[0].message.content.strip()
        json_start = content.find("{")
        json_obj = json.loads(content[json_start:])
        return jsonify({"success": True, "comments": json_obj.get("comments", [])})
    except Exception as e:
        return jsonify({"error": f"Error generating thread comments: {e}"}), 500


@app.route('/api/check-config', methods=['GET'])
def check_config():
    """Check if configuration is set up."""
    reddit_id = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_agent = os.getenv("REDDIT_USER_AGENT", "")
    
    # Check if Reddit credentials are actual values (not placeholders)
    reddit_configured = all([
        reddit_id and reddit_id not in ['your_client_id_here', 'your_reddit_client_id', ''],
        reddit_secret and reddit_secret not in ['your_client_secret_here', 'your_reddit_client_secret', ''],
        reddit_agent and 'your_username' not in reddit_agent and 'your_app_name' not in reddit_agent
    ])
    
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_configured = bool(openai_key and 'your_openai' not in openai_key.lower() and openai_key.startswith('sk-'))
    
    ahrefs_token = os.getenv("AHREFS_API_TOKEN", "")
    ahrefs_configured = bool(ahrefs_token and 'your_ahrefs' not in ahrefs_token.lower() and ahrefs_token != '')
    
    return jsonify({
        'reddit_configured': reddit_configured,
        'openai_configured': openai_configured,
        'ahrefs_configured': ahrefs_configured,
        'promotion_target': os.getenv("PROMOTION_TARGET", ""),
        'promotion_context': os.getenv("PROMOTION_CONTEXT", "")
    })


if __name__ == '__main__':
    # Try to initialize on startup
    init_components()
    print("\n" + "="*60)
    print("🚀 Reddit Comment Tool - Web Server Starting")
    print("="*60)
    print("\n📍 Server running at: http://localhost:5001")
    print("📝 Open this URL in your browser to use the tool")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5001)

