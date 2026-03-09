"""
Eurogamer Game Scraper Module with Image Support
Handles all web scraping functionality for Eurogamer.net
Images are hotlinked directly from source (no storage)
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
import json
import random
from datetime import datetime


class EurogamerScraper:
    """Main scraper class for Eurogamer.net"""
    
    def __init__(self):
        self.base_url = "https://www.eurogamer.net"
        self.games_data = []
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        self.timeout = 15
        self.min_delay = 2
        self.max_delay = 4
        self.csv_filename = 'games_data.csv'
        self.json_filename = 'games_data.json'
        self._update_headers()
        
    def _update_headers(self):
        """Update headers with random user agent"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    @staticmethod
    def _clean_text(text):
        """Clean extracted text"""
        if not text:
            return "Not Available"
        cleaned = ' '.join(str(text).strip().split())
        return cleaned if cleaned else "Not Available"
    
    def _extract_with_selectors(self, soup, selectors, attribute=None):
        """Extract data using multiple selectors"""
        for selector in selectors:
            try:
                element = None
                if isinstance(selector, tuple):
                    tag, attrs = selector
                    element = soup.find(tag, attrs)
                else:
                    element = soup.select_one(selector)
                
                if element:
                    if attribute:
                        value = element.get(attribute, '')
                    else:
                        value = element.get_text(strip=True)
                    
                    if value:
                        return self._clean_text(value)
            except:
                continue
        return "Not Available"
    
    def _extract_release_date(self, soup):
        """Extract release date from page"""
        # Meta tag selectors
        meta_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publication-date'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'property': 'og:published_time'})
        ]
        
        for tag, attrs in meta_selectors:
            element = soup.find(tag, attrs)
            if element and element.get('content'):
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', element.get('content'))
                if date_match:
                    return date_match.group()
        
        # Time tag selectors
        time_selectors = [
            'time[datetime]',
            '.article-publish-date',
            '.posted-date time',
            '.byline time'
        ]
        
        for selector in time_selectors:
            element = soup.select_one(selector)
            if element:
                if element.get('datetime'):
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', element.get('datetime'))
                    if date_match:
                        return date_match.group()
        
        # Class-based selectors
        class_selectors = [
            '.pub-date', '.date-display', '.article-date',
            '.story-date', '.meta-date', '.post-date'
        ]
        
        for selector in class_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                if re.search(r'\d{4}', date_text):
                    return date_text
        
        return "Not Available"
    
    def _extract_game_image(self, soup):
        """Extract the main game image/review image from the page"""
        try:
            # Strategy 1: Open Graph image (best for social sharing)
            og_image = (
                soup.find('meta', {'property': 'og:image'}) or 
                soup.find('meta', {'name': 'twitter:image'})
            )
            if og_image and og_image.get('content'):
                img_url = og_image['content']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = self.base_url + img_url
                return img_url
            
            # Strategy 2: Article featured image
            featured_selectors = [
                '.article-hero img',
                '.featured-image img',
                '.content-header img',
                'article img',
                '.review-header img',
                '.post-image img',
                '.lead-image img',
                '.entry-content img:first-of-type'
            ]
            
            for selector in featured_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    img_url = img['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = self.base_url + img_url
                    return img_url
            
            # Strategy 3: First large image in article
            article_images = soup.find_all('img')
            for img in article_images[:10]:  # Check first 10 images
                src = img.get('src', '')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Try to get the largest version
                    if 'srcset' in img.attrs:
                        srcset = img['srcset'].split(',')
                        if srcset:
                            largest = srcset[-1].strip().split(' ')[0]
                            if largest.startswith('//'):
                                largest = 'https:' + largest
                            elif largest.startswith('/'):
                                largest = self.base_url + largest
                            return largest
                    
                    # Handle relative URLs
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = self.base_url + src
                    return src
            
            return "Not Available"
        except Exception as e:
            print(f"Error extracting image: {str(e)}")
            return "Not Available"
    
    def _extract_key_features(self, soup):
        """Extract game description/features"""
        selectors = [
            ('meta', {'name': 'description'}),
            ('meta', {'property': 'og:description'}),
            '.article-body p',
            '.game-description',
            '.summary',
            '.standfirst',
            'article p',
            '.entry-content p',
            '.review-body p'
        ]
        
        description = self._extract_with_selectors(soup, selectors)
        
        if description and description != "Not Available" and len(description) > 20:
            return description[:200] + "..." if len(description) > 200 else description
        
        return "Not Available"
    
    def _extract_platforms(self, soup):
        """Extract platform information"""
        selectors = [
            '.platforms', '.platform-list', '.game-platforms',
            '.platform-tags', '.available-on', '.platform-info',
            '.platform', '[class*="platform"]'
        ]
        
        platform_text = self._extract_with_selectors(soup, selectors)
        
        if platform_text and platform_text != "Not Available":
            platforms = re.findall(
                r'PC|PlayStation|PS\d|PS4|PS5|Xbox|Xbox\s+Series|Xbox\s+One|Nintendo|Switch|iOS|Android|Mac|Linux',
                platform_text, re.IGNORECASE
            )
            if platforms:
                return ', '.join(dict.fromkeys(platforms))
        
        return "Not Available"
    
    def _extract_developer(self, soup):
        """Extract developer information"""
        selectors = [
            'a[href*="developer"]',
            '.developer',
            '.developer-info',
            '.game-developer',
            '.developer-name',
            'li:contains("Developer")'
        ]
        
        developer = self._extract_with_selectors(soup, selectors)
        
        if developer and developer != "Not Available" and len(developer) < 50:
            developer = re.sub(r'^(Developer|By|Developed by):?\s*', '', developer, flags=re.IGNORECASE)
            return developer.strip()
        
        return "Not Available"
    
    def _extract_publisher(self, soup):
        """Extract publisher information"""
        selectors = [
            'a[href*="publisher"]',
            '.publisher',
            '.publisher-info',
            '.game-publisher',
            '.publisher-name',
            'li:contains("Publisher")'
        ]
        
        publisher = self._extract_with_selectors(soup, selectors)
        
        if publisher and publisher != "Not Available" and len(publisher) < 50:
            publisher = re.sub(r'^(Publisher|Published by):?\s*', '', publisher, flags=re.IGNORECASE)
            return publisher.strip()
        
        return "Not Available"
    
    def _extract_title(self, soup):
        """Extract game title from page"""
        # Try article title selectors
        title_selectors = [
            'h1.article-headline',
            'h1.article-title',
            '.content-header h1',
            'article header h1',
            '.review-header h1',
            'h1'
        ]
        
        title = "Not Available"
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = self._clean_text(element.text)
                break
        else:
            # Try meta tags as fallback
            meta_title = (
                soup.find('meta', {'property': 'og:title'}) or 
                soup.find('meta', {'name': 'title'})
            )
            if meta_title and meta_title.get('content'):
                title = self._clean_text(meta_title['content'])
        
        # Clean up title
        if title != "Not Available":
            title = re.sub(r'\s*[|-]\s*Eurogamer.*$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*review$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*\|\s*Eurogamer.*$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'^Comments?\s+for\s+"', '', title, flags=re.IGNORECASE)
            title = re.sub(r'"$', '', title, flags=re.IGNORECASE)
        
        return title.strip() if title != "Not Available" else "Not Available"
    
    def _get_game_links(self):
        """Get game links from archive pages"""
        game_links = []
        
        archive_paths = [
            "/archive/reviews",
            "/archive/reviews/page/1",
            "/archive/reviews/page/2",
            "/best-games-2024",
            "/best-games-2023",
            "/reviews",
            "/games",
            "/archive/news"
        ]
        
        for path in archive_paths:
            url = self.base_url + path
            try:
                self._update_headers()
                print(f"Fetching links from: {url}")
                
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        continue
                    
                    if any(p in full_url for p in ['/review/', '/game/', '-review']):
                        if full_url not in game_links and 'eurogamer.net' in full_url:
                            game_links.append(full_url)
                
                time.sleep(random.uniform(self.min_delay, self.max_delay))
                
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                continue
        
        return list(set(game_links))
    
    def scrape_game_page(self, game_url):
        """Scrape individual game page"""
        try:
            self._update_headers()
            print(f"Scraping: {game_url}")
            
            response = self.session.get(game_url, timeout=self.timeout)
            if response.status_code != 200:
                print(f"Failed to fetch {game_url}: Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            game_data = {
                'Game Title': self._extract_title(soup),
                'Release Date': self._extract_release_date(soup),
                'Key Features': self._extract_key_features(soup),
                'Platform Availability': self._extract_platforms(soup),
                'Developer Information': self._extract_developer(soup),
                'Publisher Information': self._extract_publisher(soup),
                'Image URL': self._extract_game_image(soup),
                'URL': game_url,
                'Date Scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"  Title: {game_data['Game Title']}")
            print(f"  Image: {'✓ Found' if game_data['Image URL'] != 'Not Available' else '✗ Not found'}")
            
            return game_data
            
        except Exception as e:
            print(f"Error scraping {game_url}: {str(e)}")
            return None
    
    def scrape_multiple_games(self, num_games=10):
        """Scrape multiple games"""
        print(f"\n{'='*60}")
        print(f"Scraping {num_games} games from Eurogamer.net")
        print(f"{'='*60}\n")
        
        self.games_data = []
        
        # Get game links
        all_links = self._get_game_links()
        print(f"Found {len(all_links)} potential links")
        
        if not all_links:
            print("Using fallback URLs...")
            fallback_paths = [
                "/baldurs-gate-3-review",
                "/zelda-tears-of-the-kingdom-review",
                "/alan-wake-2-review",
                "/spider-man-2-review",
                "/starfield-review",
                "/cyberpunk-2077-phantom-liberty-review",
                "/resident-evil-4-review",
                "/final-fantasy-16-review",
                "/diablo-4-review",
                "/street-fighter-6-review",
                "/god-of-war-ragnarok-review",
                "/elden-ring-review"
            ]
            all_links = [self.base_url + path for path in fallback_paths]
        
        random.shuffle(all_links)
        
        scraped = 0
        for link in all_links:
            if scraped >= num_games:
                break
            
            if any(g['URL'] == link for g in self.games_data):
                continue
            
            game_data = self.scrape_game_page(link)
            if game_data:
                self.games_data.append(game_data)
                scraped += 1
                print(f"✓ Scraped ({scraped}/{num_games}): {game_data['Game Title']}")
            
            time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        print(f"\nScraped {len(self.games_data)} games successfully!")
        return self.games_data
    
    def save_to_csv(self, filename=None):
        """Save scraped data to CSV"""
        if not self.games_data:
            print("No data to save")
            return None
        
        filename = filename or self.csv_filename
        fieldnames = ['Game Title', 'Release Date', 'Key Features',
                     'Platform Availability', 'Developer Information',
                     'Publisher Information', 'Image URL', 'URL', 'Date Scraped']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for game in self.games_data:
                    row = {field: game.get(field, 'Not Available') for field in fieldnames}
                    writer.writerow(row)
            
            print(f"✓ Data saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
            return None
    
    def save_to_json(self, filename=None):
        """Save scraped data to JSON"""
        if not self.games_data:
            return None
        
        filename = filename or self.json_filename
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.games_data, f, ensure_ascii=False, indent=2)
            print(f"✓ Data saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving JSON: {str(e)}")
            return None
    
    def load_from_csv(self, filename=None):
        """Load data from CSV file"""
        filename = filename or self.csv_filename
        
        if not os.path.exists(filename):
            return []
        
        try:
            games = []
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    games.append(row)
            return games
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return []
    
    def clear_data(self):
        """Clear current games data"""
        self.games_data = []
        print("✓ Data cleared")


if __name__ == "__main__":
    # Test the scraper
    scraper = EurogamerScraper()
    games = scraper.scrape_multiple_games(3)
    if games:
        scraper.save_to_csv()
        scraper.save_to_json()