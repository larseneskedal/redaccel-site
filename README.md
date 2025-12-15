# Reddit Comment Tool

A Python tool for finding high-traffic Reddit threads by keywords and generating human-like, subtly promotional comments that you can copy-paste.

## Features

- 🔍 **Smart Reddit Search**: Finds the highest-traffic threads for any keyword
- 🤖 **AI-Powered Comments**: Generates natural, human-like comments using GPT
- 🎯 **Subtle Promotion**: Weaves promotional content naturally into helpful comments
- 📋 **Copy-Paste Ready**: Formatted output with links and comments ready to use
- ⚡ **Engagement Scoring**: Ranks posts by engagement (upvotes + comments)

## Setup

### Quick Start (3 Steps)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get API Keys:**
   - 📖 **Full Guide:** See `API_SETUP.md` for detailed instructions
   - 📋 **Quick Reference:** See `SETUP_QUICK_START.txt`
   
   **Direct Links:**
   - 🔴 **Reddit API:** https://www.reddit.com/prefs/apps
   - 🤖 **OpenAI API:** https://platform.openai.com/api-keys
   - 📊 **Ahrefs API (optional):** https://ahrefs.com/api

3. **Add Keys to .env File:**
   ```bash
   # Copy the template
   cp ENV_TEMPLATE.txt .env
   
   # Then edit .env and paste your keys
   ```

   Or create `.env` manually with:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USER_AGENT=RedditCommentTool/1.0 by yourusername
   OPENAI_API_KEY=your_openai_key
   AHREFS_API_TOKEN=your_ahrefs_token  (optional)
   ```

## Usage

### Web Interface (Recommended)

Start the web server:

```bash
python app.py
```

Then open your browser to:
```
http://localhost:5000
```

The web interface provides:
- Easy-to-use form for searching
- Visual display of posts with engagement metrics
- One-click comment generation
- Copy-to-clipboard functionality
- Real-time configuration checking

### Command Line Interface

```bash
python reddit_comment_tool.py "keyword"
```

### Advanced Options

```bash
# Get top 10 posts with 2 comment variations each
python reddit_comment_tool.py "python programming" -n 10 -c 2

# Override promotion settings
python reddit_comment_tool.py "web development" \
  --promotion-target "MyWebDevTool" \
  --promotion-context "A tool that helps developers build faster"

# Just find posts without generating comments
python reddit_comment_tool.py "keyword" --no-generate
```

### Options

- `keyword`: The search term to find Reddit posts (required)
- `-n, --number`: Number of top posts to process (default: 5)
- `-c, --comments`: Number of comment variations per post (default: 1)
- `--promotion-target`: What to promote (overrides .env)
- `--promotion-context`: Context about promotion (overrides .env)
- `--no-generate`: Only show posts, skip comment generation

## Output Format

The tool outputs:
- A table showing top posts with engagement metrics
- Formatted sections with:
  - Post title and metadata
  - Direct link to the post
  - Generated comments ready to copy-paste

## Example

```bash
$ python reddit_comment_tool.py "remote work" -n 3

Reddit Comment Tool

Searching for: remote work
Top posts: 3

✓ Reddit API connected
Searching Reddit for 'remote work'...
✓ Found 3 high-traffic posts

[Table showing top 3 posts]

Generating 1 comment(s) per post...
✓ Generated comments

============================================================
READY TO COPY-PASTE
============================================================

[Formatted output with links and comments]
```

## How It Works

1. **Search**: Uses Reddit's search API to find posts containing your keyword
2. **Rank**: Calculates engagement scores (upvotes + comments × 2)
3. **Filter**: Only includes posts with significant engagement (>10 points)
4. **Generate**: Uses GPT to create natural, contextually relevant comments
5. **Format**: Outputs everything in a copy-paste friendly format

## Tips for Best Results

- Use specific keywords related to your niche
- Adjust `-n` to get more or fewer posts
- Use `-c 2` or `-c 3` to get multiple comment variations to choose from
- Make sure your `PROMOTION_CONTEXT` in `.env` clearly describes what you're promoting
- Review generated comments before posting to ensure they fit the context

## Notes

- Reddit API has rate limits - be respectful
- OpenAI API usage incurs costs (GPT-4o-mini is cost-effective)
- Always review and customize comments before posting
- Follow Reddit's rules and guidelines when posting

## License

MIT License - Use responsibly and ethically.

