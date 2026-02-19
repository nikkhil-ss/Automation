"""
Utility functions for Naukri Auto Updater
Provides helper functions for various operations.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.resolve()


def ensure_directories():
    """Ensure all required directories exist."""
    root = get_project_root()
    
    dirs = [
        root / "logs",
        root / "data",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        

def save_state(state_data):
    """Save scheduler state to file for recovery."""
    root = get_project_root()
    state_file = root / "data" / "state.json"
    
    try:
        state_data["last_saved"] = datetime.now().isoformat()
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save state: {e}")


def load_state():
    """Load scheduler state from file."""
    root = get_project_root()
    state_file = root / "data" / "state.json"
    
    try:
        if state_file.exists():
            with open(state_file, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
    
    return {}


def log_update_history(success, details=None):
    """Log update history for analytics."""
    root = get_project_root()
    history_file = root / "data" / "history.json"
    
    try:
        history = []
        if history_file.exists():
            with open(history_file, "r") as f:
                history = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details or {}
        }
        
        history.append(entry)
        
        # Keep only last 100 entries
        history = history[-100:]
        
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to log history: {e}")


def get_update_stats():
    """Get statistics about update history."""
    root = get_project_root()
    history_file = root / "data" / "history.json"
    
    try:
        if not history_file.exists():
            return None
            
        with open(history_file, "r") as f:
            history = json.load(f)
        
        total = len(history)
        successful = sum(1 for h in history if h.get("success"))
        failed = total - successful
        
        last_update = history[-1] if history else None
        
        return {
            "total_updates": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "last_update": last_update
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return None


def validate_config():
    """Validate configuration settings."""
    import config
    
    errors = []
    warnings = []
    
    # Check credentials
    if not config.NAUKRI_EMAIL or config.NAUKRI_EMAIL == "your_email@example.com":
        errors.append("NAUKRI_EMAIL not configured")
        
    if not config.NAUKRI_PASSWORD or config.NAUKRI_PASSWORD == "your_password":
        errors.append("NAUKRI_PASSWORD not configured")
    
    # Check resume
    if config.UPDATE_RESUME:
        if not config.RESUME_PATH:
            errors.append("RESUME_PATH not configured but UPDATE_RESUME is True")
        elif not os.path.exists(config.RESUME_PATH):
            warnings.append(f"Resume file not found: {config.RESUME_PATH}")
    
    # Check headlines
    if config.UPDATE_HEADLINE and not config.HEADLINES:
        warnings.append("UPDATE_HEADLINE is True but no HEADLINES configured")
    
    # Check intervals
    if not config.UPDATE_INTERVALS:
        errors.append("UPDATE_INTERVALS is empty")
    else:
        for h in config.UPDATE_INTERVALS:
            if not 0 <= h <= 23:
                errors.append(f"Invalid hour in UPDATE_INTERVALS: {h}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def print_config_validation():
    """Print configuration validation results."""
    result = validate_config()
    
    print("\n" + "=" * 50)
    print("CONFIGURATION VALIDATION")
    print("=" * 50)
    
    if result["valid"]:
        print("✓ Configuration is valid!")
    else:
        print("✗ Configuration has errors:")
        for err in result["errors"]:
            print(f"  ERROR: {err}")
    
    if result["warnings"]:
        print("\nWarnings:")
        for warn in result["warnings"]:
            print(f"  WARNING: {warn}")
    
    print("=" * 50 + "\n")
    
    return result["valid"]


if __name__ == "__main__":
    # Run validation when executed directly
    ensure_directories()
    print_config_validation()
    
    # Show stats if available
    stats = get_update_stats()
    if stats:
        print("Update Statistics:")
        print(f"  Total Updates: {stats['total_updates']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        if stats['last_update']:
            print(f"  Last Update: {stats['last_update']['timestamp']}")
