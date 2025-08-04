import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN', 'your_facebook_access_token')
    FB_PAGE_ID = os.getenv('FB_PAGE_ID', 'your_facebook_page_id')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    FACEBOOK_API_VERSION = 'v23.0'
    FACEBOOK_GRAPH_URL = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}'
    
    DEFAULT_INDUSTRY = 'tech'
    DEFAULT_TONE = 'professional'
    DEFAULT_CONTENT_TYPE = 'trending'
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def validate_config():
        """Validate configuration settings"""
        warnings = []
        
        if Config.FB_ACCESS_TOKEN == 'your_facebook_access_token':
            warnings.append("FB_ACCESS_TOKEN not set - using default value")
        
        if Config.FB_PAGE_ID == 'your_facebook_page_id':
            warnings.append("FB_PAGE_ID not set - using default value")
        
        if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("SECRET_KEY not set - using development key")
        
        return warnings 