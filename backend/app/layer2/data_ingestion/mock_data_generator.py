import json
import random
from datetime import datetime, timedelta
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "../../../mock_data")
CATEGORIES = ["political", "economic", "social", "environmental", "mixed"]

def generate_mock_articles():
    """Generate mock articles for all categories"""
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate for each category
    generate_political_articles(50)
    generate_economic_articles(50)
    generate_social_articles(50)
    generate_environmental_articles(30)
    generate_mixed_articles(20)
    
    print(f"✅ Mock data generated in {os.path.abspath(OUTPUT_DIR)}")

def generate_political_articles(count):
    articles = []
    keywords = ["protest", "strike", "demonstration", "cabinet", "election", "parliament", "unrest"]
    
    for i in range(count):
        article = create_base_article(f"pol_{i:03d}", "political")
        article["content"]["title"] = f"Political Update: {random.choice(keywords).title()} reported in Colombo"
        article["content"]["body"] = f"Reports of {random.choice(keywords)} intensifying. Government responds with new measures. Public sentiment remains tense."
        article["initial_classification"]["keywords"] = [random.choice(keywords) for _ in range(3)]
        articles.append(article)
        
    save_articles(articles, "articles_political.json")

def generate_economic_articles(count):
    articles = []
    keywords = ["inflation", "currency", "LKR", "imf", "tax", "price", "market"]
    
    for i in range(count):
        article = create_base_article(f"econ_{i:03d}", "economic")
        article["content"]["title"] = f"Economic Outlook: {random.choice(keywords).title()} trends concern experts"
        article["content"]["body"] = f"The {random.choice(keywords)} situation is fluctuating. Central Bank issues new guidelines. Market reacts cautiously."
        article["initial_classification"]["keywords"] = [random.choice(keywords) for _ in range(3)]
        articles.append(article)
        
    save_articles(articles, "articles_economic.json")

def generate_social_articles(count):
    articles = []
    keywords = ["health", "education", "poverty", "cost of living", "transport", "community"]
    
    for i in range(count):
        article = create_base_article(f"soc_{i:03d}", "social")
        article["content"]["title"] = f"Social Issue: {random.choice(keywords).title()} impacts daily life"
        article["content"]["body"] = f"Citizens express concern over {random.choice(keywords)}. Authorities promise action. Local communities organize support."
        article["initial_classification"]["keywords"] = [random.choice(keywords) for _ in range(3)]
        articles.append(article)
        
    save_articles(articles, "articles_social.json")

def generate_environmental_articles(count):
    articles = []
    keywords = ["rain", "flood", "drought", "weather", "landslide", "pollution"]
    
    for i in range(count):
        article = create_base_article(f"env_{i:03d}", "environmental")
        article["content"]["title"] = f"Weather Alert: {random.choice(keywords).title()} warning issued"
        article["content"]["body"] = f"Heavy {random.choice(keywords)} expected in coming days. Disaster Management Center advises caution."
        article["initial_classification"]["keywords"] = [random.choice(keywords) for _ in range(3)]
        articles.append(article)
        
    save_articles(articles, "articles_environmental.json")

def generate_mixed_articles(count):
    articles = []
    for i in range(count):
        article = create_base_article(f"mix_{i:03d}", "mixed")
        article["content"]["title"] = "Weekly Round-up: Multiple sectors affected"
        article["content"]["body"] = "A mix of political and economic events defined the week. Weather patterns also contributed to disruptions."
        article["initial_classification"]["keywords"] = ["protest", "inflation", "rain"]
        articles.append(article)
        
    save_articles(articles, "articles_mixed.json")

def create_base_article(article_id, category):
    """Create a standard article structure"""
    return {
        "article_id": article_id,
        "content": {
            "title": "Placeholder Title",
            "body": "Placeholder Body",
            "summary": "Placeholder Summary"
        },
        "metadata": {
            "source": random.choice(["Daily Mirror", "The Island", "NewsFirst", "Ada Derana"]),
            "source_credibility": round(random.uniform(0.7, 0.95), 2),
            "publish_timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "language_original": "en"
        },
        "initial_classification": {
            "keywords": [],
            "detected_language": "en"
        },
        "quality": {
            "credibility_score": round(random.uniform(0.7, 0.95), 2),
            "word_count": random.randint(100, 500),
            "is_duplicate": False
        }
    }

def save_articles(articles, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(articles, f, indent=2)
    print(f"Saved {len(articles)} articles to {filename}")

if __name__ == "__main__":
    generate_mock_articles()
