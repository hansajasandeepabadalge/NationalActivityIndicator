"""
Feature Extractor for ML Classification

Extracts 61-dimensional feature vectors from articles to avoid overfitting.

Features (61 total):
- TF-IDF + PCA: 30 features (dimensionality reduction from 100)
- Keyword density: 10 features (one per indicator)
- Text statistics: 5 features
- Rule-based transfer: 10 features (transfer learning from Day 2)
- PESTEL category: 6 features (one-hot encoded)
"""

import re
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.keyword_config import INDICATOR_KEYWORDS


class FeatureExtractor:
    """Extract 61-dimensional feature vectors from articles"""

    def __init__(self):
        """Initialize feature extractor"""
        self.indicator_ids = [
            "POL_UNREST",
            "ECO_INFLATION",
            "ECO_CURRENCY",
            "ECO_CONSUMER_CONF",
            "ECO_SUPPLY_CHAIN",
            "ECO_TOURISM",
            "ENV_WEATHER",
            "OPS_TRANSPORT",
            "TEC_POWER",
            "SOC_HEALTHCARE"
        ]

        self.pestel_categories = [
            "Political",
            "Economic",
            "Social",
            "Technological",
            "Environmental",
            "Legal"
        ]

        # TF-IDF vectorizer (fit on training data)
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=100,  # Extract 100 features initially
            min_df=3,  # Term must appear in at least 3 documents
            max_df=0.7,  # Ignore terms that appear in >70% of docs
            ngram_range=(1, 1),  # Unigrams only (bigrams too sparse)
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )

        # PCA for dimensionality reduction (100 → 30, or fewer if small dataset)
        # Note: n_components will be adjusted based on n_samples during fit()
        self.pca = TruncatedSVD(
            n_components=30,  # Target, will be reduced if n_samples < 30
            random_state=42
        )
        self.actual_pca_components = 30  # Will be set during fit()

        # Rule-based classifier for transfer learning
        self.rule_classifier = RuleBasedClassifier()

        # Fitted flag
        self.is_fitted = False

    def fit(self, articles: List[Dict]) -> 'FeatureExtractor':
        """
        Fit TF-IDF vectorizer and PCA on training data.

        Args:
            articles: List of article dictionaries with 'content' and 'title'

        Returns:
            Self for chaining
        """
        print(f"Fitting feature extractor on {len(articles)} articles...")

        # Extract text for TF-IDF
        texts = []
        for article in articles:
            # Handle both dict and Pydantic models
            if hasattr(article, 'model_dump'):
                article = article.model_dump()

            text = f"{article.get('title', '')} {article.get('content', '')}"
            texts.append(text)

        # Fit TF-IDF
        print("  Fitting TF-IDF vectorizer (100 features)...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

        # Fit PCA (adjust n_components based on n_samples)
        n_samples = tfidf_matrix.shape[0]
        max_components = min(30, n_samples - 1, tfidf_matrix.shape[1])

        if max_components < 30:
            print(f"  ⚠️  Small dataset: Adjusting PCA from 30 → {max_components} components")
            self.pca = TruncatedSVD(n_components=max_components, random_state=42)

        print(f"  Fitting PCA (100 → {max_components} dimensions)...")
        self.pca.fit(tfidf_matrix.toarray())

        self.actual_pca_components = max_components

        explained_variance = self.pca.explained_variance_ratio_.sum()
        print(f"  PCA explained variance: {explained_variance:.2%}")

        self.is_fitted = True
        print("✓ Feature extractor fitted successfully")
        print(f"  Total features: {max_components} (PCA) + 10 (keyword) + 5 (text) + 10 (rule) + 6 (PESTEL) = {max_components + 31}")

        return self

    def transform(self, article: Dict) -> np.ndarray:
        """
        Extract 61-dimensional feature vector from a single article.

        Args:
            article: Article dictionary with 'title', 'content', 'category'

        Returns:
            61-dimensional numpy array
        """
        if not self.is_fitted:
            raise ValueError("FeatureExtractor must be fitted before transform. Call fit() first.")

        # Handle both dict and Pydantic models
        if hasattr(article, 'model_dump'):
            article = article.model_dump()

        features = []

        # 1. TF-IDF + PCA features (30 dimensions)
        tfidf_features = self._extract_tfidf_pca(article)
        features.extend(tfidf_features)

        # 2. Keyword density features (10 dimensions)
        keyword_features = self._extract_keyword_density(article)
        features.extend(keyword_features)

        # 3. Text statistics (5 dimensions)
        text_features = self._extract_text_statistics(article)
        features.extend(text_features)

        # 4. Rule-based transfer learning (10 dimensions)
        rule_features = self._extract_rule_based_features(article)
        features.extend(rule_features)

        # 5. PESTEL category (6 dimensions)
        pestel_features = self._extract_pestel_features(article)
        features.extend(pestel_features)

        # Total features is adaptive based on dataset size
        # With small datasets: actual_pca_components + 31 (other features)
        # With large datasets: 30 (PCA) + 31 = 61
        expected_total = self.actual_pca_components + 31

        if len(features) != expected_total:
            # This shouldn't happen, but safety check
            print(f"⚠️  Feature dimension mismatch: expected {expected_total}, got {len(features)}")

            # Pad or truncate to match
            while len(features) < expected_total:
                features.append(0.0)
            features = features[:expected_total]

        return np.array(features, dtype=np.float32)

    def transform_batch(self, articles: List[Dict]) -> np.ndarray:
        """
        Extract features for multiple articles.

        Args:
            articles: List of article dictionaries

        Returns:
            2D numpy array of shape (n_articles, 61)
        """
        feature_matrix = np.array([
            self.transform(article)
            for article in articles
        ])

        return feature_matrix

    def _extract_tfidf_pca(self, article: Dict) -> List[float]:
        """Extract TF-IDF + PCA features (30 dimensions)"""
        text = f"{article.get('title', '')} {article.get('content', '')}"

        # TF-IDF transformation
        tfidf_vector = self.tfidf_vectorizer.transform([text])

        # PCA dimensionality reduction
        pca_vector = self.pca.transform(tfidf_vector.toarray())[0]

        return pca_vector.tolist()

    def _extract_keyword_density(self, article: Dict) -> List[float]:
        """
        Extract keyword density features (10 dimensions).

        For each indicator, calculate:
        (count of high-weight keywords) / (total words)
        """
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words) if words else 1  # Avoid division by zero

        densities = []

        for indicator_id in self.indicator_ids:
            if indicator_id not in INDICATOR_KEYWORDS:
                densities.append(0.0)
                continue

            # Get high-weight keywords for this indicator
            high_weight_keywords = INDICATOR_KEYWORDS[indicator_id]['keywords'].get('high', [])

            # Count occurrences
            keyword_count = 0
            for keyword in high_weight_keywords:
                keyword_pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                keyword_count += len(re.findall(keyword_pattern, text))

            # Calculate density
            density = keyword_count / total_words
            densities.append(density)

        return densities

    def _extract_text_statistics(self, article: Dict) -> List[float]:
        """
        Extract text statistics (5 dimensions).

        Features:
        1. Word count
        2. Average word length
        3. Sentence count
        4. Title length
        5. Title/content overlap ratio
        """
        title = article.get('title', '')
        content = article.get('content', '')

        # 1. Word count
        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)

        # 2. Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

        # 3. Sentence count
        sentences = re.split(r'[.!?]+', content)
        sentence_count = len([s for s in sentences if s.strip()])

        # 4. Title length (in words)
        title_words = re.findall(r'\b\w+\b', title)
        title_length = len(title_words)

        # 5. Title/content overlap (how many title words appear in content)
        if title_words:
            content_lower = content.lower()
            overlap_count = sum(1 for word in title_words if word.lower() in content_lower)
            overlap_ratio = overlap_count / len(title_words)
        else:
            overlap_ratio = 0.0

        # Normalize features to reasonable ranges
        features = [
            min(word_count / 1000, 1.0),  # Normalize to 0-1 (assume max 1000 words)
            avg_word_length / 10,  # Normalize (avg word ~5 chars)
            min(sentence_count / 50, 1.0),  # Normalize (assume max 50 sentences)
            min(title_length / 20, 1.0),  # Normalize (assume max 20 words in title)
            overlap_ratio  # Already 0-1
        ]

        return features

    def _extract_rule_based_features(self, article: Dict) -> List[float]:
        """
        Extract rule-based confidence scores (10 dimensions).

        This is TRANSFER LEARNING - we use the proven Day 2 rule-based
        classifier's confidence scores as features for the ML model.
        """
        text = article.get('content', '')
        title = article.get('title', '')

        # Get rule-based classifications
        classifications = self.rule_classifier.classify_article(
            article_text=text,
            article_title=title
        )

        # Create confidence vector for all indicators
        confidence_dict = {
            cls['indicator_id']: cls['confidence']
            for cls in classifications
        }

        # Build feature vector (one confidence per indicator)
        features = [
            confidence_dict.get(indicator_id, 0.0)
            for indicator_id in self.indicator_ids
        ]

        return features

    def _extract_pestel_features(self, article: Dict) -> List[float]:
        """
        Extract PESTEL category one-hot encoding (6 dimensions).

        If category is unknown, all zeros.
        """
        category = article.get('category', '')

        # One-hot encoding
        features = [
            1.0 if category == pestel_cat else 0.0
            for pestel_cat in self.pestel_categories
        ]

        return features

    def get_feature_names(self) -> List[str]:
        """
        Get feature names for interpretability.

        Returns:
            List of feature names (adaptive based on dataset size)
        """
        names = []

        # TF-IDF + PCA (adaptive features)
        pca_dims = self.actual_pca_components if hasattr(self, 'actual_pca_components') else 30
        names.extend([f"tfidf_pca_{i}" for i in range(pca_dims)])

        # Keyword density (10 features)
        names.extend([f"keyword_density_{ind}" for ind in self.indicator_ids])

        # Text statistics (5 features)
        names.extend([
            "word_count_norm",
            "avg_word_length_norm",
            "sentence_count_norm",
            "title_length_norm",
            "title_content_overlap"
        ])

        # Rule-based transfer (10 features)
        names.extend([f"rule_confidence_{ind}" for ind in self.indicator_ids])

        # PESTEL category (6 features)
        names.extend([f"pestel_{cat.lower()}" for cat in self.pestel_categories])

        return names

    def save(self, path: str):
        """
        Save fitted feature extractor to disk.

        Args:
            path: Path to save (e.g., 'backend/models/ml_classifier/feature_extractor.pkl')
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted FeatureExtractor. Call fit() first.")

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the entire object
        joblib.dump(self, output_path)

        print(f"✓ Feature extractor saved to: {path}")

    @staticmethod
    def load(path: str) -> 'FeatureExtractor':
        """
        Load fitted feature extractor from disk.

        Args:
            path: Path to load from

        Returns:
            Loaded FeatureExtractor instance
        """
        extractor = joblib.load(path)

        if not extractor.is_fitted:
            raise ValueError("Loaded FeatureExtractor is not fitted")

        print(f"✓ Feature extractor loaded from: {path}")

        return extractor

    def print_feature_summary(self):
        """Print summary of feature extractor configuration"""
        pca_dims = self.actual_pca_components if hasattr(self, 'actual_pca_components') else 30
        total_features = pca_dims + 31

        print("\n" + "="*60)
        print("FEATURE EXTRACTOR SUMMARY")
        print("="*60)
        print(f"Total features: {total_features} (adaptive)")
        print(f"\nBreakdown:")
        print(f"  1. TF-IDF + PCA: {pca_dims} features (100 → {pca_dims} with PCA)")
        print(f"  2. Keyword density: 10 features (one per indicator)")
        print(f"  3. Text statistics: 5 features")
        print(f"  4. Rule-based transfer: 10 features (Day 2 knowledge)")
        print(f"  5. PESTEL category: 6 features (one-hot)")
        print(f"\nFitted: {self.is_fitted}")
        if self.is_fitted:
            variance = self.pca.explained_variance_ratio_.sum()
            print(f"PCA explained variance: {variance:.2%}")
        if pca_dims < 30:
            print(f"\n⚠️  Note: Using {pca_dims} PCA components (limited by n_samples)")
            print(f"   With larger dataset (100+ samples), will use 30 components")
        print("="*60 + "\n")
