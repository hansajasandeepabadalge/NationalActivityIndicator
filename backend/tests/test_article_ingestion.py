"""Unit tests for article ingestion"""

from app.layer2.data_ingestion.article_loader import ArticleLoader


def test_article_loading():
    """Test loading articles from mock data"""
    loader = ArticleLoader()
    articles = loader.load_articles(limit=10)

    assert len(articles) == 10
    assert all(a.article_id for a in articles)
    assert all(a.category in ['Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal'] for a in articles)
    print(f"✅ Successfully loaded {len(articles)} articles")


def test_preprocessing():
    """Test article preprocessing"""
    loader = ArticleLoader()
    processed = loader.load_and_preprocess(limit=5)

    assert len(processed) == 5
    assert all(p.cleaned_content for p in processed)
    assert all(p.word_count > 0 for p in processed)
    print(f"✅ Successfully preprocessed {len(processed)} articles")


def test_full_load():
    """Test loading all articles"""
    loader = ArticleLoader()
    all_articles = loader.load_articles()

    print(f"✅ Total articles in mock data: {len(all_articles)}")
    assert len(all_articles) > 200, "Expected at least 200 articles"


if __name__ == "__main__":
    print("Running article ingestion tests...\n")
    test_article_loading()
    test_preprocessing()
    test_full_load()
    print("\n✅ All article ingestion tests passed!")
