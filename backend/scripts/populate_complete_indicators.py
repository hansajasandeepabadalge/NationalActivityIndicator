"""
Populate Complete Indicator Hierarchy

This script populates the indicator_definitions table with all ~105 indicators
as specified in the Layer 2 Blueprint.
"""

import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import uuid

# Complete indicator definitions based on Layer 2 Blueprint
INDICATORS = [
    # =====================================
    # POLITICAL INDICATORS (~18)
    # =====================================
    
    # Government Stability (4)
    {
        "indicator_name": "Cabinet Changes Frequency",
        "pestel_category": "Political",
        "subcategory": "Government Stability",
        "description": "Count of ministerial appointments/resignations per month",
        "calculation_type": "frequency_count",
        "keywords": ["cabinet", "minister", "resignation", "appointment", "reshuffle"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Policy Reversal Index",
        "pestel_category": "Political",
        "subcategory": "Government Stability",
        "description": "Number of announced policies that are reversed or modified",
        "calculation_type": "frequency_count",
        "keywords": ["policy reversal", "u-turn", "backtrack", "withdrawn", "cancelled"],
        "base_weight": 0.9,
        "threshold_high": 60.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Coalition Cohesion Score",
        "pestel_category": "Political",
        "subcategory": "Government Stability",
        "description": "Sentiment analysis of inter-party relations",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["coalition", "alliance", "party unity", "political alliance"],
        "base_weight": 0.8,
        "threshold_high": 75.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Leadership Approval Proxy",
        "pestel_category": "Political",
        "subcategory": "Government Stability",
        "description": "Public sentiment toward government/president",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["president", "prime minister", "government approval", "leadership"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Civil Unrest (4)
    {
        "indicator_name": "Protest Frequency Index",
        "pestel_category": "Political",
        "subcategory": "Civil Unrest",
        "description": "Count of protest events per week",
        "calculation_type": "frequency_count",
        "keywords": ["protest", "demonstration", "rally", "march", "strike action"],
        "base_weight": 1.0,
        "threshold_high": 80.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Strike Activity Score",
        "pestel_category": "Political",
        "subcategory": "Civil Unrest",
        "description": "Active strikes count, sectors affected, participation estimates",
        "calculation_type": "frequency_count",
        "keywords": ["strike", "walkout", "work stoppage", "industrial action", "labor dispute"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Public Dissatisfaction Index",
        "pestel_category": "Political",
        "subcategory": "Civil Unrest",
        "description": "Aggregate negative sentiment toward governance",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["dissatisfaction", "anger", "frustration", "discontent", "grievance"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Violence Escalation Indicator",
        "pestel_category": "Political",
        "subcategory": "Civil Unrest",
        "description": "Mentions of violence/clashes in protests",
        "calculation_type": "frequency_count",
        "keywords": ["violence", "clash", "riot", "unrest", "confrontation", "tear gas", "curfew"],
        "base_weight": 1.2,
        "threshold_high": 60.0,
        "threshold_low": 15.0
    },
    
    # International Relations (4)
    {
        "indicator_name": "Diplomatic Activity Index",
        "pestel_category": "Political",
        "subcategory": "International Relations",
        "description": "High-level visits, agreements signed",
        "calculation_type": "frequency_count",
        "keywords": ["diplomatic", "bilateral", "agreement", "state visit", "ambassador"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Trade Partnership Momentum",
        "pestel_category": "Political",
        "subcategory": "International Relations",
        "description": "New deals, partnership announcements",
        "calculation_type": "frequency_count",
        "keywords": ["trade deal", "partnership", "MoU", "cooperation", "trade agreement"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Geopolitical Tension Score",
        "pestel_category": "Political",
        "subcategory": "International Relations",
        "description": "Negative mentions of foreign relations",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["tension", "conflict", "dispute", "sanctions", "strained relations"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Regional Cooperation Index",
        "pestel_category": "Political",
        "subcategory": "International Relations",
        "description": "SAARC/BIMSTEC engagement",
        "calculation_type": "frequency_count",
        "keywords": ["SAARC", "BIMSTEC", "regional cooperation", "South Asia", "regional summit"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 30.0
    },
    
    # Election Activity (3)
    {
        "indicator_name": "Campaign Intensity Score",
        "pestel_category": "Political",
        "subcategory": "Election Activity",
        "description": "Intensity of election campaign activities",
        "calculation_type": "frequency_count",
        "keywords": ["campaign", "election", "candidate", "rally", "manifesto", "voting"],
        "base_weight": 0.8,
        "threshold_high": 80.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Voter Sentiment Tracker",
        "pestel_category": "Political",
        "subcategory": "Election Activity",
        "description": "Public sentiment towards elections",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["election", "vote", "ballot", "polling", "voter turnout"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Electoral Volatility Index",
        "pestel_category": "Political",
        "subcategory": "Election Activity",
        "description": "Changes in polling and electoral preferences",
        "calculation_type": "frequency_count",
        "keywords": ["poll", "survey", "swing", "undecided", "frontrunner"],
        "base_weight": 0.7,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    
    # Security Situation (3)
    {
        "indicator_name": "Law Order Incidents",
        "pestel_category": "Political",
        "subcategory": "Security Situation",
        "description": "Incidents affecting law and order",
        "calculation_type": "frequency_count",
        "keywords": ["crime", "arrest", "police", "security", "law enforcement"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Border Security Mentions",
        "pestel_category": "Political",
        "subcategory": "Security Situation",
        "description": "Border security and defense mentions",
        "calculation_type": "frequency_count",
        "keywords": ["border", "military", "defense", "security forces", "territorial"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Internal Conflict Signals",
        "pestel_category": "Political",
        "subcategory": "Security Situation",
        "description": "Internal security threats and conflicts",
        "calculation_type": "frequency_count",
        "keywords": ["terrorism", "extremism", "internal conflict", "insurgency", "separatism"],
        "base_weight": 1.2,
        "threshold_high": 60.0,
        "threshold_low": 15.0
    },
    
    # =====================================
    # ECONOMIC INDICATORS (~25)
    # =====================================
    
    # Macroeconomic Health (5)
    {
        "indicator_name": "GDP Growth Sentiment",
        "pestel_category": "Economic",
        "subcategory": "Macroeconomic Health",
        "description": "Positive/negative mentions of economic growth",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["GDP", "economic growth", "expansion", "recession", "contraction"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Inflation Pressure Index",
        "pestel_category": "Economic",
        "subcategory": "Macroeconomic Health",
        "description": "Price increase mentions, cost of living complaints",
        "calculation_type": "frequency_count",
        "keywords": ["inflation", "prices", "expensive", "cost of living", "price hike"],
        "base_weight": 1.1,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Currency Stability Indicator",
        "pestel_category": "Economic",
        "subcategory": "Macroeconomic Health",
        "description": "LKR volatility mentions, exchange rate concern frequency",
        "calculation_type": "frequency_count",
        "keywords": ["rupee", "exchange rate", "currency", "devaluation", "forex"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Debt Concern Level",
        "pestel_category": "Economic",
        "subcategory": "Macroeconomic Health",
        "description": "Mentions of debt crisis, IMF, restructuring",
        "calculation_type": "frequency_count",
        "keywords": ["debt", "IMF", "restructuring", "default", "loan", "bailout"],
        "base_weight": 1.1,
        "threshold_high": 80.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Fiscal Policy Direction",
        "pestel_category": "Economic",
        "subcategory": "Macroeconomic Health",
        "description": "Tax changes, government spending news",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["budget", "fiscal", "government spending", "tax policy", "revenue"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Financial Markets (4)
    {
        "indicator_name": "Stock Market Sentiment",
        "pestel_category": "Economic",
        "subcategory": "Financial Markets",
        "description": "CSE performance mentions + sentiment",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["stock market", "CSE", "shares", "trading", "market rally", "market decline"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Investment Climate Score",
        "pestel_category": "Economic",
        "subcategory": "Financial Markets",
        "description": "FDI announcements, business expansion news",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["investment", "FDI", "investor", "capital inflow", "business expansion"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Banking Sector Health",
        "pestel_category": "Economic",
        "subcategory": "Financial Markets",
        "description": "Bank stability, liquidity mentions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["bank", "banking", "liquidity", "deposits", "lending", "NPL"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Interest Rate Trend",
        "pestel_category": "Economic",
        "subcategory": "Financial Markets",
        "description": "Central Bank policy discussions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["interest rate", "CBSL", "monetary policy", "rate hike", "rate cut"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Trade & Commerce (5)
    {
        "indicator_name": "Export Performance Index",
        "pestel_category": "Economic",
        "subcategory": "Trade Commerce",
        "description": "Export growth/decline mentions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["export", "garment", "tea export", "trade surplus", "export earnings"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Import Dependency Risk",
        "pestel_category": "Economic",
        "subcategory": "Trade Commerce",
        "description": "Import restrictions, shortage concerns",
        "calculation_type": "frequency_count",
        "keywords": ["import", "shortage", "essential goods", "import ban", "LC opening"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Port Activity Indicator",
        "pestel_category": "Economic",
        "subcategory": "Trade Commerce",
        "description": "Colombo port operations, congestion",
        "calculation_type": "frequency_count",
        "keywords": ["port", "shipping", "cargo", "container", "logistics"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Trade Balance Sentiment",
        "pestel_category": "Economic",
        "subcategory": "Trade Commerce",
        "description": "Deficit/surplus discussions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["trade deficit", "trade balance", "trade surplus", "current account"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Remittance Flow Indicator",
        "pestel_category": "Economic",
        "subcategory": "Trade Commerce",
        "description": "Worker remittance trends",
        "calculation_type": "frequency_count",
        "keywords": ["remittance", "foreign workers", "expatriate", "money transfer"],
        "base_weight": 0.9,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Sectoral Performance (5)
    {
        "indicator_name": "Tourism Activity Index",
        "pestel_category": "Economic",
        "subcategory": "Sectoral Performance",
        "description": "Arrival numbers, hotel occupancy indicators",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["tourism", "tourist", "hotel", "arrivals", "vacation", "travel"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Manufacturing Health",
        "pestel_category": "Economic",
        "subcategory": "Sectoral Performance",
        "description": "Production, factory activity news",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["manufacturing", "factory", "production", "industrial output", "plant"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Agriculture Status",
        "pestel_category": "Economic",
        "subcategory": "Sectoral Performance",
        "description": "Harvest reports, crop prices, farmer concerns",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["agriculture", "farming", "harvest", "crop", "paddy", "fertilizer"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Services Sector Momentum",
        "pestel_category": "Economic",
        "subcategory": "Sectoral Performance",
        "description": "IT, BPO, professional services news",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["IT sector", "BPO", "tech services", "outsourcing", "software"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Construction Activity",
        "pestel_category": "Economic",
        "subcategory": "Sectoral Performance",
        "description": "Infrastructure projects, real estate",
        "calculation_type": "frequency_count",
        "keywords": ["construction", "infrastructure", "real estate", "building", "development"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    
    # Employment Situation (3)
    {
        "indicator_name": "Job Market Health",
        "pestel_category": "Economic",
        "subcategory": "Employment",
        "description": "Hiring announcements, layoff reports",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["jobs", "hiring", "layoff", "unemployment", "employment", "recruitment"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Wage Pressure Index",
        "pestel_category": "Economic",
        "subcategory": "Employment",
        "description": "Salary demands, minimum wage discussions",
        "calculation_type": "frequency_count",
        "keywords": ["wages", "salary", "minimum wage", "pay raise", "compensation"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Skills Gap Indicator",
        "pestel_category": "Economic",
        "subcategory": "Employment",
        "description": "Employer complaints about talent shortage",
        "calculation_type": "frequency_count",
        "keywords": ["skills gap", "talent shortage", "brain drain", "skilled workers", "training"],
        "base_weight": 0.7,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Consumer Behavior (3)
    {
        "indicator_name": "Consumer Confidence Proxy",
        "pestel_category": "Economic",
        "subcategory": "Consumer Behavior",
        "description": "Shopping sentiment, spending willingness",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["consumer", "spending", "shopping", "purchase", "buying"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Retail Activity Indicator",
        "pestel_category": "Economic",
        "subcategory": "Consumer Behavior",
        "description": "Sales reports, shopping traffic",
        "calculation_type": "frequency_count",
        "keywords": ["retail", "sales", "mall", "store", "shopping"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Savings vs Spending Ratio",
        "pestel_category": "Economic",
        "subcategory": "Consumer Behavior",
        "description": "Sentiment about saving vs consumption",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["savings", "spending", "budget", "frugal", "economize"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 40.0
    },
    
    # =====================================
    # SOCIAL INDICATORS (~17)
    # =====================================
    
    # Public Mood & Sentiment (4)
    {
        "indicator_name": "Overall Public Sentiment",
        "pestel_category": "Social",
        "subcategory": "Public Mood",
        "description": "Aggregate sentiment across all articles",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["public mood", "sentiment", "feeling", "atmosphere", "outlook"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Anxiety Level Index",
        "pestel_category": "Social",
        "subcategory": "Public Mood",
        "description": "Frequency of worry/fear/concern keywords",
        "calculation_type": "frequency_count",
        "keywords": ["anxiety", "worry", "fear", "concern", "stress", "tension"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Optimism Indicator",
        "pestel_category": "Social",
        "subcategory": "Public Mood",
        "description": "Hope/improvement/positive future mentions",
        "calculation_type": "frequency_count",
        "keywords": ["hope", "optimism", "improvement", "recovery", "bright future"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Social Media Mood",
        "pestel_category": "Social",
        "subcategory": "Public Mood",
        "description": "Trending topics sentiment",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["social media", "trending", "viral", "twitter", "facebook"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Quality of Life (4)
    {
        "indicator_name": "Cost of Living Burden",
        "pestel_category": "Social",
        "subcategory": "Quality of Life",
        "description": "Affordability concerns, poverty mentions",
        "calculation_type": "frequency_count",
        "keywords": ["cost of living", "affordable", "poverty", "struggle", "hardship"],
        "base_weight": 1.1,
        "threshold_high": 80.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Healthcare Access Index",
        "pestel_category": "Social",
        "subcategory": "Quality of Life",
        "description": "Hospital capacity, medicine shortage reports",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["healthcare", "hospital", "medicine", "health service", "treatment"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Education Disruption Level",
        "pestel_category": "Social",
        "subcategory": "Quality of Life",
        "description": "School closures, exam postponements, teacher strikes",
        "calculation_type": "frequency_count",
        "keywords": ["education", "school", "university", "exam", "student", "teacher"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Housing Affordability",
        "pestel_category": "Social",
        "subcategory": "Quality of Life",
        "description": "Rent/property price discussions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["housing", "rent", "property", "affordable housing", "accommodation"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 35.0
    },
    
    # Public Safety (3)
    {
        "indicator_name": "Crime Rate Perception",
        "pestel_category": "Social",
        "subcategory": "Public Safety",
        "description": "Crime reports, safety concerns",
        "calculation_type": "frequency_count",
        "keywords": ["crime", "theft", "robbery", "assault", "murder", "violence"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Traffic Safety Index",
        "pestel_category": "Social",
        "subcategory": "Public Safety",
        "description": "Accident reports, road safety",
        "calculation_type": "frequency_count",
        "keywords": ["traffic accident", "road safety", "collision", "pedestrian", "fatality"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Public Space Safety",
        "pestel_category": "Social",
        "subcategory": "Public Safety",
        "description": "Evening/night safety concerns",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["safety", "public space", "street safety", "harassment", "security"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Community Cohesion (3)
    {
        "indicator_name": "Inter Community Relations",
        "pestel_category": "Social",
        "subcategory": "Community Cohesion",
        "description": "Ethnic/religious harmony indicators",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["harmony", "unity", "ethnic", "religious", "community relations"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Civic Engagement Level",
        "pestel_category": "Social",
        "subcategory": "Community Cohesion",
        "description": "Volunteer activities, community initiatives",
        "calculation_type": "frequency_count",
        "keywords": ["volunteer", "charity", "community service", "civic", "initiative"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Social Support Systems",
        "pestel_category": "Social",
        "subcategory": "Community Cohesion",
        "description": "Charity, aid programs mentions",
        "calculation_type": "frequency_count",
        "keywords": ["social support", "welfare", "aid", "assistance", "help"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Demographics & Migration (3)
    {
        "indicator_name": "Migration Intention Index",
        "pestel_category": "Social",
        "subcategory": "Demographics",
        "description": "Brain drain, emigration discussions",
        "calculation_type": "frequency_count",
        "keywords": ["emigration", "migration", "brain drain", "leaving country", "abroad"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Urbanization Trends",
        "pestel_category": "Social",
        "subcategory": "Demographics",
        "description": "Rural-urban movement indicators",
        "calculation_type": "frequency_count",
        "keywords": ["urbanization", "urban migration", "city growth", "rural exodus"],
        "base_weight": 0.6,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Population Mobility",
        "pestel_category": "Social",
        "subcategory": "Demographics",
        "description": "Internal displacement, relocation",
        "calculation_type": "frequency_count",
        "keywords": ["displacement", "relocation", "refugees", "IDP", "movement"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    
    # =====================================
    # TECHNOLOGICAL INDICATORS (~14)
    # =====================================
    
    # Digital Infrastructure (4)
    {
        "indicator_name": "Internet Connectivity Status",
        "pestel_category": "Technological",
        "subcategory": "Digital Infrastructure",
        "description": "Outage reports, speed complaints, coverage gaps",
        "calculation_type": "frequency_count",
        "keywords": ["internet", "connectivity", "broadband", "wifi", "network"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Telecom Service Quality",
        "pestel_category": "Technological",
        "subcategory": "Digital Infrastructure",
        "description": "Mobile network issues",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["telecom", "mobile", "network", "coverage", "signal"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Power Infrastructure Health",
        "pestel_category": "Technological",
        "subcategory": "Digital Infrastructure",
        "description": "Load shedding frequency, power cut duration",
        "calculation_type": "frequency_count",
        "keywords": ["power cut", "load shedding", "electricity", "CEB", "blackout"],
        "base_weight": 1.1,
        "threshold_high": 80.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Transport Infrastructure",
        "pestel_category": "Technological",
        "subcategory": "Digital Infrastructure",
        "description": "Road conditions, rail service quality, airport operations",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["transport", "road", "railway", "airport", "highway", "infrastructure"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Innovation & Adoption (5)
    {
        "indicator_name": "Startup Ecosystem Health",
        "pestel_category": "Technological",
        "subcategory": "Innovation",
        "description": "Funding announcements, new company launches",
        "calculation_type": "frequency_count",
        "keywords": ["startup", "entrepreneur", "funding", "incubator", "accelerator"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Digital Payment Adoption",
        "pestel_category": "Technological",
        "subcategory": "Innovation",
        "description": "Fintech, mobile money usage",
        "calculation_type": "frequency_count",
        "keywords": ["digital payment", "mobile money", "fintech", "e-wallet", "online banking"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "E-Commerce Growth",
        "pestel_category": "Technological",
        "subcategory": "Innovation",
        "description": "Online shopping trends",
        "calculation_type": "frequency_count",
        "keywords": ["e-commerce", "online shopping", "digital commerce", "delivery"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Tech Investment Flow",
        "pestel_category": "Technological",
        "subcategory": "Innovation",
        "description": "Tech sector investments",
        "calculation_type": "frequency_count",
        "keywords": ["tech investment", "technology sector", "IT investment", "digital"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Digital Literacy Progress",
        "pestel_category": "Technological",
        "subcategory": "Innovation",
        "description": "Education tech, digital skills",
        "calculation_type": "frequency_count",
        "keywords": ["digital literacy", "digital skills", "ed-tech", "computer training"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Cybersecurity & Data (3)
    {
        "indicator_name": "Cyber Threat Level",
        "pestel_category": "Technological",
        "subcategory": "Cybersecurity",
        "description": "Hacking, data breach reports",
        "calculation_type": "frequency_count",
        "keywords": ["cyber attack", "hacking", "data breach", "malware", "ransomware"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Privacy Concerns",
        "pestel_category": "Technological",
        "subcategory": "Cybersecurity",
        "description": "Data protection discussions",
        "calculation_type": "frequency_count",
        "keywords": ["privacy", "data protection", "surveillance", "personal data"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Digital Rights Issues",
        "pestel_category": "Technological",
        "subcategory": "Cybersecurity",
        "description": "Internet censorship, access rights",
        "calculation_type": "frequency_count",
        "keywords": ["digital rights", "internet freedom", "censorship", "access"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Research & Development (2)
    {
        "indicator_name": "Innovation Output",
        "pestel_category": "Technological",
        "subcategory": "Research Development",
        "description": "Patents, research publications",
        "calculation_type": "frequency_count",
        "keywords": ["patent", "research", "innovation", "discovery", "R&D"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Tech Collaboration",
        "pestel_category": "Technological",
        "subcategory": "Research Development",
        "description": "International tech partnerships",
        "calculation_type": "frequency_count",
        "keywords": ["tech partnership", "collaboration", "joint research", "tech transfer"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # =====================================
    # ENVIRONMENTAL INDICATORS (~16)
    # =====================================
    
    # Weather & Climate (4)
    {
        "indicator_name": "Weather Severity Index",
        "pestel_category": "Environmental",
        "subcategory": "Weather Climate",
        "description": "Extreme temperature events, rainfall intensity",
        "calculation_type": "frequency_count",
        "keywords": ["extreme weather", "heat wave", "heavy rain", "storm", "temperature"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Flood Risk Level",
        "pestel_category": "Environmental",
        "subcategory": "Weather Climate",
        "description": "Flood warnings, affected areas count",
        "calculation_type": "frequency_count",
        "keywords": ["flood", "flooding", "overflow", "inundation", "water level"],
        "base_weight": 1.1,
        "threshold_high": 80.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Drought Concern Index",
        "pestel_category": "Environmental",
        "subcategory": "Weather Climate",
        "description": "Water shortage mentions, agricultural impact",
        "calculation_type": "frequency_count",
        "keywords": ["drought", "water shortage", "dry spell", "reservoir", "irrigation"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Storm Activity Indicator",
        "pestel_category": "Environmental",
        "subcategory": "Weather Climate",
        "description": "Cyclone, storm warnings",
        "calculation_type": "frequency_count",
        "keywords": ["cyclone", "storm", "monsoon", "wind", "hurricane"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    
    # Natural Disasters (3)
    {
        "indicator_name": "Disaster Frequency",
        "pestel_category": "Environmental",
        "subcategory": "Natural Disasters",
        "description": "Landslides, earthquakes, floods",
        "calculation_type": "frequency_count",
        "keywords": ["disaster", "landslide", "earthquake", "natural calamity"],
        "base_weight": 1.2,
        "threshold_high": 70.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Disaster Impact Severity",
        "pestel_category": "Environmental",
        "subcategory": "Natural Disasters",
        "description": "Casualties, displacement, economic damage",
        "calculation_type": "frequency_count",
        "keywords": ["casualties", "damage", "destruction", "loss", "victims"],
        "base_weight": 1.2,
        "threshold_high": 75.0,
        "threshold_low": 20.0
    },
    {
        "indicator_name": "Recovery Progress Index",
        "pestel_category": "Environmental",
        "subcategory": "Natural Disasters",
        "description": "Rehabilitation efforts",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["recovery", "rehabilitation", "reconstruction", "relief", "aid"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Environmental Quality (3)
    {
        "indicator_name": "Pollution Concern Level",
        "pestel_category": "Environmental",
        "subcategory": "Environmental Quality",
        "description": "Air quality, water contamination, waste issues",
        "calculation_type": "frequency_count",
        "keywords": ["pollution", "air quality", "contamination", "waste", "emissions"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
    {
        "indicator_name": "Deforestation Activity",
        "pestel_category": "Environmental",
        "subcategory": "Environmental Quality",
        "description": "Forest loss, illegal logging",
        "calculation_type": "frequency_count",
        "keywords": ["deforestation", "forest", "logging", "timber", "tree cutting"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Wildlife Conservation Status",
        "pestel_category": "Environmental",
        "subcategory": "Environmental Quality",
        "description": "Habitat loss, species threats",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["wildlife", "conservation", "endangered", "habitat", "biodiversity"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Agriculture & Land (3)
    {
        "indicator_name": "Crop Health Indicator",
        "pestel_category": "Environmental",
        "subcategory": "Agriculture Land",
        "description": "Harvest expectations, pest issues",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["crop", "harvest", "yield", "pest", "disease", "blight"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Agricultural Productivity",
        "pestel_category": "Environmental",
        "subcategory": "Agriculture Land",
        "description": "Yield reports, farming conditions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["agricultural", "productivity", "farming", "cultivation", "season"],
        "base_weight": 1.0,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Land Use Changes",
        "pestel_category": "Environmental",
        "subcategory": "Agriculture Land",
        "description": "Urban expansion, farmland conversion",
        "calculation_type": "frequency_count",
        "keywords": ["land use", "urban expansion", "farmland", "development", "rezoning"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Climate Action (3)
    {
        "indicator_name": "Sustainability Initiatives",
        "pestel_category": "Environmental",
        "subcategory": "Climate Action",
        "description": "Green projects, renewable energy",
        "calculation_type": "frequency_count",
        "keywords": ["sustainability", "renewable", "green energy", "solar", "wind power"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Climate Policy Activity",
        "pestel_category": "Environmental",
        "subcategory": "Climate Action",
        "description": "Environmental regulations",
        "calculation_type": "frequency_count",
        "keywords": ["climate policy", "environmental regulation", "carbon", "emission"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Carbon Reduction Efforts",
        "pestel_category": "Environmental",
        "subcategory": "Climate Action",
        "description": "Emissions reduction programs",
        "calculation_type": "frequency_count",
        "keywords": ["carbon reduction", "emissions", "net zero", "carbon footprint"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # =====================================
    # LEGAL INDICATORS (~15)
    # =====================================
    
    # Legislative Activity (4)
    {
        "indicator_name": "New Laws Frequency",
        "pestel_category": "Legal",
        "subcategory": "Legislative Activity",
        "description": "Bills passed, amendments",
        "calculation_type": "frequency_count",
        "keywords": ["law", "bill", "legislation", "parliament", "enacted"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Regulatory Changes Rate",
        "pestel_category": "Legal",
        "subcategory": "Legislative Activity",
        "description": "Rule modifications across sectors",
        "calculation_type": "frequency_count",
        "keywords": ["regulation", "regulatory", "rule change", "amendment", "gazette"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Court Decision Impact",
        "pestel_category": "Legal",
        "subcategory": "Legislative Activity",
        "description": "Major rulings affecting businesses",
        "calculation_type": "frequency_count",
        "keywords": ["court", "ruling", "judgment", "verdict", "supreme court"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Legal Reform Momentum",
        "pestel_category": "Legal",
        "subcategory": "Legislative Activity",
        "description": "Justice system improvements",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["legal reform", "justice", "judicial reform", "court reform"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    
    # Business Regulation (4)
    {
        "indicator_name": "Business Ease Index",
        "pestel_category": "Legal",
        "subcategory": "Business Regulation",
        "description": "Licensing changes, permit processes",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["business registration", "license", "permit", "ease of doing business"],
        "base_weight": 0.9,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Tax Policy Direction",
        "pestel_category": "Legal",
        "subcategory": "Business Regulation",
        "description": "Tax rate changes, new tax introductions",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["tax", "taxation", "VAT", "income tax", "corporate tax"],
        "base_weight": 1.0,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Labor Law Changes",
        "pestel_category": "Legal",
        "subcategory": "Business Regulation",
        "description": "Employment regulations",
        "calculation_type": "frequency_count",
        "keywords": ["labor law", "employment law", "worker rights", "EPF", "ETF"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Trade Regulations",
        "pestel_category": "Legal",
        "subcategory": "Business Regulation",
        "description": "Import/export rules",
        "calculation_type": "frequency_count",
        "keywords": ["trade regulation", "import rules", "export regulation", "customs"],
        "base_weight": 0.8,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Compliance & Enforcement (3)
    {
        "indicator_name": "Regulatory Strictness Index",
        "pestel_category": "Legal",
        "subcategory": "Compliance Enforcement",
        "description": "Enforcement action frequency",
        "calculation_type": "frequency_count",
        "keywords": ["enforcement", "crackdown", "inspection", "compliance check"],
        "base_weight": 0.9,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Penalty Severity Trend",
        "pestel_category": "Legal",
        "subcategory": "Compliance Enforcement",
        "description": "Fine amounts, sanctions",
        "calculation_type": "frequency_count",
        "keywords": ["fine", "penalty", "sanction", "punishment", "forfeiture"],
        "base_weight": 0.8,
        "threshold_high": 70.0,
        "threshold_low": 30.0
    },
    {
        "indicator_name": "Compliance Burden Score",
        "pestel_category": "Legal",
        "subcategory": "Compliance Enforcement",
        "description": "Reporting requirements",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["compliance", "reporting", "regulatory burden", "requirement"],
        "base_weight": 0.7,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Intellectual Property (2)
    {
        "indicator_name": "IP Protection Strength",
        "pestel_category": "Legal",
        "subcategory": "Intellectual Property",
        "description": "Patent, trademark enforcement",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["intellectual property", "patent", "trademark", "copyright", "IP"],
        "base_weight": 0.7,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "IP Dispute Frequency",
        "pestel_category": "Legal",
        "subcategory": "Intellectual Property",
        "description": "Infringement cases",
        "calculation_type": "frequency_count",
        "keywords": ["IP dispute", "infringement", "counterfeit", "piracy"],
        "base_weight": 0.7,
        "threshold_high": 65.0,
        "threshold_low": 35.0
    },
    
    # Contract & Commercial Law (2)
    {
        "indicator_name": "Contract Enforcement Quality",
        "pestel_category": "Legal",
        "subcategory": "Contract Law",
        "description": "Dispute resolution efficiency",
        "calculation_type": "sentiment_aggregate",
        "keywords": ["contract", "dispute resolution", "arbitration", "enforcement"],
        "base_weight": 0.8,
        "threshold_high": 60.0,
        "threshold_low": 35.0
    },
    {
        "indicator_name": "Bankruptcy Activity",
        "pestel_category": "Legal",
        "subcategory": "Contract Law",
        "description": "Insolvency filings",
        "calculation_type": "frequency_count",
        "keywords": ["bankruptcy", "insolvency", "liquidation", "winding up", "debt default"],
        "base_weight": 1.0,
        "threshold_high": 75.0,
        "threshold_low": 25.0
    },
]


def main():
    """Populate indicator definitions in PostgreSQL."""
    
    print("=" * 60)
    print("Populating Complete Indicator Hierarchy")
    print("=" * 60)
    
    conn = psycopg2.connect(
        host='localhost',
        port=15432,
        dbname='national_indicator',
        user='postgres',
        password='postgres_secure_2024'
    )
    
    cur = conn.cursor()
    
    # First, check current table structure
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='indicator_definitions'
        ORDER BY ordinal_position
    """)
    existing_columns = [r[0] for r in cur.fetchall()]
    print(f"\nExisting columns: {existing_columns}")
    
    # Check if we need to add subcategory column
    if 'subcategory' not in existing_columns:
        print("\nAdding subcategory column...")
        cur.execute("ALTER TABLE indicator_definitions ADD COLUMN IF NOT EXISTS subcategory VARCHAR(100)")
        conn.commit()
    
    # Check if we need to add keywords column (stored in extra_metadata)
    # We'll use the extra_metadata JSONB column for keywords
    
    # Clear existing indicators (optional - comment out to preserve)
    cur.execute("DELETE FROM indicator_definitions")
    print(f"\nCleared existing indicators")
    
    # Insert new indicators
    inserted = 0
    for ind in INDICATORS:
        try:
            # Generate a unique ID
            indicator_id = str(uuid.uuid4())[:8]
            
            # Prepare extra_metadata with keywords
            extra_metadata = {
                "keywords": ind.get("keywords", []),
                "subcategory": ind.get("subcategory", "")
            }
            
            cur.execute("""
                INSERT INTO indicator_definitions (
                    indicator_id,
                    indicator_name,
                    pestel_category,
                    subcategory,
                    description,
                    calculation_type,
                    base_weight,
                    threshold_high,
                    threshold_low,
                    is_active,
                    extra_metadata,
                    aggregation_window
                ) VALUES (%s, %s, %s::pestel_category_enum, %s, %s, %s::calculation_type_enum, %s, %s, %s, %s, %s, %s)
            """, (
                indicator_id,
                ind["indicator_name"],
                ind["pestel_category"],
                ind.get("subcategory", ""),
                ind.get("description", ""),
                ind["calculation_type"],
                ind.get("base_weight", 1.0),
                ind.get("threshold_high", 70.0),
                ind.get("threshold_low", 30.0),
                True,
                psycopg2.extras.Json(extra_metadata),
                "daily"
            ))
            inserted += 1
            
        except Exception as e:
            print(f"  Error inserting {ind['indicator_name']}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    
    # Report summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total indicators defined: {len(INDICATORS)}")
    print(f"Successfully inserted: {inserted}")
    
    # Count by category
    cur.execute("""
        SELECT pestel_category, COUNT(*) 
        FROM indicator_definitions 
        GROUP BY pestel_category 
        ORDER BY pestel_category
    """)
    print(f"\nIndicators by Category:")
    for cat, count in cur.fetchall():
        print(f"  {cat}: {count}")
    
    # Count by subcategory
    cur.execute("""
        SELECT pestel_category, subcategory, COUNT(*) 
        FROM indicator_definitions 
        WHERE subcategory IS NOT NULL AND subcategory != ''
        GROUP BY pestel_category, subcategory 
        ORDER BY pestel_category, subcategory
    """)
    results = cur.fetchall()
    
    if results:
        print(f"\nIndicators by Subcategory:")
        current_cat = None
        for cat, subcat, count in results:
            if cat != current_cat:
                print(f"  {cat}:")
                current_cat = cat
            print(f"    - {subcat}: {count}")
    
    cur.close()
    conn.close()
    
    print(f"\n{'=' * 60}")
    print("Indicator population complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
