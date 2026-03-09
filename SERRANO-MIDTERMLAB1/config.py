"""
Configuration file for the Eurogamer Game Scraper
"""

class Config:
    """Base configuration"""
    BASE_URL = "https://www.eurogamer.net"
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    REQUEST_TIMEOUT = 15
    MIN_DELAY = 2
    MAX_DELAY = 5
    CSV_FILENAME = 'games_data.csv'
    JSON_FILENAME = 'games_data.json'
    
    # Archive URLs to scrape
    ARCHIVE_URLS = [
        "/archive/reviews",
        "/archive/reviews/page/1",
        "/archive/reviews/page/2",
        "/best-games-2024",
        "/best-games-2023",
        "/reviews"
    ]
    
    # Fallback URLs (used if scraping fails)
    FALLBACK_URLS = [
        "/baldurs-gate-3-review",
        "/zelda-tears-of-the-kingdom-review",
        "/alan-wake-2-review",
        "/spider-man-2-review",
        "/starfield-review",
        "/cyberpunk-2077-phantom-liberty-review",
        "/resident-evil-4-review",
        "/final-fantasy-16-review",
        "/diablo-4-review",
        "/street-fighter-6-review"
    ]