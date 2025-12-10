"""
Optimized Feature Extractor for Small-Medium Datasets

Strategy for 200-500 training articles:
1. Feature Selection: Keep only top 40-50 most informative features
2. Remove redundant/correlated features
3. Add high-impact domain features
4. Use regularization to prevent overfitting

Expected improvement: F1 0.759 → 0.85-0.90 (with same 200 articles)
"""

import re
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import SelectKBest, chi2, mutual_info_classif

from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.keyword_config import INDICATOR_KEYWORDS


class OptimizedFeatureExtractor:
    """
    Optimized feature extractor with feature selection for small-medium datasets.
    
    Target: 40-50 features (down from 61) for better performance with 200 articles.
    """

    def __init__(self, n_features_target: int = 45):
        """
        Initialize optimized feature extractor.
        
        Args:
            n_features_target: Target number of features (default 45 for ~200 articles)
        """
        self.n_features_target = n_features_target
        
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

        # TF-IDF with better parameters for small datasets
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=50,  # Reduced from 100
            min_df=2,  # Reduced from 3 (less aggressive filtering)
            max_df=0.8,  # Keep high-frequency terms
            ngram_range=(1, 2),  # Add bigrams for better context
            stop_words='english',
            lowercase=True,
            strip_accents='unicode',
            sublinear_tf=True  # Use log scaling for better TF-IDF
        )

        # Smaller PCA for small datasets
        self.pca = TruncatedSVD(
            n_components=15,  # Reduced from 30
            random_state=42
        )
        self.actual_pca_components = 15

        # Feature selection for domain features
        self.feature_selector = None
        self.selected_feature_indices = None

        # Rule-based classifier for transfer learning
        self.rule_classifier = RuleBasedClassifier()

        # Fitted flag
        self.is_fitted = False

    def fit(self, articles: List[Dict], labels: Optional[np.ndarray] = None) -> 'OptimizedFeatureExtractor':
        """
        Fit feature extractor with automatic feature selection.

        Args:
            articles: List of article dictionaries
            labels: Optional label matrix (n_samples, 10) for supervised feature selection

        Returns:
            Self for chaining
        """
        print(f"Fitting optimized feature extractor on {len(articles)} articles...")

        # Extract text for TF-IDF
        texts = []
        for article in articles:
            if hasattr(article, 'model_dump'):
                article = article.model_dump()
            text = f"{article.get('title', '')} {article.get('content', '')}"
            texts.append(text)

        # Fit TF-IDF (reduced features)
        print("  Fitting TF-IDF vectorizer (50 features)...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

        # Fit PCA with adjusted components
        n_samples = tfidf_matrix.shape[0]
        max_components = min(15, n_samples - 1, tfidf_matrix.shape[1])

        if max_components < 15:
            print(f"  ⚠️  Small dataset: Adjusting PCA from 15 → {max_components} components")
            self.pca = TruncatedSVD(n_components=max_components, random_state=42)

        print(f"  Fitting PCA (50 → {max_components} dimensions)...")
        self.pca.fit(tfidf_matrix.toarray())
        self.actual_pca_components = max_components

        explained_variance = self.pca.explained_variance_ratio_.sum()
        print(f"  PCA explained variance: {explained_variance:.2%}")

        # Extract all features for feature selection
        print("  Extracting all features for selection...")
        all_features_matrix = []
        for article in articles:
            features = self._extract_all_features_raw(article)
            all_features_matrix.append(features)
        all_features_matrix = np.array(all_features_matrix)

        # Feature selection if labels provided
        if labels is not None:
            print("  Performing supervised feature selection...")
            self._select_best_features(all_features_matrix, labels)
        else:
            print("  ⚠️  No labels provided - using all features (no selection)")
            self.selected_feature_indices = None

        self.is_fitted = True
        
        final_features = self.n_features_target if self.selected_feature_indices is not None else all_features_matrix.shape[1]
        print(f"✓ Optimized feature extractor fitted successfully")
        print(f"  Final feature count: {final_features} (optimized for {n_samples} samples)")
        print(f"  Samples-per-feature ratio: {n_samples / final_features:.1f}:1 {'✅' if n_samples / final_features >= 4 else '⚠️'}")

        return self

    def _extract_all_features_raw(self, article: Dict) -> List[float]:
        """Extract all features before selection (internal method)"""
        if hasattr(article, 'model_dump'):
            article = article.model_dump()

        features = []

        # 1. TF-IDF + PCA (15 dimensions)
        features.extend(self._extract_tfidf_pca(article))

        # 2. High-impact domain features (12 dimensions) - NEW & OPTIMIZED
        features.extend(self._extract_domain_features_optimized(article))

        # 3. Keyword density - TOP 5 only (5 dimensions)
        features.extend(self._extract_keyword_density_top(article))

        # 4. Rule-based transfer - TOP 5 only (5 dimensions)
        features.extend(self._extract_rule_features_top(article))

        # 5. Essential text stats (4 dimensions)
        features.extend(self._extract_text_statistics_essential(article))

        # 6. Source quality (2 dimensions)
        features.extend(self._extract_source_quality(article))

        # Total: 15 + 12 + 5 + 5 + 4 + 2 = 43 features (base)
        return features

    def transform(self, article: Dict) -> np.ndarray:
        """
        Extract optimized feature vector from a single article.

        Args:
            article: Article dictionary

        Returns:
            Optimized feature vector (40-50 dimensions)
        """
        if not self.is_fitted:
            raise ValueError("OptimizedFeatureExtractor must be fitted before transform")

        # Extract all features
        all_features = self._extract_all_features_raw(article)

        # Apply feature selection if fitted
        if self.selected_feature_indices is not None:
            selected_features = [all_features[i] for i in self.selected_feature_indices]
            return np.array(selected_features, dtype=np.float32)
        else:
            return np.array(all_features, dtype=np.float32)

    def transform_batch(self, articles: List[Dict]) -> np.ndarray:
        """Extract features for multiple articles"""
        return np.array([self.transform(article) for article in articles])

    def _extract_tfidf_pca(self, article: Dict) -> List[float]:
        """Extract TF-IDF + PCA features (15 dimensions)"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        tfidf_vector = self.tfidf_vectorizer.transform([text])
        pca_vector = self.pca.transform(tfidf_vector.toarray())[0]
        return pca_vector.tolist()

    def _extract_domain_features_optimized(self, article: Dict) -> List[float]:
        """
        Extract HIGH-IMPACT domain-specific features (12 dimensions).
        
        These are the most discriminative features for Sri Lankan national indicators.
        """
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        title = article.get('title', '').lower()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words) if words else 1

        # 1. Economic crisis indicators (HIGHEST IMPACT)
        econ_crisis = ['inflation', 'price', 'expensive', 'cost', 'shortage', 'crisis']
        econ_score = sum(1 for kw in econ_crisis if kw in text) / len(econ_crisis)

        # 2. Political unrest indicators
        pol_unrest = ['protest', 'strike', 'demonstration', 'unrest', 'government']
        pol_score = sum(1 for kw in pol_unrest if kw in text) / len(pol_unrest)

        # 3. Currency/forex mentions
        currency_mentions = len(re.findall(r'\b(lkr|rupee|dollar|forex|exchange rate)\b', text))
        currency_score = min(currency_mentions / 2, 1.0)

        # 4. Urgency/crisis keywords in TITLE (very discriminative)
        urgent_in_title = sum(1 for kw in ['crisis', 'urgent', 'breaking', 'emergency'] if kw in title)
        urgency_score = min(urgent_in_title, 1.0)

        # 5. Numbers/statistics presence (important for economic indicators)
        numeric_tokens = re.findall(r'\d+(?:\.\d+)?', text)
        numeric_density = min(len(numeric_tokens) / word_count * 10, 1.0)

        # 6. Stakeholder mentions (workers, consumers, businesses)
        stakeholders = ['worker', 'employee', 'consumer', 'business', 'company', 'citizen']
        stakeholder_score = sum(1 for kw in stakeholders if kw in text) / len(stakeholders)

        # 7. Action verbs (increase, decrease, announce, close)
        actions = ['increase', 'decrease', 'rise', 'fall', 'announce', 'close', 'shut']
        action_score = sum(1 for verb in actions if verb in text) / len(actions)

        # 8. Geographic specificity (Sri Lanka context)
        geo_terms = ['sri lanka', 'colombo', 'national', 'country']
        geo_score = sum(1 for term in geo_terms if term in text) / len(geo_terms)

        # 9. Supply chain keywords
        supply_chain = ['shortage', 'stock', 'supply', 'import', 'delay', 'disruption']
        supply_score = sum(1 for kw in supply_chain if kw in text) / len(supply_chain)

        # 10. Sentiment keywords (positive vs negative)
        negative_keywords = ['concern', 'worry', 'fear', 'crisis', 'problem', 'issue']
        negative_score = sum(1 for kw in negative_keywords if kw in text) / len(negative_keywords)

        # 11. Time urgency (today, now, immediate)
        time_urgent = ['today', 'now', 'immediate', 'ongoing', 'current']
        time_score = sum(1 for kw in time_urgent if kw in text) / len(time_urgent)

        # 12. Article length (normalized)
        length_score = min(word_count / 500, 1.0)  # Normalize to 500 words max

        return [
            econ_score,
            pol_score,
            currency_score,
            urgency_score,
            numeric_density,
            stakeholder_score,
            action_score,
            geo_score,
            supply_score,
            negative_score,
            time_score,
            length_score
        ]

    def _extract_keyword_density_top(self, article: Dict) -> List[float]:
        """
        Extract keyword density for TOP 5 most important indicators (5 dimensions).
        
        Focus on indicators with clearest keyword signals.
        """
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words) if words else 1

        # Top 5 indicators with best keyword discrimination
        top_indicators = [
            "POL_UNREST",      # Clear keywords (protest, strike)
            "ECO_INFLATION",   # Clear keywords (inflation, price)
            "ECO_CURRENCY",    # Clear keywords (LKR, forex)
            "ECO_SUPPLY_CHAIN", # Clear keywords (shortage, supply)
            "OPS_TRANSPORT"    # Clear keywords (transport, traffic)
        ]

        densities = []
        for indicator_id in top_indicators:
            if indicator_id not in INDICATOR_KEYWORDS:
                densities.append(0.0)
                continue

            keywords = INDICATOR_KEYWORDS[indicator_id]['keywords'].get('high', [])
            keyword_count = sum(
                len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text))
                for kw in keywords
            )
            density = keyword_count / total_words
            densities.append(density)

        return densities

    def _extract_rule_features_top(self, article: Dict) -> List[float]:
        """
        Extract rule-based confidence for TOP 5 indicators (5 dimensions).
        
        Transfer learning from proven rule-based system.
        """
        text = article.get('content', '')
        title = article.get('title', '')

        classifications = self.rule_classifier.classify_article(
            article_text=text,
            article_title=title
        )

        confidence_dict = {
            cls['indicator_id']: cls['confidence']
            for cls in classifications
        }

        # Same top 5 indicators
        top_indicators = [
            "POL_UNREST",
            "ECO_INFLATION",
            "ECO_CURRENCY",
            "ECO_SUPPLY_CHAIN",
            "OPS_TRANSPORT"
        ]

        return [confidence_dict.get(ind, 0.0) for ind in top_indicators]

    def _extract_text_statistics_essential(self, article: Dict) -> List[float]:
        """
        Extract ESSENTIAL text statistics (4 dimensions).
        
        Keep only most discriminative stats.
        """
        title = article.get('title', '')
        content = article.get('content', '')

        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)

        # 1. Word count (normalized)
        word_count_norm = min(word_count / 1000, 1.0)

        # 2. Title length (important for news vs. opinion)
        title_words = len(re.findall(r'\b\w+\b', title))
        title_length_norm = min(title_words / 15, 1.0)

        # 3. Title-content overlap (important for relevance)
        title_words_set = set(re.findall(r'\b\w+\b', title.lower()))
        content_lower = content.lower()
        overlap = sum(1 for word in title_words_set if word in content_lower)
        overlap_ratio = overlap / len(title_words_set) if title_words_set else 0.0

        # 4. Average word length (complexity indicator)
        avg_word_len = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        avg_word_len_norm = avg_word_len / 10

        return [
            word_count_norm,
            title_length_norm,
            overlap_ratio,
            avg_word_len_norm
        ]

    def _extract_source_quality(self, article: Dict) -> List[float]:
        """
        Extract source quality features (2 dimensions).
        
        Critical for weighting predictions.
        """
        metadata = article.get('metadata', {})
        
        # Source credibility (from metadata)
        credibility = metadata.get('source_credibility', 0.5)
        
        # Is mainstream source (credibility >= 0.8)
        is_mainstream = 1.0 if credibility >= 0.8 else 0.0

        return [credibility, is_mainstream]

    def _select_best_features(self, X: np.ndarray, y: np.ndarray):
        """
        Select best features using mutual information.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Label matrix (n_samples, n_indicators)
        """
        # For multi-label, select features based on average MI across all indicators
        print(f"    Selecting top {self.n_features_target} features from {X.shape[1]}...")
        
        # Calculate MI for each indicator, then average
        mi_scores = np.zeros(X.shape[1])
        
        for i in range(y.shape[1]):
            mi = mutual_info_classif(X, y[:, i], random_state=42)
            mi_scores += mi
        
        mi_scores /= y.shape[1]  # Average MI across indicators
        
        # Select top features
        top_indices = np.argsort(mi_scores)[-self.n_features_target:]
        top_indices = sorted(top_indices)  # Maintain order
        
        self.selected_feature_indices = top_indices
        
        print(f"    ✓ Selected {len(top_indices)} features")
        print(f"    Top features have MI scores: {mi_scores[top_indices][:5].round(3)} ... {mi_scores[top_indices][-5:].round(3)}")

    def get_feature_names(self) -> List[str]:
        """Get feature names for interpretability"""
        names = []

        # TF-IDF + PCA
        names.extend([f"tfidf_pca_{i}" for i in range(self.actual_pca_components)])

        # Domain features
        names.extend([
            "domain_economic_crisis",
            "domain_political_unrest",
            "domain_currency_mentions",
            "domain_urgency_in_title",
            "domain_numeric_density",
            "domain_stakeholders",
            "domain_action_verbs",
            "domain_geographic",
            "domain_supply_chain",
            "domain_negative_sentiment",
            "domain_time_urgency",
            "domain_article_length"
        ])

        # Top 5 keyword densities
        top_indicators = ["POL_UNREST", "ECO_INFLATION", "ECO_CURRENCY", "ECO_SUPPLY_CHAIN", "OPS_TRANSPORT"]
        names.extend([f"keyword_density_{ind}" for ind in top_indicators])

        # Top 5 rule confidences
        names.extend([f"rule_confidence_{ind}" for ind in top_indicators])

        # Essential text stats
        names.extend([
            "text_word_count",
            "text_title_length",
            "text_title_overlap",
            "text_avg_word_length"
        ])

        # Source quality
        names.extend([
            "source_credibility",
            "source_is_mainstream"
        ])

        # Apply feature selection if done
        if self.selected_feature_indices is not None:
            selected_names = [names[i] for i in self.selected_feature_indices]
            return selected_names

        return names

    def save(self, path: str):
        """Save fitted feature extractor"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted OptimizedFeatureExtractor")

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, output_path)
        print(f"✓ Optimized feature extractor saved to: {path}")

    @staticmethod
    def load(path: str) -> 'OptimizedFeatureExtractor':
        """Load fitted feature extractor"""
        extractor = joblib.load(path)
        if not extractor.is_fitted:
            raise ValueError("Loaded OptimizedFeatureExtractor is not fitted")
        print(f"✓ Optimized feature extractor loaded from: {path}")
        return extractor

    def print_feature_summary(self):
        """Print summary of optimized feature configuration"""
        actual_features = self.n_features_target if self.selected_feature_indices is not None else 43
        
        print("\n" + "="*60)
        print("OPTIMIZED FEATURE EXTRACTOR SUMMARY")
        print("="*60)
        print(f"Target features: {self.n_features_target}")
        print(f"Actual features: {actual_features}")
        print(f"\nOptimizations:")
        print(f"  ✅ Reduced TF-IDF: 100 → 50 features")
        print(f"  ✅ Reduced PCA: 30 → 15 components")
        print(f"  ✅ Added 12 high-impact domain features")
        print(f"  ✅ Keyword density: Top 5 indicators only")
        print(f"  ✅ Rule transfer: Top 5 indicators only")
        print(f"  ✅ Text stats: Essential 4 only")
        print(f"  ✅ Feature selection: {'Enabled' if self.selected_feature_indices else 'Disabled'}")
        print(f"\nExpected improvement with 200 articles:")
        print(f"  Before: F1 ~0.76 (61 features)")
        print(f"  After:  F1 ~0.85-0.90 ({actual_features} optimized features)")
        print("="*60 + "\n")
