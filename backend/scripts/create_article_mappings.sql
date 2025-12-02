-- Create article_indicator_mappings table
-- Maps articles to indicators with confidence scores from classification

CREATE TABLE IF NOT EXISTS article_indicator_mappings (
    mapping_id SERIAL PRIMARY KEY,
    article_id VARCHAR(100) NOT NULL,
    indicator_id VARCHAR(50) NOT NULL,
    match_confidence FLOAT NOT NULL,
    classification_method VARCHAR(50) DEFAULT 'rule_based',
    matched_keywords TEXT[],
    keyword_match_count INTEGER DEFAULT 0,
    article_category VARCHAR(50),
    article_published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    extra_metadata JSONB,
    FOREIGN KEY (indicator_id) REFERENCES indicator_definitions(indicator_id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_article_mappings_article ON article_indicator_mappings(article_id);
CREATE INDEX IF NOT EXISTS idx_article_mappings_indicator ON article_indicator_mappings(indicator_id);
CREATE INDEX IF NOT EXISTS idx_article_mappings_confidence ON article_indicator_mappings(match_confidence);
CREATE INDEX IF NOT EXISTS idx_article_mappings_method ON article_indicator_mappings(classification_method);
