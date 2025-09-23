import json
import os

class Settings:
    _settings_file = 'data/settings.json'
    
    @classmethod
    def _load_settings(cls):
        """Load settings from JSON file"""
        if not os.path.exists(cls._settings_file):
            # Create default settings if file doesn't exist
            default_settings = {
                "maintenance_mode": False,
                "quick_recommendations_count": 7,
                "personal_recommendations_count": 7
            }
            cls._save_settings(default_settings)
            return default_settings
        
        try:
            with open(cls._settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return default settings if file is corrupted
            return {
                "maintenance_mode": False,
                "quick_recommendations_count": 7,
                "personal_recommendations_count": 7
            }
    
    @classmethod
    def _save_settings(cls, settings):
        """Save settings to JSON file"""
        os.makedirs(os.path.dirname(cls._settings_file), exist_ok=True)
        with open(cls._settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def is_maintenance_mode(cls):
        """Check if maintenance mode is enabled"""
        settings = cls._load_settings()
        return settings.get('maintenance_mode', False)
    
    @classmethod
    def set_maintenance_mode(cls, enabled):
        """Enable or disable maintenance mode"""
        settings = cls._load_settings()
        settings['maintenance_mode'] = enabled
        cls._save_settings(settings)
        return enabled
    
    @classmethod
    def get_quick_recommendations_count(cls):
        """Get number of quick recommendations to show"""
        settings = cls._load_settings()
        return settings.get('quick_recommendations_count', 7)
    
    @classmethod
    def get_personal_recommendations_count(cls):
        """Get number of personal recommendations to show"""
        settings = cls._load_settings()
        return settings.get('personal_recommendations_count', 7)
    
    @classmethod
    def update_recommendations_count(cls, quick_count, personal_count):
        """Update recommendation counts"""
        settings = cls._load_settings()
        settings['quick_recommendations_count'] = quick_count
        settings['personal_recommendations_count'] = personal_count
        cls._save_settings(settings)
        return True