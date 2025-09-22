import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import json
import sqlite3
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import openai
import logging

class IntelligentDonorCrawler:
    def __init__(self, api_key, db_path="donor_prospects.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=api_key)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.setup_database()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                organization_name TEXT,
                emails TEXT,
                phones TEXT,
                addresses TEXT,
                content_text TEXT,
                sustainability_score REAL,
                donation_probability REAL,
                engagement_score REAL,
                final_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_intelligent_urls(self, prompt_text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at finding organizations that would be interested in environmental sustainability and beach cleanup initiatives. Return only valid URLs with proper protocols."},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens=300,
                temperature=0.3,
            )
            text = response.choices[0].message.content.strip()
            urls = re.findall(r'https?://(?:www\.)?[^\s/$.?#].[^\s]*', text)
            return [url for url in urls if self.is_valid_url(url)]
        except Exception as e:
            self.logger.error(f"Error getting URLs from LLM: {e}")
            return []

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def extract_enhanced_contact_info(self, text, soup):
        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
        
        phone_patterns = [
            r'\+?\d{1,3}[\s\-\.]?\(?\d{2,4}\)?[\s\-\.]?\d{2,4}[\s\-\.]?\d{2,4}',
            r'\(\d{3}\)\s?\d{3}[\s\-]?\d{4}',
            r'\d{3}[\s\-]?\d{3}[\s\-]?\d{4}'
        ]
        
        phones = set()
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                digits = re.sub(r'\D', '', match)
                if 9 <= len(digits) <= 15:
                    phones.add(match.strip())

        addresses = set()
        address_selectors = ['address', '[class*="address"]', '[class*="contact"]', '[class*="location"]']
        for selector in address_selectors:
            elements = soup.select(selector)
            for element in elements:
                addr_text = element.get_text(separator=' ', strip=True)
                if len(addr_text) > 20 and any(word in addr_text.lower() for word in ['street', 'avenue', 'road', 'blvd', 'suite']):
                    addresses.add(addr_text)

        return emails, phones, addresses

    def extract_organization_name(self, soup, url):
        name_selectors = [
            'title',
            'h1',
            '[class*="company"]',
            '[class*="organization"]',
            '[class*="brand"]',
            'meta[property="og:site_name"]'
        ]
        
        for selector in name_selectors:
            elements = soup.select(selector)
            for element in elements:
                if selector == 'meta[property="og:site_name"]':
                    name = element.get('content', '').strip()
                else:
                    name = element.get_text(strip=True)
                
                if name and len(name) < 100:
                    return name
        
        domain = urlparse(url).netloc
        return domain.replace('www.', '').replace('.com', '').replace('.org', '').title()

    def calculate_sustainability_score(self, text):
        sustainability_keywords = [
            'sustainability', 'sustainable', 'environment', 'environmental', 'green', 'eco',
            'climate', 'carbon', 'renewable', 'clean energy', 'conservation', 'biodiversity',
            'ocean', 'marine', 'beach', 'coastal', 'pollution', 'waste', 'recycling',
            'circular economy', 'ESG', 'social responsibility', 'impact'
        ]
        
        text_lower = text.lower()
        score = 0
        for keyword in sustainability_keywords:
            count = text_lower.count(keyword)
            score += count * (len(keyword) / 10)
        
        return min(score / 10, 1.0)

    def calculate_engagement_score(self, soup):
        engagement_indicators = {
            'social_links': len(soup.find_all('a', href=re.compile(r'(facebook|twitter|linkedin|instagram)'))),
            'contact_forms': len(soup.find_all(['form', 'input[type="email"]'])),
            'newsletter_signup': len(soup.find_all(text=re.compile(r'newsletter|subscribe', re.I))),
            'blog_posts': len(soup.find_all(['article', '[class*="blog"]', '[class*="news"]'])),
            'events': len(soup.find_all(text=re.compile(r'event|conference|workshop', re.I)))
        }
        
        total_score = sum(engagement_indicators.values())
        return min(total_score / 20, 1.0)

    def predict_donation_probability(self, text, sustainability_score, engagement_score):
        donation_keywords = [
            'donate', 'donation', 'support', 'contribute', 'fund', 'sponsor',
            'philanthropy', 'charity', 'giving', 'grant', 'foundation'
        ]
        
        text_lower = text.lower()
        donation_mentions = sum(text_lower.count(keyword) for keyword in donation_keywords)
        
        base_probability = min(donation_mentions / 20, 0.4)
        sustainability_boost = sustainability_score * 0.3
        engagement_boost = engagement_score * 0.3
        
        return min(base_probability + sustainability_boost + engagement_boost, 1.0)

    def crawl_intelligent_website(self, start_url, max_pages=15, delay=2):
        visited = set()
        to_visit = deque([start_url])
        all_emails, all_phones, all_addresses = set(), set(), set()
        all_text = ""
        domain = urlparse(start_url).netloc
        organization_name = ""

        while to_visit and len(visited) < max_pages:
            url = to_visit.popleft()
            if url in visited:
                continue
                
            try:
                time.sleep(delay)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, timeout=15, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text(separator=' ', strip=True)
                all_text += " " + text
                
                if not organization_name:
                    organization_name = self.extract_organization_name(soup, url)
                
                emails, phones, addresses = self.extract_enhanced_contact_info(text, soup)
                all_emails.update(emails)
                all_phones.update(phones)
                all_addresses.update(addresses)
                
                visited.add(url)

                priority_pages = ['about', 'contact', 'mission', 'sustainability', 'environment', 'impact']
                regular_links = []
                priority_links = []
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    parsed_url = urlparse(full_url)
                    
                    if (parsed_url.netloc == domain and 
                        full_url not in visited and 
                        full_url not in to_visit and
                        not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip'])):
                        
                        if any(page in full_url.lower() for page in priority_pages):
                            priority_links.append(full_url)
                        else:
                            regular_links.append(full_url)
                
                for link in priority_links[:3]:
                    to_visit.appendleft(link)
                for link in regular_links[:2]:
                    to_visit.append(link)
                    
            except Exception as e:
                self.logger.warning(f"Error crawling {url}: {e}")
                continue

        sustainability_score = self.calculate_sustainability_score(all_text)
        engagement_score = self.calculate_engagement_score(soup if 'soup' in locals() else BeautifulSoup('', 'html.parser'))
        donation_probability = self.predict_donation_probability(all_text, sustainability_score, engagement_score)
        
        final_score = (sustainability_score * 0.4 + 
                      donation_probability * 0.4 + 
                      engagement_score * 0.2)

        return {
            'url': start_url,
            'organization_name': organization_name,
            'emails': list(all_emails),
            'phones': list(all_phones),
            'addresses': list(all_addresses),
            'content_text': all_text[:5000],
            'sustainability_score': sustainability_score,
            'donation_probability': donation_probability,
            'engagement_score': engagement_score,
            'final_score': final_score
        }

    def save_prospect(self, prospect_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO prospects 
                (url, organization_name, emails, phones, addresses, content_text, 
                 sustainability_score, donation_probability, engagement_score, final_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prospect_data['url'],
                prospect_data['organization_name'],
                json.dumps(prospect_data['emails']),
                json.dumps(prospect_data['phones']),
                json.dumps(prospect_data['addresses']),
                prospect_data['content_text'],
                prospect_data['sustainability_score'],
                prospect_data['donation_probability'],
                prospect_data['engagement_score'],
                prospect_data['final_score']
            ))
            conn.commit()
            self.logger.info(f"Saved prospect: {prospect_data['organization_name']}")
        except Exception as e:
            self.logger.error(f"Error saving prospect: {e}")
        finally:
            conn.close()

    def get_top_prospects(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM prospects 
            ORDER BY final_score DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        prospects = []
        for row in results:
            prospect = {
                'id': row[0],
                'url': row[1],
                'organization_name': row[2],
                'emails': json.loads(row[3]),
                'phones': json.loads(row[4]),
                'addresses': json.loads(row[5]),
                'sustainability_score': row[7],
                'donation_probability': row[8],
                'engagement_score': row[9],
                'final_score': row[10]
            }
            prospects.append(prospect)
        
        return prospects

    def run_intelligent_campaign(self, campaign_description, max_organizations=5):
        self.logger.info(f"Starting intelligent donor acquisition campaign")
        
        prompt = f"""
        Find {max_organizations} organizations that would be interested in supporting environmental initiatives, 
        specifically beach cleanup and ocean conservation using AI technology. 
        Focus on: {campaign_description}
        
        Look for organizations that:
        - Have sustainability or environmental programs
        - Show corporate social responsibility
        - Are mid-sized companies or foundations
        - Have public contact information
        
        Return only the URLs with https:// protocol.
        """
        
        urls = self.get_intelligent_urls(prompt)
        self.logger.info(f"Found {len(urls)} potential organizations to analyze")
        
        results = []
        for url in urls[:max_organizations]:
            self.logger.info(f"Analyzing: {url}")
            prospect_data = self.crawl_intelligent_website(url)
            self.save_prospect(prospect_data)
            results.append(prospect_data)
            
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results

if __name__ == "__main__":
    api_key = "your_openai_api_key_here"
    crawler = IntelligentDonorCrawler(api_key)
    
    campaign_description = """
    Second Life NGO uses AI-powered drone technology to identify and map plastic pollution 
    along coastlines and beaches. We're looking for corporate partners and foundations 
    interested in supporting innovative environmental technology solutions.
    """
    
    results = crawler.run_intelligent_campaign(campaign_description, max_organizations=3)
    
    print("\n=== TOP PROSPECTS ===")
    for i, prospect in enumerate(results, 1):
        print(f"\n{i}. {prospect['organization_name']}")
        print(f"   URL: {prospect['url']}")
        print(f"   Final Score: {prospect['final_score']:.3f}")
        print(f"   Sustainability Score: {prospect['sustainability_score']:.3f}")
        print(f"   Donation Probability: {prospect['donation_probability']:.3f}")
        print(f"   Engagement Score: {prospect['engagement_score']:.3f}")
        print(f"   Emails: {prospect['emails']}")
        print(f"   Phones: {prospect['phones']}")
        print("-" * 60)

