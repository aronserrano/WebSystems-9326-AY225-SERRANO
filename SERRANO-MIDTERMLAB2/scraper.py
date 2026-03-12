"""
GeeksforGeeks Academic Scraper
Scrapes CSS tutorials and articles from GeeksforGeeks
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import random
from datetime import datetime
from config import Config


class GeeksforGeeksScraper:
    """Scraper for GeeksforGeeks CSS tutorials"""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.articles_data = []
        self.session = requests.Session()
        self.data_dir = "data"
        self._ensure_directories()
        self._update_headers()
        
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _update_headers(self):
        """Update headers with random user agent"""
        self.session.headers.update({
            'User-Agent': random.choice(Config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
    
    @staticmethod
    def _clean_text(text):
        """Clean extracted text"""
        if not text:
            return "Not Available"
        return ' '.join(str(text).strip().split()) or "Not Available"
    
    def _extract_title(self, soup):
        """Extract article title"""
        selectors = ['h1.entry-title', 'h1.article-title', 'article h1', 'h1']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = self._clean_text(element.text)
                title = re.sub(r'\s*[|-]\s*GeeksforGeeks.*$', '', title, flags=re.IGNORECASE)
                return title
        return "Not Available"
    
    def _extract_difficulty(self, soup):
        """Extract difficulty level"""
        text = soup.get_text().lower()[:2000]
        
        for level, keywords in Config.DIFFICULTY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return level.capitalize()
        
        return "Not Available"
    
    def _extract_key_concepts(self, soup):
        """Extract key concepts"""
        paragraphs = soup.find_all('p')
        for p in paragraphs[:3]:
            text = self._clean_text(p.get_text())
            if len(text) > 50:
                return text[:300] + "..." if len(text) > 300 else text
        return "Not Available"
    
    def _extract_code_snippets(self, soup):
        """Extract code snippets"""
        snippets = []
        code_blocks = soup.find_all(['pre', 'code'])
        
        for code in code_blocks[:3]:
            code_text = code.get_text(strip=True)
            if code_text and len(code_text) > 10:
                language = "css"
                if 'class' in code.attrs:
                    classes = ' '.join(code['class']).lower()
                    if 'html' in classes:
                        language = "html"
                    elif 'js' in classes or 'javascript' in classes:
                        language = "javascript"
                
                snippets.append({
                    'language': language,
                    'code': code_text[:300] + "..." if len(code_text) > 300 else code_text
                })
        
        return snippets if snippets else "Not Available"
    
    def _extract_complexity(self, soup):
        """Extract complexity analysis"""
        complexity = {
            'time': "Not Available",
            'space': "Not Available"
        }
        
        text = soup.get_text().lower()
        
        time_match = re.search(r'time complexity[:\s]+([^.!?]+)', text)
        if time_match:
            complexity['time'] = self._clean_text(time_match.group(1))
        
        space_match = re.search(r'space complexity[:\s]+([^.!?]+)', text)
        if space_match:
            complexity['space'] = self._clean_text(space_match.group(1))
        
        return complexity
    
    def _extract_references(self, soup):
        """Extract references"""
        references = []
        
        links = soup.find_all('a', href=True)
        for link in links[:5]:
            href = link['href']
            if href.startswith('http') and 'geeksforgeeks.org' in href:
                title = self._clean_text(link.get_text())
                if title and len(title) > 5:
                    references.append({
                        'title': title,
                        'url': href
                    })
        
        return references if references else "Not Available"
    
    def scrape_article(self, url):
        """Scrape individual article"""
        try:
            self._update_headers()
            full_url = url if url.startswith('http') else self.base_url + url
            
            response = self.session.get(full_url, timeout=Config.REQUEST_TIMEOUT)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_data = {
                'title': self._extract_title(soup),
                'difficulty': self._extract_difficulty(soup),
                'concepts': self._extract_key_concepts(soup),
                'code_snippets': self._extract_code_snippets(soup),
                'complexity': self._extract_complexity(soup),
                'references': self._extract_references(soup),
                'url': full_url,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            return article_data
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_multiple(self, count=10):
        """Scrape multiple articles"""
        print(f"\nScraping {count} CSS articles...")
        
        self.articles_data = []
        urls = [self.base_url + path for path in Config.CSS_TOPICS]
        random.shuffle(urls)
        
        scraped = 0
        for url in urls:
            if scraped >= count:
                break
            
            article = self.scrape_article(url)
            if article and article['title'] != "Not Available":
                self.articles_data.append(article)
                scraped += 1
                print(f"✓ {scraped}/{count}: {article['title']}")
            
            time.sleep(random.uniform(Config.MIN_DELAY, Config.MAX_DELAY))
        
        return self.articles_data
    
    def save_data(self, filename='scraped_data.json'):
        """Save data to JSON"""
        if not self.articles_data:
            return None
        
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.articles_data, f, indent=2)
        
        return filepath
    
    def load_data(self, filename='scraped_data.json'):
        """Load data from JSON"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clear_data(self):
        """Clear current data"""
        self.articles_data = []