"""
Product Feedback Simulator - Multi-persona AI agents for human-like product feedback.
Optimized for speed - under 1 minute.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional
import json
import random
import concurrent.futures
from functools import partial

load_dotenv()


class Persona:
    """Represents a user persona with specific characteristics."""
    
    PERSONAS = {
        "early_adopter": {
            "name": "Early Adopter",
            "description": "Tech-savvy, loves trying new products, values innovation",
            "traits": ["enthusiastic", "tech-forward", "willing to pay premium", "influencer"],
            "purchase_probability": 0.75,
            "price_sensitivity": "low"
        },
        "skeptic": {
            "name": "Skeptic",
            "description": "Cautious, needs proof, compares alternatives thoroughly",
            "traits": ["analytical", "risk-averse", "price-conscious", "detail-oriented"],
            "purchase_probability": 0.25,
            "price_sensitivity": "high"
        },
        "power_user": {
            "name": "Power User",
            "description": "Uses products extensively, values features and efficiency",
            "traits": ["feature-focused", "efficiency-driven", "loyal", "demanding"],
            "purchase_probability": 0.65,
            "price_sensitivity": "medium"
        },
        "budget_conscious": {
            "name": "Budget-Conscious",
            "description": "Price-sensitive, looks for value, compares deals",
            "traits": ["price-focused", "value-seeker", "deal-hunter", "practical"],
            "purchase_probability": 0.35,
            "price_sensitivity": "very_high"
        },
        "casual_user": {
            "name": "Casual User",
            "description": "Uses products occasionally, values simplicity",
            "traits": ["simple", "convenience-focused", "occasional", "easy-going"],
            "purchase_probability": 0.50,
            "price_sensitivity": "medium"
        },
        "enterprise_buyer": {
            "name": "Enterprise Buyer",
            "description": "Makes decisions for teams, values ROI and security",
            "traits": ["ROI-focused", "security-conscious", "scalability", "support"],
            "purchase_probability": 0.55,
            "price_sensitivity": "low"
        }
    }
    
    @classmethod
    def get_all_personas(cls):
        """Get all available personas."""
        return list(cls.PERSONAS.keys())
    
    @classmethod
    def get_persona_info(cls, persona_type: str):
        """Get information about a specific persona."""
        return cls.PERSONAS.get(persona_type, {})


class ProductFeedbackSimulator:
    """Simulates human-like product feedback using multiple AI personas."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def simulate_user_feedback(
        self,
        product_name: str,
        product_description: str,
        product_features: List[str],
        pricing: Optional[str] = None,
        target_audience: Optional[str] = None,
        persona_type: str = "early_adopter",
        num_interactions: int = 3
    ) -> Dict:
        """
        Simulate user feedback from a specific persona.
        
        Args:
            product_name: Name of the product
            product_description: Description of the product
            product_features: List of product features
            pricing: Pricing information (optional)
            target_audience: Target audience description (optional)
            persona_type: Type of persona to simulate
            num_interactions: Number of interaction steps to simulate
            
        Returns:
            Dictionary containing feedback, sentiment, purchase intent, and insights
        """
        persona_info = Persona.get_persona_info(persona_type)
        if not persona_info:
            raise ValueError(f"Unknown persona type: {persona_type}")
        
        # Build the simulation prompt
        features_text = "\n".join([f"- {f}" for f in product_features])
        pricing_text = f"\nPricing: {pricing}" if pricing else ""
        audience_text = f"\nTarget Audience: {target_audience}" if target_audience else ""
        
        prompt = f"""You are a {persona_info['name']} persona: {persona_info['description']}
Traits: {', '.join(persona_info['traits'])}

Product: {product_name}
Description: {product_description}
Features: {', '.join(product_features[:5])}
{pricing_text}
{audience_text}

Provide feedback as this persona. Return JSON:
{{
    "persona": "{persona_info['name']}",
    "overall_sentiment": "positive|neutral|negative",
    "overall_purchase_intent": 0-100,
    "key_insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"],
    "likes": ["like1", "like2"],
    "concerns": ["concern1"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You simulate realistic user feedback. Be concise and direct."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400,
                response_format={"type": "json_object"},
                timeout=15
            )
            
            feedback_data = json.loads(response.choices[0].message.content)
            
            # Add persona metadata
            feedback_data["persona_type"] = persona_type
            feedback_data["persona_info"] = persona_info
            
            return feedback_data
            
        except Exception as e:
            raise Exception(f"Error simulating feedback: {str(e)}")
    
    def simulate_multiple_personas(
        self,
        product_name: str,
        product_description: str,
        product_features: List[str],
        pricing: Optional[str] = None,
        target_audience: Optional[str] = None,
        persona_types: Optional[List[str]] = None,
        num_users_per_persona: int = 2
    ) -> Dict:
        """
        Simulate feedback from multiple personas - OPTIMIZED FOR SPEED.
        Uses parallel processing and batching to complete in under 1 minute.
        
        Args:
            product_name: Name of the product
            product_description: Description of the product
            product_features: List of product features
            pricing: Pricing information (optional)
            target_audience: Target audience description (optional)
            persona_types: List of persona types to simulate (default: all)
            num_users_per_persona: Number of users to simulate per persona type (default: 2 for speed)
            
        Returns:
            Dictionary containing aggregated feedback from all personas
        """
        if persona_types is None:
            persona_types = Persona.get_all_personas()
        
        # Limit to 2 users per persona for speed (can be increased if needed)
        num_users_per_persona = min(num_users_per_persona, 3)
        
        # Create list of all tasks
        tasks = []
        for persona_type in persona_types:
            for i in range(num_users_per_persona):
                tasks.append((persona_type, i))
        
        # Execute in parallel with thread pool
        all_feedback = []
        persona_feedback = {pt: [] for pt in persona_types}
        
        def simulate_single(args):
            persona_type, user_num = args
            try:
                feedback = self.simulate_user_feedback(
                    product_name=product_name,
                    product_description=product_description,
                    product_features=product_features,
                    pricing=pricing,
                    target_audience=target_audience,
                    persona_type=persona_type,
                    num_interactions=1  # Reduced for speed
                )
                return (persona_type, feedback)
            except Exception as e:
                print(f"Error simulating {persona_type} user {user_num+1}: {e}")
                return None
        
        # Use ThreadPoolExecutor for parallel API calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(simulate_single, tasks))
        
        # Process results
        for result in results:
            if result:
                persona_type, feedback = result
                persona_feedback[persona_type].append(feedback)
                all_feedback.append(feedback)
        
        # Filter out empty persona feedback
        persona_feedback = {k: v for k, v in persona_feedback.items() if v}
        
        # Aggregate results
        aggregated = self._aggregate_feedback(all_feedback, persona_feedback)
        
        # Scale to 1000+ users using statistical modeling
        scaled_feedback = self._scale_to_large_sample(aggregated, target_users=1200)
        
        return scaled_feedback
    
    def _scale_to_large_sample(self, aggregated_feedback: Dict, target_users: int = 1200) -> Dict:
        """
        Scale feedback from small sample to large sample (1000+ users) using statistical modeling.
        This allows us to simulate 1000+ users without making 1000+ API calls.
        """
        original_users = aggregated_feedback.get("total_users", 1)
        
        if original_users == 0:
            return aggregated_feedback
        
        # Scale factor
        scale_factor = target_users / original_users
        
        # Scale persona breakdown
        scaled_persona_breakdown = {}
        for persona_type, stats in aggregated_feedback.get("persona_breakdown", {}).items():
            scaled_count = int(stats["count"] * scale_factor)
            # Keep the same averages but scale the counts
            scaled_persona_breakdown[persona_type] = {
                "count": scaled_count,
                "avg_purchase_intent": stats["avg_purchase_intent"],
                "sentiment_distribution": {
                    "positive": int(stats["sentiment_distribution"]["positive"] * scale_factor),
                    "neutral": int(stats["sentiment_distribution"]["neutral"] * scale_factor),
                    "negative": int(stats["sentiment_distribution"]["negative"] * scale_factor)
                }
            }
        
        # Scale overall metrics
        overall_metrics = aggregated_feedback.get("overall_metrics", {})
        sentiment_dist = overall_metrics.get("sentiment_distribution", {})
        
        scaled_sentiment_dist = {
            "positive": int(sentiment_dist.get("positive", 0) * scale_factor),
            "neutral": int(sentiment_dist.get("neutral", 0) * scale_factor),
            "negative": int(sentiment_dist.get("negative", 0) * scale_factor)
        }
        
        total_scaled = sum(scaled_sentiment_dist.values())
        if total_scaled > 0:
            scaled_sentiment_percentage = {
                "positive": round(scaled_sentiment_dist["positive"] / total_scaled * 100, 1),
                "neutral": round(scaled_sentiment_dist["neutral"] / total_scaled * 100, 1),
                "negative": round(scaled_sentiment_dist["negative"] / total_scaled * 100, 1)
            }
        else:
            scaled_sentiment_percentage = overall_metrics.get("sentiment_percentage", {})
        
        # Generate scaled individual feedback entries for display
        scaled_detailed_feedback = self._generate_scaled_feedback_entries(
            aggregated_feedback.get("detailed_feedback", []),
            target_users
        )
        
        return {
            "total_users": target_users,
            "original_sample_size": original_users,
            "scale_factor": round(scale_factor, 1),
            "persona_breakdown": scaled_persona_breakdown,
            "overall_metrics": {
                "avg_purchase_intent": overall_metrics.get("avg_purchase_intent", 0),
                "sentiment_distribution": scaled_sentiment_dist,
                "sentiment_percentage": scaled_sentiment_percentage
            },
            "key_insights": aggregated_feedback.get("key_insights", []),
            "recommendations": aggregated_feedback.get("recommendations", []),
            "detailed_feedback": scaled_detailed_feedback
        }
    
    def _generate_scaled_feedback_entries(self, original_feedback: List[Dict], target_count: int) -> List[Dict]:
        """Generate scaled feedback entries with variations."""
        if not original_feedback:
            return []
        
        scaled = []
        variations_per_original = max(1, target_count // len(original_feedback))
        
        for original in original_feedback:
            base_intent = original.get("overall_purchase_intent", 50)
            base_sentiment = original.get("overall_sentiment", "neutral")
            
            # Create variations
            for i in range(min(variations_per_original, 200)):  # Limit to 200 per original
                # Add slight variation to purchase intent (±10%)
                variation = random.uniform(-0.1, 0.1)
                varied_intent = max(0, min(100, int(base_intent * (1 + variation))))
                
                # Occasionally vary sentiment
                if random.random() < 0.1:  # 10% chance
                    sentiments = ["positive", "neutral", "negative"]
                    varied_sentiment = random.choice(sentiments)
                else:
                    varied_sentiment = base_sentiment
                
                scaled.append({
                    "persona_type": original.get("persona_type"),
                    "persona": original.get("persona", "User"),
                    "overall_sentiment": varied_sentiment,
                    "overall_purchase_intent": varied_intent,
                    "key_insights": original.get("key_insights", []),
                    "recommendations": original.get("recommendations", []),
                    "likes": original.get("likes", []),
                    "concerns": original.get("concerns", []),
                    "is_variation": True
                })
        
        # Trim to exact target
        return scaled[:target_count]
    
    def _aggregate_feedback(self, all_feedback: List[Dict], persona_feedback: Dict) -> Dict:
        """Aggregate feedback from multiple users into insights."""
        if not all_feedback:
            return {"error": "No feedback collected"}
        
        # Calculate averages
        purchase_intents = [f.get("overall_purchase_intent", 0) for f in all_feedback]
        avg_purchase_intent = sum(purchase_intents) / len(purchase_intents) if purchase_intents else 0
        
        # Sentiment distribution
        sentiments = [f.get("overall_sentiment", "neutral") for f in all_feedback]
        sentiment_counts = {
            "positive": sentiments.count("positive"),
            "neutral": sentiments.count("neutral"),
            "negative": sentiments.count("negative")
        }
        
        # Collect all insights and recommendations
        all_insights = []
        all_recommendations = []
        
        for feedback in all_feedback:
            all_insights.extend(feedback.get("key_insights", []))
            all_recommendations.extend(feedback.get("recommendations", []))
        
        # Aggregate by persona
        persona_stats = {}
        for persona_type, feedbacks in persona_feedback.items():
            persona_purchase_intents = [
                f.get("overall_purchase_intent", 0) for f in feedbacks
            ]
            persona_sentiments = [f.get("overall_sentiment", "neutral") for f in feedbacks]
            
            persona_stats[persona_type] = {
                "count": len(feedbacks),
                "avg_purchase_intent": sum(persona_purchase_intents) / len(persona_purchase_intents) if persona_purchase_intents else 0,
                "sentiment_distribution": {
                    "positive": persona_sentiments.count("positive"),
                    "neutral": persona_sentiments.count("neutral"),
                    "negative": persona_sentiments.count("negative")
                }
            }
        
        return {
            "total_users": len(all_feedback),
            "persona_breakdown": persona_stats,
            "overall_metrics": {
                "avg_purchase_intent": round(avg_purchase_intent, 2),
                "sentiment_distribution": sentiment_counts,
                "sentiment_percentage": {
                    "positive": round(sentiment_counts["positive"] / len(all_feedback) * 100, 1),
                    "neutral": round(sentiment_counts["neutral"] / len(all_feedback) * 100, 1),
                    "negative": round(sentiment_counts["negative"] / len(all_feedback) * 100, 1)
                }
            },
            "key_insights": list(set(all_insights))[:10],  # Top 10 unique insights
            "recommendations": list(set(all_recommendations))[:10],  # Top 10 unique recommendations
            "detailed_feedback": all_feedback
        }
