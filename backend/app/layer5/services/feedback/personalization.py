"""
Personalization Engine

Learns user preferences and customizes insights delivery.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import statistics


class NotificationChannel(Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class InsightPreference(Enum):
    """User preference for insight visibility."""
    SHOW = "show"
    HIDE = "hide"
    DIGEST = "digest"  # Show in summary only
    URGENT_ONLY = "urgent_only"


@dataclass
class UserPreferences:
    """Complete user preference profile."""
    user_id: str
    company_id: str
    
    # Display preferences
    dashboard_layout: str = "default"
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"
    
    # Notification settings
    notification_channels: List[NotificationChannel] = field(
        default_factory=lambda: [NotificationChannel.IN_APP]
    )
    email_frequency: str = "daily"  # "realtime", "hourly", "daily", "weekly"
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None
    
    # Risk preferences
    risk_appetite: str = "moderate"  # "conservative", "moderate", "aggressive"
    min_risk_severity: str = "low"  # Minimum severity to show
    priority_categories: List[str] = field(default_factory=list)
    hidden_categories: List[str] = field(default_factory=list)
    
    # Opportunity preferences
    opportunity_focus: List[str] = field(default_factory=list)
    min_opportunity_score: float = 0.3
    
    # Industry focus
    industry: str = ""
    related_industries: List[str] = field(default_factory=list)
    
    # Learning data (internal)
    interaction_history: Dict[str, int] = field(default_factory=dict)
    dismissed_insights: Set[str] = field(default_factory=set)
    starred_insights: Set[str] = field(default_factory=set)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PreferenceUpdate:
    """Record of a preference update."""
    update_id: str
    user_id: str
    field_name: str
    old_value: Any
    new_value: Any
    source: str  # "user", "learned", "system"
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalizedSettings:
    """Settings personalized for a specific user."""
    user_id: str
    
    # Thresholds (personalized)
    risk_thresholds: Dict[str, float]
    opportunity_thresholds: Dict[str, float]
    alert_thresholds: Dict[str, float]
    
    # Weights (personalized)
    category_weights: Dict[str, float]
    indicator_weights: Dict[str, float]
    
    # Filters
    active_filters: Dict[str, Any]
    
    # Calculated at
    generated_at: datetime = field(default_factory=datetime.now)


class PersonalizationEngine:
    """
    Learns user preferences and personalizes the experience.
    
    Features:
    - Explicit preference management
    - Implicit learning from user behavior
    - Personalized thresholds and weights
    - Notification customization
    - Industry-specific defaults
    """
    
    def __init__(self):
        """Initialize personalization engine."""
        self._preferences: Dict[str, UserPreferences] = {}
        self._update_history: Dict[str, List[PreferenceUpdate]] = defaultdict(list)
        self._interaction_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Industry defaults
        self._industry_defaults: Dict[str, Dict[str, Any]] = {
            "retail": {
                "priority_categories": ["SUPPLY_CHAIN", "DEMAND", "PRICING"],
                "risk_appetite": "moderate",
                "opportunity_focus": ["MARKET_CAPTURE", "PRICING_POWER"],
            },
            "manufacturing": {
                "priority_categories": ["SUPPLY_CHAIN", "WORKFORCE", "INFRASTRUCTURE"],
                "risk_appetite": "conservative",
                "opportunity_focus": ["COST_REDUCTION", "EFFICIENCY"],
            },
            "logistics": {
                "priority_categories": ["TRANSPORT", "FUEL", "WORKFORCE"],
                "risk_appetite": "moderate",
                "opportunity_focus": ["EFFICIENCY", "MARKET_CAPTURE"],
            },
            "hospitality": {
                "priority_categories": ["DEMAND", "WORKFORCE", "INFRASTRUCTURE"],
                "risk_appetite": "moderate",
                "opportunity_focus": ["DEMAND_SURGE", "PRICING_POWER"],
            },
            "technology": {
                "priority_categories": ["WORKFORCE", "INFRASTRUCTURE", "MARKET"],
                "risk_appetite": "aggressive",
                "opportunity_focus": ["INNOVATION", "MARKET_CAPTURE"],
            },
        }
        
        self._update_counter = 0
    
    def _generate_update_id(self) -> str:
        """Generate unique update ID."""
        self._update_counter += 1
        return f"PREF_UPD_{self._update_counter:06d}"
    
    def get_or_create_preferences(
        self,
        user_id: str,
        company_id: str,
        industry: Optional[str] = None,
    ) -> UserPreferences:
        """
        Get user preferences, creating defaults if needed.
        
        Args:
            user_id: User ID
            company_id: Company ID
            industry: Industry for defaults
        
        Returns:
            UserPreferences object
        """
        if user_id in self._preferences:
            return self._preferences[user_id]
        
        # Create with industry defaults
        defaults = {}
        if industry and industry.lower() in self._industry_defaults:
            defaults = self._industry_defaults[industry.lower()]
        
        preferences = UserPreferences(
            user_id=user_id,
            company_id=company_id,
            industry=industry or "",
            priority_categories=defaults.get("priority_categories", []),
            risk_appetite=defaults.get("risk_appetite", "moderate"),
            opportunity_focus=defaults.get("opportunity_focus", []),
        )
        
        self._preferences[user_id] = preferences
        return preferences
    
    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences if they exist."""
        return self._preferences.get(user_id)
    
    def update_preference(
        self,
        user_id: str,
        field_name: str,
        value: Any,
        source: str = "user",
    ) -> PreferenceUpdate:
        """
        Update a specific preference field.
        
        Args:
            user_id: User ID
            field_name: Name of the preference field
            value: New value
            source: Source of update ("user", "learned", "system")
        
        Returns:
            PreferenceUpdate record
        """
        preferences = self._preferences.get(user_id)
        if not preferences:
            raise ValueError(f"User {user_id} not found")
        
        # Get old value
        old_value = getattr(preferences, field_name, None)
        
        # Create update record
        update = PreferenceUpdate(
            update_id=self._generate_update_id(),
            user_id=user_id,
            field_name=field_name,
            old_value=old_value,
            new_value=value,
            source=source,
        )
        
        # Apply update
        setattr(preferences, field_name, value)
        preferences.updated_at = datetime.now()
        
        # Record in history
        self._update_history[user_id].append(update)
        
        return update
    
    def batch_update_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any],
        source: str = "user",
    ) -> List[PreferenceUpdate]:
        """
        Update multiple preferences at once.
        
        Args:
            user_id: User ID
            updates: Dict of field_name -> value
            source: Source of updates
        
        Returns:
            List of PreferenceUpdate records
        """
        results = []
        for field_name, value in updates.items():
            try:
                update = self.update_preference(user_id, field_name, value, source)
                results.append(update)
            except (ValueError, AttributeError):
                continue
        return results
    
    def record_interaction(
        self,
        user_id: str,
        insight_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record user interaction with an insight.
        
        Args:
            user_id: User ID
            insight_id: Insight ID
            interaction_type: Type of interaction (view, click, dismiss, star, etc.)
            metadata: Additional metadata
        """
        preferences = self._preferences.get(user_id)
        if not preferences:
            return
        
        # Update interaction count
        key = f"{interaction_type}_{insight_id}"
        preferences.interaction_history[key] = (
            preferences.interaction_history.get(key, 0) + 1
        )
        
        # Track specific actions
        if interaction_type == "dismiss":
            preferences.dismissed_insights.add(insight_id)
        elif interaction_type == "star":
            preferences.starred_insights.add(insight_id)
        elif interaction_type == "unstar":
            preferences.starred_insights.discard(insight_id)
        
        # Store detailed interaction data
        if user_id not in self._interaction_data:
            self._interaction_data[user_id] = {"interactions": []}
        
        self._interaction_data[user_id]["interactions"].append({
            "insight_id": insight_id,
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })
    
    def learn_preferences(self, user_id: str) -> List[PreferenceUpdate]:
        """
        Learn preferences from user behavior.
        
        Args:
            user_id: User ID
        
        Returns:
            List of learned preference updates
        """
        preferences = self._preferences.get(user_id)
        if not preferences:
            return []
        
        updates = []
        interactions = self._interaction_data.get(user_id, {}).get("interactions", [])
        
        if len(interactions) < 10:
            # Not enough data
            return []
        
        # Analyze category engagement
        category_engagement: Dict[str, int] = defaultdict(int)
        category_dismissals: Dict[str, int] = defaultdict(int)
        
        for interaction in interactions:
            metadata = interaction.get("metadata", {})
            category = metadata.get("category", "")
            
            if not category:
                continue
            
            if interaction["type"] in ["click", "view", "star"]:
                category_engagement[category] += 1
            elif interaction["type"] == "dismiss":
                category_dismissals[category] += 1
        
        # Learn priority categories
        if category_engagement:
            # Sort by engagement
            sorted_categories = sorted(
                category_engagement.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Top 3 most engaged categories
            new_priorities = [cat for cat, _ in sorted_categories[:3]]
            
            if new_priorities != preferences.priority_categories:
                update = self.update_preference(
                    user_id,
                    "priority_categories",
                    new_priorities,
                    source="learned",
                )
                updates.append(update)
        
        # Learn hidden categories (frequently dismissed)
        if category_dismissals:
            total_interactions = sum(category_engagement.values()) + sum(category_dismissals.values())
            
            hidden = [
                cat for cat, count in category_dismissals.items()
                if count / total_interactions > 0.3  # >30% dismissal rate
            ]
            
            if hidden and hidden != preferences.hidden_categories:
                update = self.update_preference(
                    user_id,
                    "hidden_categories",
                    hidden,
                    source="learned",
                )
                updates.append(update)
        
        return updates
    
    def get_personalized_settings(
        self,
        user_id: str,
        base_thresholds: Optional[Dict[str, float]] = None,
    ) -> PersonalizedSettings:
        """
        Get personalized settings for a user.
        
        Args:
            user_id: User ID
            base_thresholds: Base threshold values
        
        Returns:
            PersonalizedSettings object
        """
        preferences = self._preferences.get(user_id)
        
        if not preferences:
            # Return defaults
            return PersonalizedSettings(
                user_id=user_id,
                risk_thresholds={},
                opportunity_thresholds={},
                alert_thresholds={},
                category_weights={},
                indicator_weights={},
                active_filters={},
            )
        
        # Adjust thresholds based on risk appetite
        risk_adjustment = {
            "conservative": 0.1,  # Lower thresholds (more alerts)
            "moderate": 0.0,
            "aggressive": -0.1,  # Higher thresholds (fewer alerts)
        }.get(preferences.risk_appetite, 0.0)
        
        base = base_thresholds or {}
        
        risk_thresholds = {
            "critical": base.get("critical_risk", 0.8) + risk_adjustment,
            "high": base.get("high_risk", 0.6) + risk_adjustment,
            "medium": base.get("medium_risk", 0.4) + risk_adjustment,
            "low": base.get("low_risk", 0.2) + risk_adjustment,
        }
        
        opportunity_thresholds = {
            "high": base.get("high_opportunity", 0.7),
            "medium": base.get("medium_opportunity", 0.5),
            "minimum": preferences.min_opportunity_score,
        }
        
        # Category weights based on priorities
        category_weights = {}
        for i, cat in enumerate(preferences.priority_categories):
            category_weights[cat] = 1.0 - (i * 0.1)  # 1.0, 0.9, 0.8, ...
        
        for cat in preferences.hidden_categories:
            category_weights[cat] = 0.0
        
        # Build filters
        active_filters = {
            "min_severity": preferences.min_risk_severity,
            "categories": preferences.priority_categories,
            "hidden": preferences.hidden_categories,
            "industry": preferences.industry,
            "opportunity_focus": preferences.opportunity_focus,
        }
        
        return PersonalizedSettings(
            user_id=user_id,
            risk_thresholds=risk_thresholds,
            opportunity_thresholds=opportunity_thresholds,
            alert_thresholds={},
            category_weights=category_weights,
            indicator_weights={},
            active_filters=active_filters,
        )
    
    def should_show_insight(
        self,
        user_id: str,
        insight_id: str,
        insight_type: str,
        category: str,
        severity: str,
        score: float,
    ) -> bool:
        """
        Determine if an insight should be shown to a user.
        
        Args:
            user_id: User ID
            insight_id: Insight ID
            insight_type: Type of insight (risk, opportunity)
            category: Category of insight
            severity: Severity level
            score: Score value
        
        Returns:
            True if insight should be shown
        """
        preferences = self._preferences.get(user_id)
        
        if not preferences:
            return True  # No preferences = show all
        
        # Check if dismissed
        if insight_id in preferences.dismissed_insights:
            return False
        
        # Check hidden categories
        if category in preferences.hidden_categories:
            return False
        
        # Check minimum severity for risks
        if insight_type == "risk":
            severity_order = ["low", "medium", "high", "critical"]
            min_idx = severity_order.index(preferences.min_risk_severity.lower())
            current_idx = severity_order.index(severity.lower()) if severity.lower() in severity_order else 0
            
            if current_idx < min_idx:
                return False
        
        # Check minimum score for opportunities
        if insight_type == "opportunity":
            if score < preferences.min_opportunity_score:
                return False
        
        return True
    
    def get_notification_settings(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Get notification settings for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Notification settings dict
        """
        preferences = self._preferences.get(user_id)
        
        if not preferences:
            return {
                "channels": [NotificationChannel.IN_APP.value],
                "email_frequency": "daily",
                "quiet_hours": None,
            }
        
        quiet_hours = None
        if preferences.quiet_hours_start is not None:
            quiet_hours = {
                "start": preferences.quiet_hours_start,
                "end": preferences.quiet_hours_end or 7,
            }
        
        return {
            "channels": [c.value for c in preferences.notification_channels],
            "email_frequency": preferences.email_frequency,
            "quiet_hours": quiet_hours,
        }
    
    def is_in_quiet_hours(self, user_id: str) -> bool:
        """Check if user is currently in quiet hours."""
        preferences = self._preferences.get(user_id)
        
        if not preferences or preferences.quiet_hours_start is None:
            return False
        
        current_hour = datetime.now().hour
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end or 7
        
        if start <= end:
            return start <= current_hour < end
        else:
            # Overnight (e.g., 22:00 to 07:00)
            return current_hour >= start or current_hour < end
    
    def get_preference_history(
        self,
        user_id: str,
        field_name: Optional[str] = None,
        days: int = 30,
    ) -> List[PreferenceUpdate]:
        """
        Get history of preference changes.
        
        Args:
            user_id: User ID
            field_name: Filter by field name
            days: Number of days of history
        
        Returns:
            List of PreferenceUpdate records
        """
        history = self._update_history.get(user_id, [])
        
        cutoff = datetime.now() - timedelta(days=days)
        
        results = [
            u for u in history
            if u.updated_at >= cutoff
        ]
        
        if field_name:
            results = [u for u in results if u.field_name == field_name]
        
        return results
    
    def export_preferences(self, user_id: str) -> Dict[str, Any]:
        """Export user preferences for backup."""
        preferences = self._preferences.get(user_id)
        
        if not preferences:
            return {}
        
        return {
            "user_id": preferences.user_id,
            "company_id": preferences.company_id,
            "dashboard_layout": preferences.dashboard_layout,
            "theme": preferences.theme,
            "language": preferences.language,
            "timezone": preferences.timezone,
            "notification_channels": [c.value for c in preferences.notification_channels],
            "email_frequency": preferences.email_frequency,
            "quiet_hours_start": preferences.quiet_hours_start,
            "quiet_hours_end": preferences.quiet_hours_end,
            "risk_appetite": preferences.risk_appetite,
            "min_risk_severity": preferences.min_risk_severity,
            "priority_categories": preferences.priority_categories,
            "hidden_categories": preferences.hidden_categories,
            "opportunity_focus": preferences.opportunity_focus,
            "min_opportunity_score": preferences.min_opportunity_score,
            "industry": preferences.industry,
            "related_industries": preferences.related_industries,
            "exported_at": datetime.now().isoformat(),
        }
    
    def import_preferences(
        self,
        user_id: str,
        company_id: str,
        data: Dict[str, Any],
    ) -> UserPreferences:
        """Import user preferences from backup."""
        preferences = UserPreferences(
            user_id=user_id,
            company_id=company_id,
            dashboard_layout=data.get("dashboard_layout", "default"),
            theme=data.get("theme", "light"),
            language=data.get("language", "en"),
            timezone=data.get("timezone", "UTC"),
            notification_channels=[
                NotificationChannel(c) for c in data.get("notification_channels", ["in_app"])
            ],
            email_frequency=data.get("email_frequency", "daily"),
            quiet_hours_start=data.get("quiet_hours_start"),
            quiet_hours_end=data.get("quiet_hours_end"),
            risk_appetite=data.get("risk_appetite", "moderate"),
            min_risk_severity=data.get("min_risk_severity", "low"),
            priority_categories=data.get("priority_categories", []),
            hidden_categories=data.get("hidden_categories", []),
            opportunity_focus=data.get("opportunity_focus", []),
            min_opportunity_score=data.get("min_opportunity_score", 0.3),
            industry=data.get("industry", ""),
            related_industries=data.get("related_industries", []),
        )
        
        self._preferences[user_id] = preferences
        return preferences
    
    def delete_preferences(self, user_id: str) -> bool:
        """Delete user preferences."""
        if user_id in self._preferences:
            del self._preferences[user_id]
            if user_id in self._update_history:
                del self._update_history[user_id]
            if user_id in self._interaction_data:
                del self._interaction_data[user_id]
            return True
        return False
