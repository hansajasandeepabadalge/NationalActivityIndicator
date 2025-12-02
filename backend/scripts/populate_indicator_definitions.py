import sys
import os
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal, engine
from app.models.indicator import IndicatorDefinition, Base

def init_db():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

def populate_indicators():
    session = SessionLocal()
    try:
        indicators = [
            # Political
            {
                "indicator_code": "POL_UNREST_01",
                "indicator_name": "Protest Frequency Index",
                "display_name": "Political Unrest Level",
                "pestel_category": "Political",
                "subcategory": "Civil Unrest",
                "calculation_type": "frequency_count",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Measures frequency and intensity of protests"
            },
            {
                "indicator_code": "POL_STABILITY_01",
                "indicator_name": "Government Stability Score",
                "display_name": "Gov Stability",
                "pestel_category": "Political",
                "subcategory": "Governance",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Sentiment towards government stability"
            },
            {
                "indicator_code": "POL_POLICY_01",
                "indicator_name": "Policy Change Rate",
                "display_name": "Policy Volatility",
                "pestel_category": "Political",
                "subcategory": "Policy",
                "calculation_type": "frequency_count",
                "value_type": "count",
                "min_value": 0,
                "max_value": 50,
                "description": "Frequency of major policy announcements"
            },
            {
                "indicator_code": "POL_ELECTION_01",
                "indicator_name": "Election Uncertainty",
                "display_name": "Election Risk",
                "pestel_category": "Political",
                "subcategory": "Elections",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Uncertainty related to upcoming elections"
            },
            {
                "indicator_code": "POL_INTL_REL_01",
                "indicator_name": "International Relations Score",
                "display_name": "Diplomatic Health",
                "pestel_category": "Political",
                "subcategory": "Diplomacy",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Sentiment of international relations"
            },

            # Economic
            {
                "indicator_code": "ECON_INFLATION_01",
                "indicator_name": "Inflation Pressure Index",
                "display_name": "Inflation Pressure",
                "pestel_category": "Economic",
                "subcategory": "Macroeconomic",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Media mentions of inflation and price hikes"
            },
            {
                "indicator_code": "ECON_CURRENCY_01",
                "indicator_name": "Currency Stability Indicator",
                "display_name": "LKR Stability",
                "pestel_category": "Economic",
                "subcategory": "Monetary",
                "calculation_type": "numeric_extraction",
                "value_type": "currency",
                "min_value": 0,
                "max_value": 500,
                "description": "Exchange rate volatility mentions"
            },
            {
                "indicator_code": "ECON_CONFIDENCE_01",
                "indicator_name": "Consumer Confidence Proxy",
                "display_name": "Consumer Confidence",
                "pestel_category": "Economic",
                "subcategory": "Consumer",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Public sentiment regarding spending and economy"
            },
            {
                "indicator_code": "ECON_BIZ_SENTIMENT_01",
                "indicator_name": "Business Sentiment Index",
                "display_name": "Business Confidence",
                "pestel_category": "Economic",
                "subcategory": "Business",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Business community outlook"
            },
            {
                "indicator_code": "ECON_SUPPLY_CHAIN_01",
                "indicator_name": "Supply Chain Health",
                "display_name": "Supply Chain Status",
                "pestel_category": "Economic",
                "subcategory": "Trade",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Disruptions in supply chains"
            },
            {
                "indicator_code": "ECON_TOURISM_01",
                "indicator_name": "Tourism Activity Index",
                "display_name": "Tourism Activity",
                "pestel_category": "Economic",
                "subcategory": "Tourism",
                "calculation_type": "frequency_count",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Mentions of tourist arrivals and bookings"
            },
            {
                "indicator_code": "ECON_STOCK_01",
                "indicator_name": "Stock Market Sentiment",
                "display_name": "Market Sentiment",
                "pestel_category": "Economic",
                "subcategory": "Financial Markets",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Sentiment towards stock market performance"
            },
            {
                "indicator_code": "ECON_EXPORT_01",
                "indicator_name": "Export Performance Index",
                "display_name": "Export Health",
                "pestel_category": "Economic",
                "subcategory": "Trade",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Performance of export sector"
            },

            # Social
            {
                "indicator_code": "SOC_SENTIMENT_01",
                "indicator_name": "Overall Public Sentiment",
                "display_name": "Public Mood",
                "pestel_category": "Social",
                "subcategory": "General",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": -100,
                "max_value": 100,
                "description": "General public happiness/unhappiness"
            },
            {
                "indicator_code": "SOC_COST_LIVING_01",
                "indicator_name": "Cost of Living Burden",
                "display_name": "Cost of Living",
                "pestel_category": "Social",
                "subcategory": "Lifestyle",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Complaints about cost of living"
            },
            {
                "indicator_code": "SOC_HEALTH_01",
                "indicator_name": "Healthcare Access Index",
                "display_name": "Healthcare Status",
                "pestel_category": "Social",
                "subcategory": "Health",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Availability and quality of healthcare"
            },
            {
                "indicator_code": "SOC_EDUCATION_01",
                "indicator_name": "Education Disruption Level",
                "display_name": "Education Status",
                "pestel_category": "Social",
                "subcategory": "Education",
                "calculation_type": "frequency_count",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Disruptions to schools and universities"
            },

            # Technological
            {
                "indicator_code": "TECH_CONNECTIVITY_01",
                "indicator_name": "Internet Connectivity Status",
                "display_name": "Internet Status",
                "pestel_category": "Technological",
                "subcategory": "Infrastructure",
                "calculation_type": "sentiment_analysis",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Internet speed and availability"
            },
            {
                "indicator_code": "TECH_POWER_01",
                "indicator_name": "Power Infrastructure Health",
                "display_name": "Power Supply",
                "pestel_category": "Technological",
                "subcategory": "Infrastructure",
                "calculation_type": "frequency_count",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Power outages and grid stability"
            },

            # Environmental
            {
                "indicator_code": "ENV_WEATHER_01",
                "indicator_name": "Weather Severity Index",
                "display_name": "Weather Severity",
                "pestel_category": "Environmental",
                "subcategory": "Weather",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Severity of weather conditions"
            },
            {
                "indicator_code": "ENV_FLOOD_01",
                "indicator_name": "Flood Risk Level",
                "display_name": "Flood Risk",
                "pestel_category": "Environmental",
                "subcategory": "Disaster",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Risk and occurrence of floods"
            },
            {
                "indicator_code": "ENV_DROUGHT_01",
                "indicator_name": "Drought Concern Index",
                "display_name": "Drought Risk",
                "pestel_category": "Environmental",
                "subcategory": "Disaster",
                "calculation_type": "keyword_density",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Risk and occurrence of drought"
            },

            # Legal
            {
                "indicator_code": "LEG_REGULATION_01",
                "indicator_name": "Regulatory Change Rate",
                "display_name": "Regulatory Change",
                "pestel_category": "Legal",
                "subcategory": "Regulation",
                "calculation_type": "frequency_count",
                "value_type": "count",
                "min_value": 0,
                "max_value": 50,
                "description": "Frequency of new regulations"
            },
            {
                "indicator_code": "LEG_LITIGATION_01",
                "indicator_name": "Corporate Litigation Index",
                "display_name": "Litigation Risk",
                "pestel_category": "Legal",
                "subcategory": "Litigation",
                "calculation_type": "frequency_count",
                "value_type": "index",
                "min_value": 0,
                "max_value": 100,
                "description": "Frequency of major corporate lawsuits"
            }
        ]

        print(f"🚀 Populating {len(indicators)} indicators...")
        
        for ind_data in indicators:
            # Transform data to match new model structure
            meta = {
                "display_name": ind_data.pop("display_name", None),
                "subcategory": ind_data.pop("subcategory", None),
                "value_type": ind_data.pop("value_type", None),
                "min_value": ind_data.pop("min_value", None),
                "max_value": ind_data.pop("max_value", None)
            }
            
            # Map code to ID
            if "indicator_code" in ind_data:
                ind_data["indicator_id"] = ind_data.pop("indicator_code")
            
            ind_data["metadata_"] = meta

            # Check if exists
            existing = session.query(IndicatorDefinition).filter_by(indicator_id=ind_data['indicator_id']).first()
            if not existing:
                indicator = IndicatorDefinition(**ind_data)
                session.add(indicator)
                print(f"   ✅ Added {ind_data['indicator_id']}")
            else:
                print(f"   ⚠️ Skipped {ind_data['indicator_id']} (Already exists)")
        
        session.commit()
        print("🎉 Indicator population complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    populate_indicators()
