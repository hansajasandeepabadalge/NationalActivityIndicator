#!/usr/bin/env python3
"""
Generate 200+ mock articles for Layer 2 testing
Covers all PESTEL categories with realistic Sri Lankan context
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Article templates by PESTEL category
POLITICAL_TOPICS = [
    ("Parliament debates new electoral reforms bill", "The parliament convened today to discuss proposed reforms to the electoral system, with opposition parties raising concerns about implementation timelines."),
    ("Government announces cabinet reshuffle", "The President announced a major cabinet reshuffle affecting six ministries, citing the need for fresh perspectives in key portfolios."),
    ("Opposition calls for no-confidence motion", "Opposition parties have submitted a no-confidence motion against the Minister of Finance, criticizing recent economic policies."),
    ("New diplomatic ties established with neighboring countries", "Sri Lanka signed bilateral agreements with three regional partners, focusing on trade and security cooperation."),
    ("Provincial council elections postponed", "The Election Commission announced a delay in provincial council elections due to pending legal challenges."),
    ("Anti-corruption commission launches probe", "The Commission to Investigate Allegations of Bribery or Corruption initiated investigations into several high-profile cases."),
    ("Parliament passes constitutional amendment", "A landmark constitutional amendment was passed with a two-thirds majority, strengthening parliamentary oversight."),
    ("Political parties form coalition for upcoming elections", "Five political parties announced a coalition agreement ahead of general elections scheduled for next year."),
    ("Government approves decentralization policy", "Cabinet approved a new policy framework for fiscal decentralization to provincial administrations."),
    ("Supreme Court rules on executive powers", "The Supreme Court delivered a judgment clarifying the limits of executive authority in provincial governance."),
]

ECONOMIC_TOPICS = [
    ("Central Bank maintains interest rates", "The Monetary Board decided to keep policy rates unchanged at 9.5%, citing stable inflation expectations."),
    ("Tourism revenue exceeds pre-pandemic levels", "The tourism sector reported record earnings this quarter, surpassing 2019 figures for the first time since the pandemic."),
    ("Stock market reaches 12-month high", "The Colombo Stock Exchange All Share Price Index closed at a 12-month peak, driven by banking sector gains."),
    ("Foreign reserves increase by $500 million", "The Central Bank reported gross official reserves rose to $4.2 billion, reflecting improved external position."),
    ("Government unveils tax reform package", "The Finance Ministry announced comprehensive tax reforms aimed at broadening the revenue base and reducing compliance costs."),
    ("Export earnings grow 15% year-on-year", "Merchandise exports reached $1.8 billion last month, with strong performance in textiles and IT services."),
    ("Inflation rate drops to single digits", "Consumer price inflation moderated to 8.9% in the latest reading, down from double digits earlier this year."),
    ("Credit rating agency upgrades outlook", "International rating agency Moody's revised Sri Lanka's outlook from negative to stable, citing fiscal consolidation."),
    ("FDI inflows surge in manufacturing sector", "Foreign direct investment in manufacturing increased by 45% in the first quarter, led by electronics assembly."),
    ("Colombo Port handles record container volumes", "The Port of Colombo processed 1.8 million TEUs last quarter, marking a 12% increase from the previous year."),
]

SOCIAL_TOPICS = [
    ("Healthcare spending increases by 20%", "The government allocated an additional 50 billion rupees to the healthcare sector in the supplementary budget."),
    ("New education policy emphasizes STEM", "The Ministry of Education unveiled a curriculum reform prioritizing science, technology, engineering, and mathematics."),
    ("Unemployment rate falls to 4.8%", "The Department of Census and Statistics reported the unemployment rate declined for the third consecutive quarter."),
    ("Housing development project launched", "A public-private partnership will deliver 50,000 affordable housing units over the next three years."),
    ("Poverty alleviation program expanded", "The Samurdhi welfare program coverage was extended to an additional 200,000 families in rural areas."),
    ("Youth skills training initiative announced", "A national skills development program will train 100,000 youth in digital and vocational skills."),
    ("Public health campaign targets malnutrition", "The Ministry of Health launched a comprehensive nutrition intervention targeting children under five."),
    ("Gender equality index shows improvement", "Sri Lanka moved up five places in the global gender gap index, driven by educational parity gains."),
    ("Rural connectivity project connects 500 villages", "A telecommunications infrastructure project brought 4G coverage to remote communities."),
    ("Social security net strengthened", "The government expanded pension coverage to include informal sector workers in a phased rollout."),
]

TECHNOLOGICAL_TOPICS = [
    ("National AI strategy released", "The government unveiled a comprehensive artificial intelligence roadmap targeting healthcare, agriculture, and public services."),
    ("5G network rollout begins in Colombo", "Major telecommunications providers commenced 5G services in the capital with plans for nationwide coverage."),
    ("Cybersecurity law enacted", "Parliament passed the Cybersecurity Act providing a legal framework for protecting critical information infrastructure."),
    ("Digital payment adoption reaches 60%", "Mobile payment transactions grew 85% year-on-year as cashless adoption accelerated across demographics."),
    ("Tech startup ecosystem attracts $100M investment", "Venture capital funding into Sri Lankan startups reached a record high, focusing on fintech and edtech."),
    ("Smart city pilot launched in Kandy", "An IoT-enabled urban management system was deployed covering traffic, waste, and energy management."),
    ("E-government services expanded", "Citizens can now access 150 government services online through a unified digital platform."),
    ("Research institute develops local AI model", "Scientists at a national research center created a Sinhala and Tamil language processing model."),
    ("Blockchain pilot for land registry", "The Land Registry Department initiated a blockchain-based property registration system in select districts."),
    ("National broadband policy targets 95% coverage", "A policy framework aims to provide high-speed internet access to 95% of households by 2026."),
]

ENVIRONMENTAL_TOPICS = [
    ("Renewable energy capacity reaches 45%", "Sri Lanka achieved a milestone with 45% of electricity generation from renewable sources, mainly hydro and solar."),
    ("Marine conservation zone expanded", "The government designated an additional 15,000 square kilometers as a marine protected area."),
    ("Plastic ban extended to single-use products", "Environmental regulations now prohibit 15 categories of single-use plastics nationwide."),
    ("Climate adaptation fund receives $200M", "International climate finance commitments will support coastal resilience and agriculture adaptation projects."),
    ("Deforestation rate drops by 30%", "Satellite monitoring showed forest cover increased due to reforestation initiatives and enforcement."),
    ("Electric vehicle adoption exceeds targets", "Electric vehicle registrations surpassed 50,000, ahead of government projections for the year."),
    ("Water management project completed", "A comprehensive watershed restoration program improved water security for 500,000 people."),
    ("Carbon neutrality roadmap announced", "The government committed to achieving carbon neutrality by 2050 with interim targets for 2030."),
    ("Wildlife corridor protection law passed", "New legislation protects 12 critical wildlife corridors connecting national parks and reserves."),
    ("Air quality monitoring network expanded", "Real-time air quality sensors were installed in 25 cities to track pollution levels."),
]

LEGAL_TOPICS = [
    ("Right to Information Act strengthened", "Amendments to the RTI Act reduced response times and penalties for non-compliance by public officials."),
    ("New data protection law enacted", "Parliament passed comprehensive data privacy legislation aligned with international standards."),
    ("Judicial system digitization accelerated", "Courts rolled out e-filing and virtual hearing capabilities in 15 districts."),
    ("Competition law amended", "The Competition Commission received enhanced powers to investigate anti-competitive practices."),
    ("Labor law reforms approved", "Amendments to labor legislation introduced flexible work arrangements and strengthened worker protections."),
    ("Intellectual property regime updated", "Patent and trademark laws were harmonized with international treaties to support innovation."),
    ("Environmental compliance penalties increased", "New regulations imposed stricter fines for environmental violations by industrial facilities."),
    ("Consumer protection bureau established", "A dedicated authority was created to address consumer complaints and enforce fair trading practices."),
    ("Anti-money laundering framework strengthened", "The Financial Intelligence Unit received additional resources and powers to combat financial crimes."),
    ("Legal aid program expanded", "Free legal services were extended to cover civil matters in addition to criminal defense."),
]

def generate_article(category, topic, summary, article_id, date):
    """Generate a complete article structure"""

    # Generate realistic content based on summary
    content_variations = [
        f"{summary} Industry experts believe this development will have significant implications for the sector. Stakeholders are closely monitoring the situation as implementation details emerge. The announcement comes amid broader efforts to address systemic challenges. Officials indicated that consultations with affected parties would continue. Further details are expected to be released in the coming weeks.",

        f"{summary} According to official statements, this represents a major policy shift. The decision follows extensive consultations with stakeholders and technical experts. Implementation will be phased over the next 12-18 months. Independent analysts have welcomed the move, noting its potential long-term benefits. Critics, however, raised concerns about execution capacity. A monitoring committee will oversee progress.",

        f"{summary} The initiative aligns with broader national development objectives outlined in recent planning documents. Funding arrangements have been secured through a combination of domestic resources and international partnerships. Key performance indicators will track impact and outcomes. Regional variations in implementation are expected. Public feedback mechanisms have been established. Preliminary results will be reviewed in six months.",

        f"{summary} Observers note this development reflects evolving priorities in national policy. The announcement triggered varied reactions from different interest groups. Technical feasibility studies underpinned the decision-making process. Capacity building programs will support successful rollout. International best practices informed the design. Lessons learned from pilot projects were incorporated. Accountability frameworks ensure transparency.",
    ]

    content = random.choice(content_variations)

    # Generate metadata
    sources = ["Daily News", "The Island", "Colombo Gazette", "Newsfirst", "Ada Derana", "Hiru News"]
    authors = ["Staff Reporter", "News Desk", "Special Correspondent", "Political Editor", "Economic Bureau", "Field Reporter"]

    article = {
        "article_id": article_id,
        "title": topic,
        "content": content,
        "summary": summary,
        "category": category,
        "source": random.choice(sources),
        "author": random.choice(authors),
        "published_at": date.isoformat(),
        "language": "en",
        "url": f"https://example.com/articles/{article_id}",
        "metadata": {
            "word_count": len(content.split()),
            "reading_time_minutes": max(1, len(content.split()) // 200),
            "has_images": random.choice([True, False]),
            "view_count": random.randint(100, 10000)
        }
    }

    return article

def generate_mock_dataset(num_articles=220):
    """Generate complete mock dataset"""

    articles = []
    article_id_counter = 1

    # Calculate articles per category (roughly equal distribution)
    categories = {
        "Political": POLITICAL_TOPICS * 4,  # 40 articles
        "Economic": ECONOMIC_TOPICS * 4,    # 40 articles
        "Social": SOCIAL_TOPICS * 4,        # 40 articles
        "Technological": TECHNOLOGICAL_TOPICS * 4,  # 40 articles
        "Environmental": ENVIRONMENTAL_TOPICS * 4,  # 40 articles
        "Legal": LEGAL_TOPICS * 4,          # 40 articles
    }

    # Generate articles with dates spread over last 30 days
    start_date = datetime.now() - timedelta(days=30)

    for category, topics in categories.items():
        for i, (topic, summary) in enumerate(topics[:40]):  # Limit to 40 per category
            # Spread articles across 30 days
            days_offset = (i * 30) // 40
            article_date = start_date + timedelta(days=days_offset, hours=random.randint(0, 23))

            article_id = f"ART{article_id_counter:06d}"
            article = generate_article(category, topic, summary, article_id, article_date)
            articles.append(article)
            article_id_counter += 1

    return articles

def main():
    """Generate and save mock data"""
    print("Generating mock articles...")
    articles = generate_mock_dataset(220)

    # Sort by date
    articles.sort(key=lambda x: x['published_at'])

    # Save to JSON file
    output_dir = Path(__file__).parent.parent / "data" / "mock"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "mock_articles.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "total_articles": len(articles),
                "generation_date": datetime.now().isoformat(),
                "date_range": {
                    "start": articles[0]['published_at'],
                    "end": articles[-1]['published_at']
                },
                "categories": {
                    "Political": sum(1 for a in articles if a['category'] == 'Political'),
                    "Economic": sum(1 for a in articles if a['category'] == 'Economic'),
                    "Social": sum(1 for a in articles if a['category'] == 'Social'),
                    "Technological": sum(1 for a in articles if a['category'] == 'Technological'),
                    "Environmental": sum(1 for a in articles if a['category'] == 'Environmental'),
                    "Legal": sum(1 for a in articles if a['category'] == 'Legal'),
                }
            },
            "articles": articles
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated {len(articles)} mock articles")
    print(f"📁 Saved to: {output_file}")
    print(f"\nCategory breakdown:")
    for category in ["Political", "Economic", "Social", "Technological", "Environmental", "Legal"]:
        count = sum(1 for a in articles if a['category'] == category)
        print(f"  {category:20} {count:3} articles")

    return output_file

if __name__ == "__main__":
    main()
