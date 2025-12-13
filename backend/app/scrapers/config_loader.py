"""
Source Configuration Loader

Loads, validates, and manages source configuration YAML files.
This implements the Configuration-Driven Architecture from the Layer 1 blueprint.

Features:
- Load all source configs from sources/ directory
- Validate config schema
- Dynamic discovery of new configs
- Hot reload support (iteration 2)
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SourceMetadata:
    """Source metadata from YAML config."""
    name: str
    source_type: str
    base_url: str
    language: str
    credibility_score: float = 0.75
    update_frequency_minutes: int = 60


@dataclass 
class ScrapingConfig:
    """Scraping configuration from YAML."""
    method: str  # 'html', 'rss', 'api', 'selenium'
    entry_points: List[Dict[str, Any]] = field(default_factory=list)
    selectors: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limiting: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceConfig:
    """Complete source configuration."""
    config_path: str
    metadata: SourceMetadata
    scraping: ScrapingConfig
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    categorization: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    loaded_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def source_name(self) -> str:
        return self.metadata.name
    
    @property
    def is_active(self) -> bool:
        """Check if source is active for scraping."""
        return True  # Can be extended with active flag in config


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigurationLoader:
    """
    Loads and manages source configuration YAML files.
    
    Usage:
        loader = ConfigurationLoader()
        sources = loader.load_all_sources()
        
        config = loader.get_source_config("Ada Derana")
        if config:
            print(f"Scraping method: {config.scraping.method}")
    """
    
    # Required fields in metadata section
    REQUIRED_METADATA = ["name", "source_type", "base_url", "language"]
    
    # Required fields in scraping section
    REQUIRED_SCRAPING = ["method"]
    
    # Valid scraping methods
    VALID_METHODS = ["html", "rss", "api", "selenium"]
    
    def __init__(self, sources_dir: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            sources_dir: Path to sources directory. 
                        Defaults to 'sources/' in backend root.
        """
        if sources_dir:
            self.sources_dir = Path(sources_dir)
        else:
            # Default to backend/sources/
            backend_dir = Path(__file__).parent.parent.parent
            self.sources_dir = backend_dir / "sources"
        
        self._configs: Dict[str, SourceConfig] = {}
        self._load_errors: Dict[str, str] = {}
        
        logger.info(f"ConfigurationLoader initialized with sources_dir: {self.sources_dir}")
    
    def load_all_sources(self) -> Dict[str, SourceConfig]:
        """
        Load all source configurations from the sources directory.
        
        Returns:
            Dictionary mapping source name to SourceConfig
        """
        self._configs = {}
        self._load_errors = {}
        
        if not self.sources_dir.exists():
            logger.warning(f"Sources directory does not exist: {self.sources_dir}")
            return {}
        
        yaml_files = list(self.sources_dir.glob("*.yaml")) + list(self.sources_dir.glob("*.yml"))
        
        for yaml_path in yaml_files:
            try:
                config = self._load_single_source(yaml_path)
                if config:
                    self._configs[config.source_name] = config
                    logger.info(f"Loaded config: {config.source_name} from {yaml_path.name}")
            except Exception as e:
                error_msg = f"Failed to load {yaml_path.name}: {str(e)}"
                self._load_errors[str(yaml_path)] = error_msg
                logger.error(error_msg)
        
        logger.info(f"Loaded {len(self._configs)} source configurations")
        return self._configs
    
    def _load_single_source(self, yaml_path: Path) -> Optional[SourceConfig]:
        """Load a single source configuration file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ConfigValidationError(f"Empty configuration file: {yaml_path}")
        
        # Validate structure
        validation_result = self.validate_config(data)
        if not validation_result["is_valid"]:
            raise ConfigValidationError(
                f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Parse metadata
        meta_data = data.get("metadata", {})
        metadata = SourceMetadata(
            name=meta_data["name"],
            source_type=meta_data["source_type"],
            base_url=meta_data["base_url"],
            language=meta_data["language"],
            credibility_score=meta_data.get("credibility_score", 0.75),
            update_frequency_minutes=meta_data.get("update_frequency_minutes", 60)
        )
        
        # Parse scraping config
        scrape_data = data.get("scraping", {})
        scraping = ScrapingConfig(
            method=scrape_data["method"],
            entry_points=scrape_data.get("entry_points", []),
            selectors=scrape_data.get("selectors", {}),
            headers=scrape_data.get("headers", {}),
            rate_limiting=scrape_data.get("rate_limiting", {}),
            validation=scrape_data.get("validation", {})
        )
        
        return SourceConfig(
            config_path=str(yaml_path),
            metadata=metadata,
            scraping=scraping,
            preprocessing=data.get("preprocessing", {}),
            categorization=data.get("categorization", {}),
            error_handling=data.get("error_handling", {})
        )
    
    def validate_config(self, yaml_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate source configuration content.
        
        Args:
            yaml_content: Parsed YAML content dictionary
            
        Returns:
            Dict with 'is_valid' bool and 'errors' list
        """
        errors = []
        warnings = []
        
        # Check metadata section
        if "metadata" not in yaml_content:
            errors.append("Missing 'metadata' section")
        else:
            meta = yaml_content["metadata"]
            for field in self.REQUIRED_METADATA:
                if field not in meta:
                    errors.append(f"Missing required metadata field: {field}")
        
        # Check scraping section
        if "scraping" not in yaml_content:
            errors.append("Missing 'scraping' section")
        else:
            scraping = yaml_content["scraping"]
            for field in self.REQUIRED_SCRAPING:
                if field not in scraping:
                    errors.append(f"Missing required scraping field: {field}")
            
            # Validate method
            method = scraping.get("method", "")
            if method and method not in self.VALID_METHODS:
                errors.append(f"Invalid scraping method: {method}. Valid: {self.VALID_METHODS}")
            
            # Validate entry points
            if not scraping.get("entry_points"):
                warnings.append("No entry_points defined")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_source_config(self, source_name: str) -> Optional[SourceConfig]:
        """
        Get configuration for a specific source.
        
        Args:
            source_name: Name of the source (e.g., "Ada Derana")
            
        Returns:
            SourceConfig if found, None otherwise
        """
        # Load configs if not already loaded
        if not self._configs:
            self.load_all_sources()
        
        return self._configs.get(source_name)
    
    def get_all_configs(self) -> Dict[str, SourceConfig]:
        """Get all loaded configurations."""
        if not self._configs:
            self.load_all_sources()
        return self._configs
    
    def get_active_sources(self) -> List[SourceConfig]:
        """Get list of active source configurations."""
        return [c for c in self.get_all_configs().values() if c.is_active]
    
    def get_load_errors(self) -> Dict[str, str]:
        """Get any errors that occurred during loading."""
        return self._load_errors
    
    def reload_source(self, source_name: str) -> Optional[SourceConfig]:
        """
        Reload a specific source configuration.
        
        Args:
            source_name: Name of the source to reload
            
        Returns:
            Updated SourceConfig, or None if source not found
        """
        config = self._configs.get(source_name)
        if config:
            try:
                new_config = self._load_single_source(Path(config.config_path))
                if new_config:
                    self._configs[source_name] = new_config
                    logger.info(f"Reloaded config for: {source_name}")
                    return new_config
            except Exception as e:
                logger.error(f"Failed to reload {source_name}: {e}")
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        configs = self.get_all_configs()
        return {
            "total_sources": len(configs),
            "active_sources": len([c for c in configs.values() if c.is_active]),
            "by_type": self._count_by_type(configs),
            "by_method": self._count_by_method(configs),
            "load_errors": len(self._load_errors)
        }
    
    def _count_by_type(self, configs: Dict[str, SourceConfig]) -> Dict[str, int]:
        """Count configurations by source type."""
        counts: Dict[str, int] = {}
        for config in configs.values():
            stype = config.metadata.source_type
            counts[stype] = counts.get(stype, 0) + 1
        return counts
    
    def _count_by_method(self, configs: Dict[str, SourceConfig]) -> Dict[str, int]:
        """Count configurations by scraping method."""
        counts: Dict[str, int] = {}
        for config in configs.values():
            method = config.scraping.method
            counts[method] = counts.get(method, 0) + 1
        return counts


# Factory function
def create_config_loader(sources_dir: Optional[str] = None) -> ConfigurationLoader:
    """Create and return a ConfigurationLoader instance."""
    return ConfigurationLoader(sources_dir)


# Convenience function to get all sources
def get_all_source_configs() -> Dict[str, SourceConfig]:
    """Load and return all source configurations."""
    loader = ConfigurationLoader()
    return loader.load_all_sources()
