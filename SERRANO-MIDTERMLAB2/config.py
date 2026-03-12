"""
Configuration settings for GeeksforGeeks Academic Scraper
"""

class Config:
    """Application configuration"""
    
    # Website settings
    BASE_URL = "https://www.geeksforgeeks.org"
    TOPIC = "css"
    
    # CSS topic URLs to scrape
    CSS_TOPICS = [
        "/css-tutorial/",
        "/css-introduction/",
        "/css-syntax/",
        "/css-selectors/",
        "/css-colors/",
        "/css-backgrounds/",
        "/css-borders/",
        "/css-margins/",
        "/css-padding/",
        "/css-box-model/",
        "/css-fonts/",
        "/css-text/",
        "/css-links/",
        "/css-positioning/",
        "/css-flexbox/",
        "/css-grid/"
    ]
    
    # Difficulty level keywords
    DIFFICULTY_KEYWORDS = {
        'easy': ['easy', 'beginner', 'basic', 'simple'],
        'medium': ['medium', 'intermediate', 'moderate'],
        'hard': ['hard', 'advanced', 'expert', 'complex']
    }
    
    # Request settings
    REQUEST_TIMEOUT = 15
    MIN_DELAY = 2
    MAX_DELAY = 4
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # PDF settings
    PDF_OUTPUT_DIR = "data/generated_pdfs"
    STUDENT_NAME = "Aron Serrano"
    SUBJECT_CATEGORY = "Web Development - CSS"