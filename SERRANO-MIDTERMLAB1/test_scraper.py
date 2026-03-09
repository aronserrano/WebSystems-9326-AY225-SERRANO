# test_scraper.py - Save this in your MIDTERM-LAB-1 folder
from scraper import EurogamerScraper

print("Testing Eurogamer Scraper...")
print(f"Current directory: {__file__}")
print("-" * 50)

# Create scraper instance
scraper = EurogamerScraper()

# Try to scrape 3 games
games = scraper.scrape_multiple_games(3)

if games:
    print(f"\n✅ Successfully scraped {len(games)} games!")
    print("\n" + "="*60)
    print("SAMPLE GAME DATA:")
    print("="*60)
    
    for i, game in enumerate(games, 1):
        print(f"\n{i}. {game['Game Title']}")
        print(f"   📅 Release: {game['Release Date']}")
        print(f"   🎮 Platforms: {game['Platform Availability']}")
        print(f"   👨‍💻 Developer: {game['Developer Information']}")
        print(f"   🏢 Publisher: {game['Publisher Information']}")
        print(f"   ⭐ Features: {game['Key Features'][:100]}...")
        print("-" * 40)
else:
    print("❌ No games were scraped")

# Save to files
if games:
    scraper.save_to_csv()
    scraper.save_to_json()
    print("\n✅ Data saved to games_data.csv and games_data.json")