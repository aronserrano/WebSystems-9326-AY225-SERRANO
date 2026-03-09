"""
Eurogamer Game Scraper Web Application
Flask-based web interface for displaying scraped game data with images
"""

from flask import Flask, render_template, request, jsonify
from scraper import EurogamerScraper
import os
from datetime import datetime
import re

app = Flask(__name__)

# Global data store
games_data = []


def clean_game_title(title):
    """Helper function to clean game titles"""
    if not title or title == "Not Available":
        return title
    
    patterns = [
        r'\s*[|-]\s*Eurogamer.*$',
        r'\s*review$',
        r'\s*\|\s*Eurogamer.*$',
        r'^Comments?\s+for\s+"',
        r'"$'
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    return title.strip()


@app.route('/')
def index():
    """Home page with search/filter functionality"""
    global games_data
    
    scraper = EurogamerScraper()
    games_data = scraper.load_from_csv()
    
    # Clean titles for display
    for game in games_data:
        game['Display Title'] = clean_game_title(game.get('Game Title', ''))
    
    return render_template('index.html', games=games_data, now=datetime.now)


@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape new data from Eurogamer"""
    global games_data
    
    try:
        data = request.get_json() or {}
        num_games = data.get('num_games', 10)
        
        scraper = EurogamerScraper()
        scraper.clear_data()  # Clear old data before scraping new
        
        scraped_games = scraper.scrape_multiple_games(num_games)
        
        if scraped_games:
            scraper.save_to_csv()
            scraper.save_to_json()
            games_data = scraped_games  # Update global data
            
            # Count images found
            images_found = sum(1 for g in scraped_games if g.get('Image URL') != 'Not Available')
            
            return jsonify({
                'success': True,
                'message': f'Successfully scraped {len(scraped_games)} games! ({images_found} with images)',
                'count': len(scraped_games),
                'images_found': images_found
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No games were scraped. Please try again.'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/filter', methods=['GET'])
def filter_games():
    """Filter games based on search criteria"""
    global games_data
    
    search_term = request.args.get('search', '').lower()
    platform_filter = request.args.get('platform', '').lower()
    
    filtered = games_data
    
    if search_term:
        filtered = [
            g for g in filtered
            if search_term in g.get('Game Title', '').lower()
        ]
    
    if platform_filter and platform_filter != 'all':
        filtered = [
            g for g in filtered
            if platform_filter in g.get('Platform Availability', '').lower()
        ]
    
    # Add display titles
    for game in filtered:
        game['Display Title'] = clean_game_title(game.get('Game Title', ''))
    
    return jsonify(filtered)


@app.route('/refresh', methods=['POST'])
def refresh_data():
    """Refresh data from CSV - resets to saved data"""
    global games_data
    
    scraper = EurogamerScraper()
    games_data = scraper.load_from_csv()
    
    return jsonify({
        'success': True,
        'count': len(games_data)
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about scraped games"""
    global games_data
    
    if not games_data:
        return jsonify({
            'total_games': 0,
            'images_found': 0,
            'platforms': {},
            'developers': {}
        })
    
    # Platform statistics
    platforms = {}
    developers = {}
    images_found = 0
    
    for game in games_data:
        # Count platforms
        plat_text = game.get('Platform Availability', '')
        if plat_text and plat_text != 'Not Available':
            for p in plat_text.split(','):
                p = p.strip()
                if p:
                    platforms[p] = platforms.get(p, 0) + 1
        
        # Count developers
        dev = game.get('Developer Information', '')
        if dev and dev != 'Not Available':
            developers[dev] = developers.get(dev, 0) + 1
        
        # Count images
        if game.get('Image URL') and game['Image URL'] != 'Not Available':
            images_found += 1
    
    return jsonify({
        'total_games': len(games_data),
        'images_found': images_found,
        'platforms': dict(sorted(platforms.items(), key=lambda x: x[1], reverse=True)[:5]),
        'developers': dict(sorted(developers.items(), key=lambda x: x[1], reverse=True)[:5])
    })


@app.route('/reset', methods=['POST'])
def reset_data():
    """Completely reset all data - clears CSV and JSON files"""
    global games_data
    
    try:
        # Clear global data
        games_data = []
        
        # Delete CSV file if it exists
        if os.path.exists('games_data.csv'):
            os.remove('games_data.csv')
            print("✓ Deleted games_data.csv")
        
        # Delete JSON file if it exists
        if os.path.exists('games_data.json'):
            os.remove('games_data.json')
            print("✓ Deleted games_data.json")
        
        return jsonify({
            'success': True,
            'message': 'All data has been reset. Ready to scrape new games!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting data: {str(e)}'
        })


if __name__ == '__main__':
    app.run(debug=True, port=5000)