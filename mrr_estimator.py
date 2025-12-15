"""
MRR (Monthly Recurring Revenue) Estimation Engine.
Estimates potential MRR based on purchase intent and user feedback.
"""
from typing import Dict, List, Optional
import math


class MRREstimator:
    """Estimates potential MRR based on simulated user feedback."""
    
    def __init__(self):
        """Initialize MRR estimator."""
        pass
    
    def estimate_mrr(
        self,
        aggregated_feedback: Dict,
        pricing_tiers: List[Dict],
        target_market_size: int = 10000,
        conversion_rate_override: Optional[float] = None
    ) -> Dict:
        """
        Estimate potential MRR based on feedback and pricing.
        
        Args:
            aggregated_feedback: Aggregated feedback from ProductFeedbackSimulator
            pricing_tiers: List of pricing tiers, e.g. [{"name": "Basic", "price": 29, "percentage": 60}, ...]
            target_market_size: Total addressable market size
            conversion_rate_override: Override calculated conversion rate (optional)
            
        Returns:
            Dictionary containing MRR estimates and breakdown
        """
        if not pricing_tiers:
            raise ValueError("At least one pricing tier is required")
        
        # Get average purchase intent from feedback
        avg_purchase_intent = aggregated_feedback.get(
            "overall_metrics", {}
        ).get("avg_purchase_intent", 0)
        
        # Calculate conversion rate based on purchase intent
        # Purchase intent is 0-100, we convert to a realistic conversion rate
        # Typical SaaS conversion rates are 2-5%, so we scale purchase intent accordingly
        if conversion_rate_override is not None:
            base_conversion_rate = conversion_rate_override
        else:
            # Map purchase intent (0-100) to conversion rate (0-10%)
            # Higher purchase intent = higher conversion rate, but with diminishing returns
            base_conversion_rate = (avg_purchase_intent / 100) * 0.10
        
        # Adjust based on sentiment
        sentiment_dist = aggregated_feedback.get("overall_metrics", {}).get(
            "sentiment_percentage", {}
        )
        positive_sentiment = sentiment_dist.get("positive", 0) / 100
        
        # Sentiment multiplier: more positive sentiment = higher conversion
        sentiment_multiplier = 0.7 + (positive_sentiment * 0.6)  # Range: 0.7-1.3
        
        adjusted_conversion_rate = base_conversion_rate * sentiment_multiplier
        
        # Calculate conversions per tier
        total_conversions = target_market_size * adjusted_conversion_rate
        
        # Distribute conversions across pricing tiers
        tier_breakdown = []
        total_mrr = 0
        
        for tier in pricing_tiers:
            tier_name = tier.get("name", "Unknown")
            tier_price = tier.get("price", 0)
            tier_percentage = tier.get("percentage", 0) / 100
            
            tier_conversions = total_conversions * tier_percentage
            tier_mrr = tier_conversions * tier_price
            
            tier_breakdown.append({
                "tier": tier_name,
                "price": tier_price,
                "conversions": round(tier_conversions, 0),
                "mrr": round(tier_mrr, 2),
                "percentage": tier.get("percentage", 0)
            })
            
            total_mrr += tier_mrr
        
        # Calculate additional metrics
        overall_conversion_rate = (total_conversions / target_market_size) * 100 if target_market_size > 0 else 0
        
        # Confidence score based on feedback quality
        total_users = aggregated_feedback.get("total_users", 0)
        confidence_score = min(100, (total_users / 30) * 100)  # 30+ users = 100% confidence
        
        # Growth projections (conservative estimates)
        month_1_mrr = total_mrr
        month_3_mrr = month_1_mrr * 1.15  # 15% growth
        month_6_mrr = month_1_mrr * 1.35  # 35% growth
        month_12_mrr = month_1_mrr * 1.70  # 70% growth
        
        return {
            "estimated_mrr": round(total_mrr, 2),
            "target_market_size": target_market_size,
            "total_conversions": round(total_conversions, 0),
            "conversion_rate": round(overall_conversion_rate, 2),
            "confidence_score": round(confidence_score, 1),
            "pricing_tier_breakdown": tier_breakdown,
            "growth_projections": {
                "month_1": round(month_1_mrr, 2),
                "month_3": round(month_3_mrr, 2),
                "month_6": round(month_6_mrr, 2),
                "month_12": round(month_12_mrr, 2)
            },
            "assumptions": {
                "base_purchase_intent": round(avg_purchase_intent, 1),
                "sentiment_multiplier": round(sentiment_multiplier, 2),
                "adjusted_conversion_rate": round(adjusted_conversion_rate * 100, 2),
                "feedback_sample_size": total_users
            }
        }
    
    def estimate_arr(self, mrr_estimate: Dict) -> Dict:
        """
        Estimate Annual Recurring Revenue (ARR) from MRR.
        
        Args:
            mrr_estimate: MRR estimation dictionary
            
        Returns:
            Dictionary with ARR estimates
        """
        base_mrr = mrr_estimate.get("estimated_mrr", 0)
        arr = base_mrr * 12
        
        growth_projections = mrr_estimate.get("growth_projections", {})
        
        return {
            "estimated_arr": round(arr, 2),
            "monthly_breakdown": {
                "month_1": round(growth_projections.get("month_1", base_mrr), 2),
                "month_3": round(growth_projections.get("month_3", base_mrr * 1.15), 2),
                "month_6": round(growth_projections.get("month_6", base_mrr * 1.35), 2),
                "month_12": round(growth_projections.get("month_12", base_mrr * 1.70), 2)
            },
            "annual_revenue": round(arr, 2)
        }
