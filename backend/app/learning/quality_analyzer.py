"""
Quality Analyzer for Layer 1 Adaptive Learning System.

Identifies recurring quality issues, analyzes patterns in validation failures,
and suggests targeted improvements for data quality.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict
import json
import re

logger = logging.getLogger(__name__)


class QualityIssueType(Enum):
    """Types of quality issues detected."""
    MISSING_FIELD = "missing_field"
    INVALID_FORMAT = "invalid_format"
    DUPLICATE_CONTENT = "duplicate_content"
    LOW_CREDIBILITY = "low_credibility"
    STALE_CONTENT = "stale_content"
    LANGUAGE_MISMATCH = "language_mismatch"
    CONTENT_TOO_SHORT = "content_too_short"
    CONTENT_TOO_LONG = "content_too_long"
    SPAM_DETECTED = "spam_detected"
    INCONSISTENT_DATA = "inconsistent_data"
    BROKEN_LINKS = "broken_links"
    ENCODING_ERROR = "encoding_error"
    RATE_LIMITED = "rate_limited"
    PARSING_FAILURE = "parsing_failure"


class IssueSeverity(Enum):
    """Severity levels for quality issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    """A detected quality issue."""
    issue_type: QualityIssueType
    severity: IssueSeverity
    source_id: Optional[str]
    article_id: Optional[str]
    field_name: Optional[str]
    description: str
    raw_value: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "source_id": self.source_id,
            "article_id": self.article_id,
            "field_name": self.field_name,
            "description": self.description,
            "raw_value": self.raw_value[:100] if self.raw_value else None,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved
        }


@dataclass
class IssuePattern:
    """A recurring pattern of quality issues."""
    pattern_id: str
    issue_types: Set[QualityIssueType]
    affected_sources: Set[str]
    affected_fields: Set[str]
    occurrence_count: int
    first_seen: datetime
    last_seen: datetime
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    priority_score: float = 0.0


@dataclass
class QualityReport:
    """Summary report of quality analysis."""
    period_start: datetime
    period_end: datetime
    total_articles_analyzed: int
    total_issues_found: int
    issues_by_type: Dict[str, int]
    issues_by_severity: Dict[str, int]
    issues_by_source: Dict[str, int]
    top_patterns: List[IssuePattern]
    overall_quality_score: float  # 0.0 to 1.0
    trend: str  # "improving", "stable", "degrading"
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationRule:
    """A validation rule with learned thresholds."""
    rule_id: str
    field_name: str
    rule_type: str  # "required", "format", "range", "length", "pattern"
    threshold: Any
    learned_from_data: bool = False
    effectiveness: float = 1.0  # How well this rule catches real issues
    false_positive_rate: float = 0.0


class QualityAnalyzer:
    """
    Analyzes quality patterns in Layer 1 data.
    
    Features:
    - Detects recurring quality issues
    - Identifies problematic sources
    - Learns optimal validation thresholds
    - Suggests targeted fixes
    - Tracks quality trends over time
    """
    
    def __init__(
        self,
        db_pool=None,
        analysis_window_days: int = 7,
        min_pattern_occurrences: int = 5
    ):
        self.db_pool = db_pool
        self.analysis_window = timedelta(days=analysis_window_days)
        self.min_pattern_occurrences = min_pattern_occurrences
        
        # Issue tracking
        self._issues: List[QualityIssue] = []
        self._patterns: Dict[str, IssuePattern] = {}
        self._source_issue_counts: Dict[str, Dict[QualityIssueType, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        
        # Validation rules (with learned thresholds)
        self._validation_rules: Dict[str, ValidationRule] = {}
        self._init_default_rules()
        
        # Quality metrics
        self._quality_scores: List[Tuple[datetime, float]] = []
        self._articles_analyzed: int = 0
        
        # Field-specific patterns
        self._field_patterns: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
    
    def _init_default_rules(self) -> None:
        """Initialize default validation rules."""
        default_rules = [
            ValidationRule("title_required", "title", "required", None),
            ValidationRule("title_length", "title", "length", {"min": 10, "max": 500}),
            ValidationRule("content_required", "content", "required", None),
            ValidationRule("content_length", "content", "length", {"min": 100, "max": 50000}),
            ValidationRule("url_format", "url", "format", r"^https?://"),
            ValidationRule("date_format", "published_date", "format", r"\d{4}-\d{2}-\d{2}"),
            ValidationRule("source_required", "source_id", "required", None),
        ]
        
        for rule in default_rules:
            self._validation_rules[rule.rule_id] = rule
    
    async def analyze_article(
        self,
        article: Dict[str, Any],
        source_id: str,
        validation_results: Optional[Dict[str, bool]] = None
    ) -> List[QualityIssue]:
        """
        Analyze a single article for quality issues.
        
        Args:
            article: Article data dictionary
            source_id: Source identifier
            validation_results: Optional pre-computed validation results
            
        Returns:
            List of quality issues found
        """
        issues: List[QualityIssue] = []
        article_id = article.get("id", article.get("url", "unknown"))
        
        # Apply validation rules
        for rule in self._validation_rules.values():
            issue = self._apply_rule(rule, article, source_id, article_id)
            if issue:
                issues.append(issue)
        
        # Check for content quality issues
        content = article.get("content", "")
        title = article.get("title", "")
        
        # Content too short
        if content and len(content) < 100:
            issues.append(QualityIssue(
                issue_type=QualityIssueType.CONTENT_TOO_SHORT,
                severity=IssueSeverity.MEDIUM,
                source_id=source_id,
                article_id=article_id,
                field_name="content",
                description=f"Content is too short ({len(content)} chars)",
                raw_value=content[:50]
            ))
        
        # Check for spam patterns
        spam_issue = self._check_spam_patterns(content, title, source_id, article_id)
        if spam_issue:
            issues.append(spam_issue)
        
        # Check for encoding issues
        encoding_issue = self._check_encoding(content, title, source_id, article_id)
        if encoding_issue:
            issues.append(encoding_issue)
        
        # Check date freshness
        date_str = article.get("published_date")
        if date_str:
            staleness_issue = self._check_staleness(date_str, source_id, article_id)
            if staleness_issue:
                issues.append(staleness_issue)
        
        # Record issues
        for issue in issues:
            self._issues.append(issue)
            self._source_issue_counts[source_id][issue.issue_type] += 1
        
        self._articles_analyzed += 1
        
        # Update patterns periodically
        if self._articles_analyzed % 100 == 0:
            await self._update_patterns()
        
        return issues
    
    def _apply_rule(
        self,
        rule: ValidationRule,
        article: Dict[str, Any],
        source_id: str,
        article_id: str
    ) -> Optional[QualityIssue]:
        """Apply a validation rule and return issue if violated."""
        value = article.get(rule.field_name)
        
        if rule.rule_type == "required":
            if not value:
                return QualityIssue(
                    issue_type=QualityIssueType.MISSING_FIELD,
                    severity=IssueSeverity.HIGH,
                    source_id=source_id,
                    article_id=article_id,
                    field_name=rule.field_name,
                    description=f"Required field '{rule.field_name}' is missing"
                )
        
        elif rule.rule_type == "length" and value:
            min_len = rule.threshold.get("min", 0)
            max_len = rule.threshold.get("max", float("inf"))
            
            if len(str(value)) < min_len:
                return QualityIssue(
                    issue_type=QualityIssueType.CONTENT_TOO_SHORT,
                    severity=IssueSeverity.MEDIUM,
                    source_id=source_id,
                    article_id=article_id,
                    field_name=rule.field_name,
                    description=f"Field '{rule.field_name}' is too short "
                               f"({len(str(value))} < {min_len})",
                    raw_value=str(value)[:50]
                )
            elif len(str(value)) > max_len:
                return QualityIssue(
                    issue_type=QualityIssueType.CONTENT_TOO_LONG,
                    severity=IssueSeverity.LOW,
                    source_id=source_id,
                    article_id=article_id,
                    field_name=rule.field_name,
                    description=f"Field '{rule.field_name}' exceeds max length "
                               f"({len(str(value))} > {max_len})"
                )
        
        elif rule.rule_type == "format" and value:
            pattern = rule.threshold
            if not re.search(pattern, str(value)):
                return QualityIssue(
                    issue_type=QualityIssueType.INVALID_FORMAT,
                    severity=IssueSeverity.MEDIUM,
                    source_id=source_id,
                    article_id=article_id,
                    field_name=rule.field_name,
                    description=f"Field '{rule.field_name}' has invalid format",
                    raw_value=str(value)[:100]
                )
        
        return None
    
    def _check_spam_patterns(
        self,
        content: str,
        title: str,
        source_id: str,
        article_id: str
    ) -> Optional[QualityIssue]:
        """Check for spam patterns in content."""
        spam_patterns = [
            r"click here",
            r"buy now",
            r"limited offer",
            r"act now",
            r"free money",
            r"congratulations.*winner",
            r"you have been selected",
            r"\$\d+,?\d*\s*(per|a)\s*(day|hour|week)",
        ]
        
        text = f"{title} {content}".lower()
        matches = sum(1 for p in spam_patterns if re.search(p, text, re.IGNORECASE))
        
        if matches >= 2:
            return QualityIssue(
                issue_type=QualityIssueType.SPAM_DETECTED,
                severity=IssueSeverity.HIGH,
                source_id=source_id,
                article_id=article_id,
                field_name="content",
                description=f"Spam patterns detected ({matches} matches)"
            )
        
        return None
    
    def _check_encoding(
        self,
        content: str,
        title: str,
        source_id: str,
        article_id: str
    ) -> Optional[QualityIssue]:
        """Check for encoding issues."""
        # Common mojibake patterns (UTF-8 interpreted as Latin-1)
        encoding_indicators = [
            "\xe2\x80\x99",  # Curly apostrophe (')
            "\xe2\x80\x9c",  # Left double quote (")
            "\xe2\x80\x9d",  # Right double quote (")
            "\xc3\xa9",     # e acute (é)
            "\xc3\xa8",     # e grave (è)
            "\xe2\x80\x94", # Em dash (—)
            "\xc2\xa0",     # Non-breaking space
        ]
        
        text = f"{title} {content}"
        matches = sum(1 for p in encoding_indicators if p in text)
        
        if matches > 0:
            return QualityIssue(
                issue_type=QualityIssueType.ENCODING_ERROR,
                severity=IssueSeverity.MEDIUM,
                source_id=source_id,
                article_id=article_id,
                field_name="content",
                description=f"Encoding issues detected ({matches} instances)"
            )
        
        return None
    
    def _check_staleness(
        self,
        date_str: str,
        source_id: str,
        article_id: str
    ) -> Optional[QualityIssue]:
        """Check if content is stale."""
        try:
            # Try parsing ISO format
            if "T" in date_str:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            
            age = datetime.now() - date.replace(tzinfo=None)
            
            if age > timedelta(days=30):
                return QualityIssue(
                    issue_type=QualityIssueType.STALE_CONTENT,
                    severity=IssueSeverity.LOW,
                    source_id=source_id,
                    article_id=article_id,
                    field_name="published_date",
                    description=f"Content is {age.days} days old",
                    raw_value=date_str
                )
        except (ValueError, TypeError):
            pass
        
        return None
    
    async def _update_patterns(self) -> None:
        """Update issue patterns based on collected data."""
        # Group issues by type and source
        type_source_issues: Dict[Tuple[QualityIssueType, str], List[QualityIssue]] = defaultdict(list)
        
        # Consider only recent issues
        cutoff = datetime.now() - self.analysis_window
        recent_issues = [i for i in self._issues if i.detected_at > cutoff]
        
        for issue in recent_issues:
            key = (issue.issue_type, issue.source_id or "unknown")
            type_source_issues[key].append(issue)
        
        # Identify patterns
        for (issue_type, source_id), issues in type_source_issues.items():
            if len(issues) >= self.min_pattern_occurrences:
                pattern_id = f"{issue_type.value}_{source_id}"
                
                # Get affected fields
                affected_fields = {i.field_name for i in issues if i.field_name}
                
                self._patterns[pattern_id] = IssuePattern(
                    pattern_id=pattern_id,
                    issue_types={issue_type},
                    affected_sources={source_id},
                    affected_fields=affected_fields,
                    occurrence_count=len(issues),
                    first_seen=min(i.detected_at for i in issues),
                    last_seen=max(i.detected_at for i in issues),
                    suggested_fix=self._suggest_fix(issue_type, affected_fields),
                    auto_fixable=self._is_auto_fixable(issue_type),
                    priority_score=self._calculate_priority(issue_type, len(issues))
                )
    
    def _suggest_fix(
        self,
        issue_type: QualityIssueType,
        affected_fields: Set[str]
    ) -> str:
        """Suggest a fix for the issue pattern."""
        fixes = {
            QualityIssueType.MISSING_FIELD: 
                f"Add fallback extraction for fields: {', '.join(affected_fields)}",
            QualityIssueType.INVALID_FORMAT: 
                f"Review format validation rules for: {', '.join(affected_fields)}",
            QualityIssueType.CONTENT_TOO_SHORT: 
                "Consider adjusting minimum content length threshold or improving content extraction",
            QualityIssueType.ENCODING_ERROR: 
                "Add encoding normalization step in scraping pipeline",
            QualityIssueType.SPAM_DETECTED: 
                "Review source credibility and consider lowering source reputation",
            QualityIssueType.STALE_CONTENT: 
                "Increase scraping frequency for fresher content",
            QualityIssueType.DUPLICATE_CONTENT: 
                "Strengthen deduplication rules or adjust similarity threshold",
            QualityIssueType.PARSING_FAILURE: 
                "Update parsing rules for affected source structure changes",
            QualityIssueType.RATE_LIMITED: 
                "Reduce request frequency or implement better rate limiting",
        }
        
        return fixes.get(issue_type, "Manual investigation required")
    
    def _is_auto_fixable(self, issue_type: QualityIssueType) -> bool:
        """Check if issue type can be auto-fixed."""
        auto_fixable = {
            QualityIssueType.ENCODING_ERROR,
            QualityIssueType.STALE_CONTENT,  # Can adjust thresholds
            QualityIssueType.RATE_LIMITED,    # Can adjust timing
        }
        return issue_type in auto_fixable
    
    def _calculate_priority(
        self,
        issue_type: QualityIssueType,
        occurrence_count: int
    ) -> float:
        """Calculate priority score for a pattern."""
        # Base priority by severity
        severity_weights = {
            QualityIssueType.MISSING_FIELD: 3.0,
            QualityIssueType.SPAM_DETECTED: 4.0,
            QualityIssueType.PARSING_FAILURE: 3.5,
            QualityIssueType.ENCODING_ERROR: 2.0,
            QualityIssueType.CONTENT_TOO_SHORT: 1.5,
            QualityIssueType.STALE_CONTENT: 1.0,
        }
        
        base = severity_weights.get(issue_type, 2.0)
        
        # Scale by occurrence (log scale to prevent runaway)
        import math
        occurrence_factor = math.log10(max(1, occurrence_count)) + 1
        
        return base * occurrence_factor
    
    async def generate_quality_report(
        self,
        period_days: int = 7
    ) -> QualityReport:
        """
        Generate a comprehensive quality report.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            QualityReport with analysis results
        """
        period_end = datetime.now()
        period_start = period_end - timedelta(days=period_days)
        
        # Filter issues for period
        period_issues = [
            i for i in self._issues 
            if period_start <= i.detected_at <= period_end
        ]
        
        # Count by type
        issues_by_type: Dict[str, int] = defaultdict(int)
        for issue in period_issues:
            issues_by_type[issue.issue_type.value] += 1
        
        # Count by severity
        issues_by_severity: Dict[str, int] = defaultdict(int)
        for issue in period_issues:
            issues_by_severity[issue.severity.value] += 1
        
        # Count by source
        issues_by_source: Dict[str, int] = defaultdict(int)
        for issue in period_issues:
            if issue.source_id:
                issues_by_source[issue.source_id] += 1
        
        # Get top patterns
        sorted_patterns = sorted(
            self._patterns.values(),
            key=lambda p: p.priority_score,
            reverse=True
        )
        top_patterns = sorted_patterns[:10]
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(period_issues)
        
        # Determine trend
        trend = self._calculate_trend(period_days)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            period_issues, top_patterns, quality_score
        )
        
        return QualityReport(
            period_start=period_start,
            period_end=period_end,
            total_articles_analyzed=self._articles_analyzed,
            total_issues_found=len(period_issues),
            issues_by_type=dict(issues_by_type),
            issues_by_severity=dict(issues_by_severity),
            issues_by_source=dict(issues_by_source),
            top_patterns=top_patterns,
            overall_quality_score=quality_score,
            trend=trend,
            recommendations=recommendations
        )
    
    def _calculate_quality_score(self, issues: List[QualityIssue]) -> float:
        """Calculate overall quality score from issues."""
        if self._articles_analyzed == 0:
            return 1.0
        
        # Weight by severity
        severity_weights = {
            IssueSeverity.LOW: 0.1,
            IssueSeverity.MEDIUM: 0.3,
            IssueSeverity.HIGH: 0.6,
            IssueSeverity.CRITICAL: 1.0,
        }
        
        weighted_issues = sum(
            severity_weights[i.severity] for i in issues
        )
        
        # Score = 1 - (weighted issues per article)
        # Bounded to 0-1 range
        score = 1.0 - min(1.0, weighted_issues / max(1, self._articles_analyzed))
        
        return max(0.0, score)
    
    def _calculate_trend(self, period_days: int) -> str:
        """Calculate quality trend."""
        if len(self._quality_scores) < 2:
            return "stable"
        
        # Compare recent scores to older scores
        cutoff = datetime.now() - timedelta(days=period_days // 2)
        
        recent_scores = [s for t, s in self._quality_scores if t > cutoff]
        older_scores = [s for t, s in self._quality_scores if t <= cutoff]
        
        if not recent_scores or not older_scores:
            return "stable"
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        diff = recent_avg - older_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "degrading"
        else:
            return "stable"
    
    def _generate_recommendations(
        self,
        issues: List[QualityIssue],
        patterns: List[IssuePattern],
        quality_score: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations: List[str] = []
        
        # Critical quality issues
        if quality_score < 0.7:
            recommendations.append(
                "⚠️ CRITICAL: Quality score below 70%. Immediate attention required."
            )
        
        # Top issue types
        type_counts = defaultdict(int)
        for issue in issues:
            type_counts[issue.issue_type] += 1
        
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for issue_type, count in top_types:
            fix = self._suggest_fix(issue_type, set())
            recommendations.append(
                f"Address {issue_type.value} issues ({count} occurrences): {fix}"
            )
        
        # Problematic sources
        source_counts = defaultdict(int)
        for issue in issues:
            if issue.source_id:
                source_counts[issue.source_id] += 1
        
        problem_sources = [
            s for s, c in source_counts.items() 
            if c > len(issues) * 0.1  # Sources with >10% of issues
        ]
        
        if problem_sources:
            recommendations.append(
                f"Review sources with high issue rates: {', '.join(problem_sources[:5])}"
            )
        
        # Auto-fixable patterns
        auto_fixable = [p for p in patterns if p.auto_fixable]
        if auto_fixable:
            recommendations.append(
                f"{len(auto_fixable)} issue patterns can be auto-fixed. "
                f"Consider enabling auto-remediation."
            )
        
        return recommendations
    
    async def get_source_quality_analysis(
        self,
        source_id: str
    ) -> Dict[str, Any]:
        """Get detailed quality analysis for a specific source."""
        source_issues = [i for i in self._issues if i.source_id == source_id]
        
        if not source_issues:
            return {
                "source_id": source_id,
                "has_data": False,
                "message": "No quality data for this source"
            }
        
        # Issue breakdown
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        field_counts = defaultdict(int)
        
        for issue in source_issues:
            type_counts[issue.issue_type.value] += 1
            severity_counts[issue.severity.value] += 1
            if issue.field_name:
                field_counts[issue.field_name] += 1
        
        # Calculate source quality score
        source_articles = len(set(i.article_id for i in source_issues if i.article_id))
        quality_score = self._calculate_quality_score(source_issues)
        
        # Get relevant patterns
        source_patterns = [
            p for p in self._patterns.values()
            if source_id in p.affected_sources
        ]
        
        return {
            "source_id": source_id,
            "has_data": True,
            "total_issues": len(source_issues),
            "articles_with_issues": source_articles,
            "quality_score": quality_score,
            "issues_by_type": dict(type_counts),
            "issues_by_severity": dict(severity_counts),
            "issues_by_field": dict(field_counts),
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "occurrence_count": p.occurrence_count,
                    "suggested_fix": p.suggested_fix,
                    "priority_score": p.priority_score
                }
                for p in source_patterns
            ],
            "recommendations": [
                p.suggested_fix for p in source_patterns if p.suggested_fix
            ][:5]
        }
    
    async def learn_thresholds(
        self,
        field_name: str,
        valid_samples: List[Any],
        invalid_samples: List[Any]
    ) -> Optional[ValidationRule]:
        """
        Learn optimal validation thresholds from sample data.
        
        Args:
            field_name: Field to learn thresholds for
            valid_samples: Examples of valid values
            invalid_samples: Examples of invalid values
            
        Returns:
            Learned ValidationRule or None
        """
        if not valid_samples:
            return None
        
        # For length-based validation
        if all(isinstance(s, str) for s in valid_samples):
            valid_lengths = [len(s) for s in valid_samples]
            
            # Use percentiles to handle outliers
            valid_lengths.sort()
            min_len = valid_lengths[int(len(valid_lengths) * 0.05)]  # 5th percentile
            max_len = valid_lengths[int(len(valid_lengths) * 0.95)]  # 95th percentile
            
            rule = ValidationRule(
                rule_id=f"learned_{field_name}_length",
                field_name=field_name,
                rule_type="length",
                threshold={"min": min_len, "max": max_len},
                learned_from_data=True
            )
            
            # Calculate effectiveness
            if invalid_samples:
                invalid_lengths = [len(s) for s in invalid_samples if isinstance(s, str)]
                caught = sum(
                    1 for l in invalid_lengths 
                    if l < min_len or l > max_len
                )
                rule.effectiveness = caught / len(invalid_samples) if invalid_samples else 0
            
            self._validation_rules[rule.rule_id] = rule
            
            logger.info(
                f"Learned threshold for {field_name}: "
                f"length {min_len}-{max_len}, effectiveness={rule.effectiveness:.1%}"
            )
            
            return rule
        
        return None
    
    async def persist_analysis(self) -> None:
        """Persist analysis results to database."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Persist recent issues
                for issue in self._issues[-1000:]:  # Last 1000 issues
                    await conn.execute("""
                        INSERT INTO l1_quality_issues (
                            issue_type, severity, source_id, article_id,
                            field_name, description, detected_at, resolved
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT DO NOTHING
                    """,
                        issue.issue_type.value, issue.severity.value,
                        issue.source_id, issue.article_id, issue.field_name,
                        issue.description, issue.detected_at, issue.resolved
                    )
                
                # Persist patterns
                for pattern in self._patterns.values():
                    await conn.execute("""
                        INSERT INTO l1_quality_patterns (
                            pattern_id, issue_types, affected_sources,
                            occurrence_count, first_seen, last_seen,
                            suggested_fix, auto_fixable, priority_score
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (pattern_id) DO UPDATE SET
                            occurrence_count = $4,
                            last_seen = $6,
                            priority_score = $9
                    """,
                        pattern.pattern_id,
                        json.dumps([t.value for t in pattern.issue_types]),
                        json.dumps(list(pattern.affected_sources)),
                        pattern.occurrence_count, pattern.first_seen,
                        pattern.last_seen, pattern.suggested_fix,
                        pattern.auto_fixable, pattern.priority_score
                    )
                
                logger.info("Persisted quality analysis data")
        except Exception as e:
            logger.error(f"Failed to persist quality analysis: {e}")
    
    async def load_historical_data(self) -> None:
        """Load historical analysis data from database."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Load recent issues
                rows = await conn.fetch("""
                    SELECT * FROM l1_quality_issues
                    WHERE detected_at > NOW() - INTERVAL '30 days'
                    ORDER BY detected_at DESC
                    LIMIT 10000
                """)
                
                for row in rows:
                    issue = QualityIssue(
                        issue_type=QualityIssueType(row["issue_type"]),
                        severity=IssueSeverity(row["severity"]),
                        source_id=row["source_id"],
                        article_id=row["article_id"],
                        field_name=row["field_name"],
                        description=row["description"],
                        detected_at=row["detected_at"],
                        resolved=row["resolved"]
                    )
                    self._issues.append(issue)
                
                # Load patterns
                pattern_rows = await conn.fetch("""
                    SELECT * FROM l1_quality_patterns
                """)
                
                for row in pattern_rows:
                    pattern = IssuePattern(
                        pattern_id=row["pattern_id"],
                        issue_types={QualityIssueType(t) for t in json.loads(row["issue_types"])},
                        affected_sources=set(json.loads(row["affected_sources"])),
                        affected_fields=set(),
                        occurrence_count=row["occurrence_count"],
                        first_seen=row["first_seen"],
                        last_seen=row["last_seen"],
                        suggested_fix=row["suggested_fix"],
                        auto_fixable=row["auto_fixable"],
                        priority_score=row["priority_score"]
                    )
                    self._patterns[pattern.pattern_id] = pattern
                
                logger.info(
                    f"Loaded {len(self._issues)} issues and "
                    f"{len(self._patterns)} patterns from history"
                )
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
