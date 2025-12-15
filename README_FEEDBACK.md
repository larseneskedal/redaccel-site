# Product Feedback Simulator - AI-Powered Human Feedback Tool

A comprehensive AI-powered tool that simulates thousands of virtual users to provide human-like product feedback, sentiment analysis, and MRR estimation. Better than Vicaura with enhanced features and insights.

## 🚀 Features

### Core Capabilities
- **🤖 Multi-Persona AI Simulation**: Simulate feedback from 6 different user personas:
  - Early Adopter (tech-savvy, innovation-focused)
  - Skeptic (cautious, analytical)
  - Power User (feature-focused, demanding)
  - Budget-Conscious (price-sensitive, value-seeking)
  - Casual User (simplicity-focused)
  - Enterprise Buyer (ROI and security-focused)

- **💬 Human-Like Feedback**: Generate realistic, detailed feedback that mimics real user interactions
- **📊 Sentiment Analysis**: Automatic sentiment classification (positive/neutral/negative)
- **💰 MRR Estimation**: Predict potential Monthly Recurring Revenue based on purchase intent
- **📈 Growth Projections**: 1, 3, 6, and 12-month revenue projections
- **🎯 Purchase Intent Scoring**: 0-100% purchase intent per persona
- **💡 Key Insights & Recommendations**: AI-generated actionable insights
- **📉 Visual Analytics**: Interactive charts and dashboards

### Enhanced Features (Better than Vicaura)
- ✅ **Multiple Personas**: 6 distinct user types vs. generic simulation
- ✅ **Detailed Interaction Steps**: 3-stage user journey simulation
- ✅ **Real-time Analytics Dashboard**: Beautiful, interactive visualizations
- ✅ **Pricing Tier Analysis**: Multi-tier pricing breakdown and MRR calculation
- ✅ **Confidence Scoring**: Data quality indicators
- ✅ **Export-Ready Insights**: Structured feedback for easy analysis
- ✅ **Sentiment Distribution**: Visual sentiment breakdown across all users
- ✅ **Persona-Specific Metrics**: Deep dive into each user type's behavior

## 📋 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API

1. Get an API key from https://platform.openai.com/api-keys
2. Add credits to your OpenAI account if needed

### 3. Create Environment File

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎮 Usage

### Web Interface (Recommended)

Start the web server:

```bash
python feedback_app.py
```

Then open your browser to:
```
http://localhost:5000
```

### Using the Dashboard

1. **Enter Product Information**:
   - Product name
   - Product description
   - Product features (one per line)
   - Optional: Pricing and target audience

2. **Select Personas**: Choose which user personas to simulate (default: all)

3. **Configure Simulation**:
   - Set number of users per persona (default: 5)
   - Set target market size (default: 10,000)

4. **Run Simulation**: Click "Simulate Feedback" to generate feedback

5. **Review Results**:
   - View overview metrics (purchase intent, sentiment)
   - Analyze persona breakdown
   - Review key insights and recommendations
   - Explore detailed feedback by persona

6. **Estimate MRR**:
   - Add pricing tiers (name, price, percentage of users)
   - Ensure percentages sum to 100%
   - Click "Estimate MRR" to get revenue projections

## 📊 Understanding the Results

### Overview Metrics
- **Total Users Simulated**: Number of virtual users that provided feedback
- **Average Purchase Intent**: Overall purchase likelihood (0-100%)
- **Positive Sentiment**: Percentage of users with positive sentiment
- **Conversion Rate**: Estimated conversion rate based on feedback

### Persona Breakdown
Each persona shows:
- Number of users simulated
- Average purchase intent for that persona
- Sentiment distribution (positive/neutral/negative)

### MRR Estimation
- **Estimated MRR**: Monthly recurring revenue projection
- **Estimated ARR**: Annual recurring revenue
- **Total Conversions**: Number of expected conversions
- **Confidence Score**: Quality indicator based on sample size
- **Growth Projections**: Revenue forecasts for months 1, 3, 6, and 12
- **Tier Breakdown**: MRR contribution by pricing tier

### Key Insights & Recommendations
AI-generated insights covering:
- Common pain points
- Feature requests
- Pricing feedback
- User experience issues
- Improvement opportunities

## 🎯 Use Cases

1. **Product Validation**: Test product concepts before launch
2. **Feature Prioritization**: Understand which features matter most
3. **Pricing Strategy**: Validate pricing tiers and optimize revenue
4. **Market Research**: Understand different user segments
5. **MRR Forecasting**: Estimate potential revenue before launch
6. **User Experience Testing**: Identify UX issues early
7. **Competitive Analysis**: Compare feedback across personas

## 🔧 Technical Details

### Personas
Each persona has unique characteristics:
- **Purchase Probability**: Base likelihood to purchase
- **Price Sensitivity**: How price affects decisions
- **Traits**: Behavioral characteristics
- **Interaction Style**: How they evaluate products

### MRR Calculation
The MRR estimator uses:
- Purchase intent from feedback (0-100%)
- Sentiment multiplier (positive sentiment boosts conversion)
- Target market size
- Pricing tier distribution
- Realistic conversion rate mapping

### Confidence Scoring
- Based on sample size
- 30+ users = 100% confidence
- Scales linearly with fewer users

## 💡 Tips for Best Results

1. **Detailed Product Descriptions**: More context = better feedback
2. **Comprehensive Features List**: Include all key features
3. **Realistic Pricing**: Use actual or planned pricing
4. **Multiple Personas**: Simulate all personas for comprehensive insights
5. **Adequate Sample Size**: 5+ users per persona recommended
6. **Review Insights**: Always review AI-generated insights for accuracy

## 📝 Example

```python
# Product: TaskMaster Pro
# Description: AI-powered task management tool for teams
# Features:
# - AI task prioritization
# - Team collaboration
# - Time tracking
# - Analytics dashboard
# Pricing: $29/month (Basic), $99/month (Pro)
# Target Audience: Small business teams

# Results might show:
# - Early Adopters: 75% purchase intent
# - Skeptics: 25% purchase intent
# - Overall: 55% average purchase intent
# - Estimated MRR: $15,000 (with 10,000 market size)
```

## 🆚 Comparison with Vicaura

| Feature | Vicaura | This Tool |
|---------|---------|-----------|
| Personas | Generic | 6 distinct personas |
| Feedback Detail | Basic | Multi-stage interactions |
| Analytics | Limited | Comprehensive dashboard |
| Pricing Analysis | Basic | Multi-tier breakdown |
| Growth Projections | No | Yes (1, 3, 6, 12 months) |
| Confidence Scoring | No | Yes |
| Sentiment Analysis | Basic | Detailed with charts |
| Export/Insights | Limited | Structured insights |

## ⚠️ Notes

- OpenAI API usage incurs costs (GPT-4o-mini is cost-effective)
- Results are estimates based on AI simulation, not real user data
- Always validate with real users when possible
- MRR estimates are projections, actual results may vary
- Sample size affects confidence scores

## 🔒 Privacy & Security

- All processing happens locally or via OpenAI API
- No product data is stored permanently
- API keys are stored in `.env` file (not committed to git)

## 📄 License

MIT License - Use responsibly and ethically.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Built with ❤️ for startups and businesses who want better product feedback**
