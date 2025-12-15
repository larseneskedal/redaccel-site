# Quick Start Guide - Product Feedback Simulator

Get started in 3 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Key

Create a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

## Step 3: Start the Server

```bash
python feedback_app.py
```

Or use the startup script:

```bash
./start_feedback_server.sh
```

## Step 4: Open in Browser

Navigate to: http://localhost:5000

## Step 5: Run Your First Simulation

1. Enter your product information:
   - **Product Name**: e.g., "TaskMaster Pro"
   - **Description**: Brief description of your product
   - **Features**: List features (one per line)
   - **Pricing**: Optional (e.g., "$29/month")
   - **Target Audience**: Optional (e.g., "Small businesses")

2. Select personas (or use all)

3. Click "🚀 Simulate Feedback"

4. Review results and insights

5. Add pricing tiers and click "💰 Estimate MRR"

## Example Input

**Product Name**: AI Writing Assistant

**Description**: An AI-powered writing tool that helps content creators write faster and better with real-time suggestions and grammar checking.

**Features**:
- Real-time AI suggestions
- Grammar and style checking
- Multi-language support
- Team collaboration
- Analytics dashboard

**Pricing**: $19/month (Starter), $49/month (Pro)

**Target Audience**: Content creators and marketing teams

## What You'll Get

✅ Feedback from 6 different user personas  
✅ Sentiment analysis (positive/neutral/negative)  
✅ Purchase intent scores (0-100%)  
✅ Key insights and recommendations  
✅ MRR and ARR estimates  
✅ Growth projections (1, 3, 6, 12 months)  
✅ Pricing tier breakdown  

## Tips

- Be specific in your product description
- Include all key features
- Use realistic pricing
- Simulate 5+ users per persona for better accuracy
- Review insights carefully - they're AI-generated

## Need Help?

Check the full README: `README_FEEDBACK.md`

---

**Ready to get insights? Start the server and begin simulating!** 🚀
