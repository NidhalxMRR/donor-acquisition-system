import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import sqlite3
import json
from datetime import datetime
import re
import openai

class AIProspectScoringEngine:
    def __init__(self, api_key, db_path="donor_prospects.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=api_key)
        self.models = {}
        self.scalers = {}
        self.vectorizers = {}
        self.feature_importance = {}
        
    def extract_advanced_features(self, prospect_data):
        features = {}
        
        text = prospect_data.get('content_text', '')
        emails = prospect_data.get('emails', [])
        phones = prospect_data.get('phones', [])
        url = prospect_data.get('url', '')
        
        features['email_count'] = len(emails)
        features['phone_count'] = len(phones)
        features['has_contact_info'] = 1 if (emails or phones) else 0
        
        domain_indicators = {
            'org_domain': 1 if '.org' in url else 0,
            'com_domain': 1 if '.com' in url else 0,
            'edu_domain': 1 if '.edu' in url else 0,
            'gov_domain': 1 if '.gov' in url else 0
        }
        features.update(domain_indicators)
        
        sustainability_keywords = [
            'sustainability', 'sustainable', 'environment', 'environmental', 'green', 'eco',
            'climate', 'carbon', 'renewable', 'clean energy', 'conservation', 'biodiversity',
            'ocean', 'marine', 'beach', 'coastal', 'pollution', 'waste', 'recycling'
        ]
        
        donation_keywords = [
            'donate', 'donation', 'support', 'contribute', 'fund', 'sponsor',
            'philanthropy', 'charity', 'giving', 'grant', 'foundation', 'csr',
            'corporate social responsibility', 'impact investing'
        ]
        
        technology_keywords = [
            'technology', 'innovation', 'ai', 'artificial intelligence', 'machine learning',
            'drone', 'automation', 'digital', 'tech', 'startup', 'research'
        ]
        
        text_lower = text.lower()
        
        features['sustainability_mentions'] = sum(text_lower.count(kw) for kw in sustainability_keywords)
        features['donation_mentions'] = sum(text_lower.count(kw) for kw in donation_keywords)
        features['technology_mentions'] = sum(text_lower.count(kw) for kw in technology_keywords)
        
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        
        financial_indicators = re.findall(r'\$[\d,]+(?:\.\d{2})?[kmb]?', text_lower)
        features['financial_mentions'] = len(financial_indicators)
        
        partnership_keywords = ['partner', 'collaboration', 'alliance', 'network', 'member']
        features['partnership_mentions'] = sum(text_lower.count(kw) for kw in partnership_keywords)
        
        award_keywords = ['award', 'recognition', 'certified', 'accredited', 'winner']
        features['award_mentions'] = sum(text_lower.count(kw) for kw in award_keywords)
        
        return features
    
    def generate_llm_insights(self, prospect_data):
        try:
            prompt = f"""
            Analyze this organization for potential donation likelihood to an environmental NGO that uses AI for beach cleanup:
            
            Organization: {prospect_data.get('organization_name', 'Unknown')}
            Website: {prospect_data.get('url', '')}
            Content sample: {prospect_data.get('content_text', '')[:1000]}
            
            Rate from 0-10:
            1. Environmental alignment
            2. Technology interest  
            3. Donation capacity
            4. Partnership potential
            
            Respond with only numbers separated by commas (e.g., "7,8,6,9").
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            scores_text = response.choices[0].message.content.strip()
            scores = [float(x.strip()) for x in scores_text.split(',')]
            
            return {
                'llm_environmental_score': scores[0] / 10 if len(scores) > 0 else 0.5,
                'llm_technology_score': scores[1] / 10 if len(scores) > 1 else 0.5,
                'llm_capacity_score': scores[2] / 10 if len(scores) > 2 else 0.5,
                'llm_partnership_score': scores[3] / 10 if len(scores) > 3 else 0.5
            }
        except Exception as e:
            return {
                'llm_environmental_score': 0.5,
                'llm_technology_score': 0.5,
                'llm_capacity_score': 0.5,
                'llm_partnership_score': 0.5
            }
    
    def create_training_data(self):
        positive_examples = [
            {
                'content_text': 'Our foundation supports environmental technology initiatives and sustainable innovation projects. We have donated over $2M to clean energy startups and ocean conservation programs.',
                'emails': ['contact@greenfund.org'],
                'phones': ['+1-555-0123'],
                'url': 'https://greenfund.org',
                'organization_name': 'Green Innovation Fund',
                'label': 1
            },
            {
                'content_text': 'TechCorp is committed to corporate social responsibility and environmental sustainability. We partner with NGOs on climate technology solutions and have an annual CSR budget of $5M.',
                'emails': ['csr@techcorp.com'],
                'phones': ['+1-555-0456'],
                'url': 'https://techcorp.com',
                'organization_name': 'TechCorp Industries',
                'label': 1
            },
            {
                'content_text': 'EcoFoundation focuses on marine conservation and ocean cleanup initiatives. We support innovative approaches to environmental challenges including AI and drone technology.',
                'emails': ['grants@ecofoundation.org'],
                'phones': ['+1-555-0789'],
                'url': 'https://ecofoundation.org',
                'organization_name': 'Eco Foundation',
                'label': 1
            }
        ]
        
        negative_examples = [
            {
                'content_text': 'Welcome to our restaurant! We serve the best pizza in town. Check out our menu and make a reservation today.',
                'emails': ['info@pizzaplace.com'],
                'phones': ['+1-555-1111'],
                'url': 'https://pizzaplace.com',
                'organization_name': 'Pizza Palace',
                'label': 0
            },
            {
                'content_text': 'Personal blog about my daily life and thoughts. No business or organizational content here.',
                'emails': ['john@personalblog.com'],
                'phones': [],
                'url': 'https://johnsblog.com',
                'organization_name': 'Johns Blog',
                'label': 0
            }
        ]
        
        return positive_examples + negative_examples
    
    def prepare_features(self, data):
        features_list = []
        texts = []
        
        for item in data:
            basic_features = self.extract_advanced_features(item)
            llm_features = self.generate_llm_insights(item)
            
            combined_features = {**basic_features, **llm_features}
            features_list.append(combined_features)
            texts.append(item.get('content_text', ''))
        
        features_df = pd.DataFrame(features_list)
        
        if 'text_vectorizer' not in self.vectorizers:
            self.vectorizers['text_vectorizer'] = TfidfVectorizer(
                max_features=100, 
                stop_words='english',
                ngram_range=(1, 2)
            )
            text_features = self.vectorizers['text_vectorizer'].fit_transform(texts)
        else:
            text_features = self.vectorizers['text_vectorizer'].transform(texts)
        
        text_feature_names = [f'text_feature_{i}' for i in range(text_features.shape[1])]
        text_df = pd.DataFrame(text_features.toarray(), columns=text_feature_names)
        
        final_features = pd.concat([features_df, text_df], axis=1)
        
        if 'feature_scaler' not in self.scalers:
            self.scalers['feature_scaler'] = StandardScaler()
            scaled_features = self.scalers['feature_scaler'].fit_transform(final_features)
        else:
            scaled_features = self.scalers['feature_scaler'].transform(final_features)
        
        return scaled_features, final_features.columns.tolist()
    
    def train_models(self):
        training_data = self.create_training_data()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prospects')
        db_data = cursor.fetchall()
        conn.close()
        
        for row in db_data:
            prospect = {
                'content_text': row[6],
                'emails': json.loads(row[3]),
                'phones': json.loads(row[4]),
                'url': row[1],
                'organization_name': row[2],
                'label': 1 if row[10] > 0.6 else 0
            }
            training_data.append(prospect)
        
        if len(training_data) < 5:
            print("Insufficient training data. Using synthetic examples only.")
        
        X, feature_names = self.prepare_features(training_data)
        y = np.array([item['label'] for item in training_data])
        
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            class_weight='balanced'
        )
        
        self.models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42
        )
        
        self.models['logistic_regression'] = LogisticRegression(
            random_state=42,
            class_weight='balanced'
        )
        
        for name, model in self.models.items():
            model.fit(X, y)
            
            if hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(feature_names, model.feature_importances_))
                self.feature_importance[name] = sorted(
                    importance_dict.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]
        
        print("Models trained successfully!")
        return True
    
    def score_prospect(self, prospect_data):
        if not self.models:
            self.train_models()
        
        X, _ = self.prepare_features([prospect_data])
        
        scores = {}
        probabilities = {}
        
        for name, model in self.models.items():
            try:
                prob = model.predict_proba(X)[0]
                scores[name] = prob[1] if len(prob) > 1 else prob[0]
                probabilities[name] = prob.tolist()
            except Exception as e:
                scores[name] = 0.5
                probabilities[name] = [0.5, 0.5]
        
        ensemble_score = np.mean(list(scores.values()))
        
        confidence = 1 - np.std(list(scores.values()))
        
        return {
            'ensemble_score': ensemble_score,
            'individual_scores': scores,
            'confidence': confidence,
            'recommendation': self.get_recommendation(ensemble_score, confidence)
        }
    
    def get_recommendation(self, score, confidence):
        if score >= 0.8 and confidence >= 0.7:
            return "HIGH_PRIORITY"
        elif score >= 0.6 and confidence >= 0.5:
            return "MEDIUM_PRIORITY"
        elif score >= 0.4:
            return "LOW_PRIORITY"
        else:
            return "NOT_RECOMMENDED"
    
    def batch_score_prospects(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prospects')
        prospects = cursor.fetchall()
        
        scored_prospects = []
        
        for row in prospects:
            prospect_data = {
                'content_text': row[6],
                'emails': json.loads(row[3]),
                'phones': json.loads(row[4]),
                'url': row[1],
                'organization_name': row[2]
            }
            
            scoring_result = self.score_prospect(prospect_data)
            
            scored_prospect = {
                'id': row[0],
                'organization_name': row[2],
                'url': row[1],
                'ai_score': scoring_result['ensemble_score'],
                'confidence': scoring_result['confidence'],
                'recommendation': scoring_result['recommendation'],
                'individual_scores': scoring_result['individual_scores']
            }
            
            scored_prospects.append(scored_prospect)
        
        conn.close()
        
        scored_prospects.sort(key=lambda x: x['ai_score'], reverse=True)
        return scored_prospects
    
    def save_model(self, filepath="ai_scoring_model.pkl"):
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'vectorizers': self.vectorizers,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath="ai_scoring_model.pkl"):
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.vectorizers = model_data['vectorizers']
            self.feature_importance = model_data['feature_importance']
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

if __name__ == "__main__":
    api_key = "your_openai_api_key_here"
    scoring_engine = AIProspectScoringEngine(api_key)
    
    scoring_engine.train_models()
    
    scored_prospects = scoring_engine.batch_score_prospects()
    
    print("\n=== AI SCORING RESULTS ===")
    for prospect in scored_prospects[:5]:
        print(f"\nOrganization: {prospect['organization_name']}")
        print(f"AI Score: {prospect['ai_score']:.3f}")
        print(f"Confidence: {prospect['confidence']:.3f}")
        print(f"Recommendation: {prospect['recommendation']}")
        print(f"URL: {prospect['url']}")
        print("-" * 50)
    
    scoring_engine.save_model()

