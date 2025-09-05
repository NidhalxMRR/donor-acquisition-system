import openai
import sqlite3
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time

class PersonalizedOutreachEngine:
    def __init__(self, api_key, db_path="donor_prospects.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate_personalized_email(self, prospect_data, campaign_info):
        organization_name = prospect_data.get('organization_name', 'Organization')
        sustainability_score = prospect_data.get('sustainability_score', 0)
        content_sample = prospect_data.get('content_text', '')[:500]
        
        prompt = f"""
        Write a personalized email to {organization_name} for Second Life NGO.
        
        About Second Life NGO:
        - Uses AI-powered drone technology to identify and map plastic pollution on beaches
        - Converts waste data into actionable insights for cleanup operations
        - Partners with organizations for environmental impact and CSR initiatives
        
        About the prospect:
        - Organization: {organization_name}
        - Sustainability alignment: {sustainability_score:.2f}/1.0
        - Content insight: {content_sample}
        
        Email requirements:
        - Professional but warm tone
        - Highlight alignment with their values
        - Mention specific partnership opportunities
        - Include clear call-to-action
        - Keep under 200 words
        - Subject line and body
        
        Format as:
        SUBJECT: [subject line]
        BODY: [email body]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            email_content = response.choices[0].message.content.strip()
            
            if "SUBJECT:" in email_content and "BODY:" in email_content:
                parts = email_content.split("BODY:")
                subject = parts[0].replace("SUBJECT:", "").strip()
                body = parts[1].strip()
            else:
                subject = f"Partnership Opportunity: AI-Powered Beach Cleanup Initiative"
                body = email_content
            
            return {
                'subject': subject,
                'body': body,
                'personalization_score': self.calculate_personalization_score(body, prospect_data)
            }
            
        except Exception as e:
            return self.get_fallback_email(organization_name)
    
    def get_fallback_email(self, organization_name):
        return {
            'subject': f"Partnership Opportunity with Second Life NGO",
            'body': f"""Dear {organization_name} Team,

I hope this message finds you well. I'm reaching out from Second Life NGO, where we're revolutionizing beach cleanup through AI-powered drone technology.

Our innovative approach maps plastic pollution along coastlines, providing actionable data that makes cleanup efforts 300% more efficient. We're seeking forward-thinking partners who share our commitment to environmental sustainability.

Would you be interested in exploring how we could collaborate on this impactful initiative? I'd love to discuss partnership opportunities that align with your organization's values.

Best regards,
Second Life NGO Partnership Team""",
            'personalization_score': 0.3
        }
    
    def calculate_personalization_score(self, email_body, prospect_data):
        score = 0.5
        
        org_name = prospect_data.get('organization_name', '').lower()
        if org_name and org_name in email_body.lower():
            score += 0.2
        
        sustainability_keywords = ['sustainability', 'environmental', 'green', 'eco', 'climate']
        content = prospect_data.get('content_text', '').lower()
        
        for keyword in sustainability_keywords:
            if keyword in content and keyword in email_body.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def generate_social_media_content(self, prospect_data):
        organization_name = prospect_data.get('organization_name', 'Organization')
        
        prompt = f"""
        Create social media content to engage {organization_name} about Second Life NGO's AI beach cleanup technology.
        
        Generate:
        1. LinkedIn connection message (under 300 characters)
        2. Twitter mention (under 280 characters)
        3. LinkedIn post mentioning them (under 1300 characters)
        
        Focus on:
        - AI technology for environmental impact
        - Partnership opportunities
        - Shared values in sustainability
        
        Format as:
        LINKEDIN_MESSAGE: [message]
        TWITTER: [tweet]
        LINKEDIN_POST: [post]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            social_content = {}
            for platform in ['LINKEDIN_MESSAGE', 'TWITTER', 'LINKEDIN_POST']:
                if platform in content:
                    start = content.find(platform + ":") + len(platform + ":")
                    end = content.find("\n" + platform.split("_")[0], start) if "_" in platform else len(content)
                    social_content[platform.lower()] = content[start:end].strip()
            
            return social_content
            
        except Exception as e:
            return {
                'linkedin_message': f"Hi! I'd love to connect and share how Second Life NGO's AI technology is revolutionizing beach cleanup. Interested in environmental partnerships?",
                'twitter': f"@{organization_name.replace(' ', '')} Check out how AI drones are transforming beach cleanup! Partnership opportunities available. #AI #Sustainability",
                'linkedin_post': f"Excited to see organizations like {organization_name} leading in sustainability! At Second Life NGO, we're using AI-powered drones to map beach pollution and make cleanup 300% more efficient. Would love to explore collaboration opportunities!"
            }
    
    def create_outreach_sequence(self, prospect_data, sequence_type="standard"):
        sequences = {
            "standard": [
                {"day": 0, "type": "email", "template": "initial_outreach"},
                {"day": 7, "type": "linkedin", "template": "connection_request"},
                {"day": 14, "type": "email", "template": "follow_up"},
                {"day": 21, "type": "linkedin", "template": "value_add_post"},
                {"day": 30, "type": "email", "template": "final_follow_up"}
            ],
            "high_priority": [
                {"day": 0, "type": "email", "template": "initial_outreach"},
                {"day": 3, "type": "linkedin", "template": "connection_request"},
                {"day": 7, "type": "email", "template": "follow_up"},
                {"day": 10, "type": "phone", "template": "call_script"},
                {"day": 14, "type": "linkedin", "template": "value_add_post"},
                {"day": 21, "type": "email", "template": "partnership_proposal"}
            ],
            "low_priority": [
                {"day": 0, "type": "email", "template": "initial_outreach"},
                {"day": 14, "type": "linkedin", "template": "connection_request"},
                {"day": 30, "type": "email", "template": "follow_up"}
            ]
        }
        
        return sequences.get(sequence_type, sequences["standard"])
    
    def generate_call_script(self, prospect_data):
        organization_name = prospect_data.get('organization_name', 'Organization')
        
        prompt = f"""
        Create a phone call script for reaching out to {organization_name} about Second Life NGO partnership.
        
        Include:
        - Opening introduction (30 seconds)
        - Value proposition (45 seconds)
        - Question to engage them
        - Handling common objections
        - Clear next steps
        
        Keep professional but conversational.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"""
            OPENING: "Hi, this is [Name] from Second Life NGO. I'm calling because I noticed {organization_name}'s commitment to sustainability and thought you'd be interested in our AI-powered beach cleanup technology."
            
            VALUE PROP: "We use drones and AI to map plastic pollution on beaches, making cleanup efforts 300% more efficient. We're looking for partners who share our environmental mission."
            
            ENGAGEMENT: "Does environmental technology innovation align with your current initiatives?"
            
            NEXT STEPS: "Could we schedule a brief 15-minute call to explore potential collaboration?"
            """
    
    def schedule_outreach_campaign(self, prospect_id, sequence_type="standard"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prospects WHERE id = ?', (prospect_id,))
        prospect_row = cursor.fetchone()
        
        if not prospect_row:
            return False
        
        prospect_data = {
            'id': prospect_row[0],
            'url': prospect_row[1],
            'organization_name': prospect_row[2],
            'emails': json.loads(prospect_row[3]),
            'phones': json.loads(prospect_row[4]),
            'content_text': prospect_row[6],
            'sustainability_score': prospect_row[7],
            'final_score': prospect_row[10]
        }
        
        sequence = self.create_outreach_sequence(prospect_data, sequence_type)
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER,
                sequence_type TEXT,
                current_step INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO outreach_campaigns (prospect_id, sequence_type)
            VALUES (?, ?)
        ''', (prospect_id, sequence_type))
        
        campaign_id = cursor.lastrowid
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                step_number INTEGER,
                step_type TEXT,
                scheduled_date DATE,
                content TEXT,
                status TEXT DEFAULT 'pending',
                executed_at TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES outreach_campaigns (id)
            )
        ''')
        
        base_date = datetime.now()
        
        for i, step in enumerate(sequence):
            scheduled_date = base_date + timedelta(days=step['day'])
            
            if step['type'] == 'email':
                email_content = self.generate_personalized_email(prospect_data, {})
                content = json.dumps(email_content)
            elif step['type'] == 'linkedin':
                social_content = self.generate_social_media_content(prospect_data)
                content = json.dumps(social_content)
            elif step['type'] == 'phone':
                call_script = self.generate_call_script(prospect_data)
                content = call_script
            else:
                content = f"Execute {step['type']} outreach"
            
            cursor.execute('''
                INSERT INTO outreach_steps 
                (campaign_id, step_number, step_type, scheduled_date, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, i, step['type'], scheduled_date.date(), content))
        
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def get_pending_outreach_tasks(self, days_ahead=1):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        target_date = datetime.now().date() + timedelta(days=days_ahead)
        
        cursor.execute('''
            SELECT os.*, oc.prospect_id, p.organization_name, p.emails, p.phones
            FROM outreach_steps os
            JOIN outreach_campaigns oc ON os.campaign_id = oc.id
            JOIN prospects p ON oc.prospect_id = p.id
            WHERE os.scheduled_date <= ? AND os.status = 'pending'
            ORDER BY os.scheduled_date, os.step_number
        ''', (target_date,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        return tasks
    
    def execute_outreach_task(self, task_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM outreach_steps WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            return False
        
        cursor.execute('''
            UPDATE outreach_steps 
            SET status = 'executed', executed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def generate_campaign_report(self, campaign_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT oc.*, p.organization_name, p.final_score
            FROM outreach_campaigns oc
            JOIN prospects p ON oc.prospect_id = p.id
            WHERE oc.id = ?
        ''', (campaign_id,))
        
        campaign = cursor.fetchone()
        
        cursor.execute('''
            SELECT step_type, status, COUNT(*) as count
            FROM outreach_steps
            WHERE campaign_id = ?
            GROUP BY step_type, status
        ''', (campaign_id,))
        
        step_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'campaign_info': campaign,
            'step_statistics': step_stats
        }

if __name__ == "__main__":
    api_key = "your_openai_api_key_here"
    outreach_engine = PersonalizedOutreachEngine(api_key)
    
    sample_prospect = {
        'organization_name': 'Green Tech Foundation',
        'sustainability_score': 0.8,
        'content_text': 'We support innovative environmental technology solutions and sustainable development initiatives.',
        'emails': ['contact@greentech.org'],
        'phones': ['+1-555-0123']
    }
    
    email = outreach_engine.generate_personalized_email(sample_prospect, {})
    print("Generated Email:")
    print(f"Subject: {email['subject']}")
    print(f"Body: {email['body']}")
    print(f"Personalization Score: {email['personalization_score']}")
    
    social_content = outreach_engine.generate_social_media_content(sample_prospect)
    print("\nSocial Media Content:")
    for platform, content in social_content.items():
        print(f"{platform}: {content}")
    
    call_script = outreach_engine.generate_call_script(sample_prospect)
    print(f"\nCall Script:\n{call_script}")

