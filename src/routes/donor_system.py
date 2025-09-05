from flask import Blueprint, request, jsonify
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.intelligent_donor_crawler import IntelligentDonorCrawler
from src.ai_scoring_engine import AIProspectScoringEngine
from src.personalized_outreach import PersonalizedOutreachEngine
import sqlite3
import json
from datetime import datetime

donor_bp = Blueprint('donor', __name__)

API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'donor_prospects.db')

@donor_bp.route('/prospects', methods=['GET'])
def get_prospects():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, url, organization_name, emails, phones, addresses, 
                   sustainability_score, donation_probability, engagement_score, final_score
            FROM prospects 
            ORDER BY final_score DESC
        ''')
        
        prospects = []
        for row in cursor.fetchall():
            prospect = {
                'id': row[0],
                'url': row[1],
                'organization_name': row[2],
                'emails': json.loads(row[3]),
                'phones': json.loads(row[4]),
                'addresses': json.loads(row[5]),
                'sustainability_score': row[6],
                'donation_probability': row[7],
                'engagement_score': row[8],
                'final_score': row[9]
            }
            prospects.append(prospect)
        
        conn.close()
        return jsonify({'success': True, 'prospects': prospects})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/crawl', methods=['POST'])
def start_crawl():
    try:
        data = request.get_json()
        campaign_description = data.get('campaign_description', '')
        max_organizations = data.get('max_organizations', 3)
        
        crawler = IntelligentDonorCrawler(API_KEY, DB_PATH)
        results = crawler.run_intelligent_campaign(campaign_description, max_organizations)
        
        return jsonify({
            'success': True, 
            'message': f'Successfully crawled {len(results)} organizations',
            'results': results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/score', methods=['POST'])
def score_prospects():
    try:
        scoring_engine = AIProspectScoringEngine(API_KEY, DB_PATH)
        scored_prospects = scoring_engine.batch_score_prospects()
        
        return jsonify({
            'success': True,
            'scored_prospects': scored_prospects
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/outreach/generate', methods=['POST'])
def generate_outreach():
    try:
        data = request.get_json()
        prospect_id = data.get('prospect_id')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prospects WHERE id = ?', (prospect_id,))
        prospect_row = cursor.fetchone()
        conn.close()
        
        if not prospect_row:
            return jsonify({'success': False, 'error': 'Prospect not found'}), 404
        
        prospect_data = {
            'organization_name': prospect_row[2],
            'emails': json.loads(prospect_row[3]),
            'phones': json.loads(prospect_row[4]),
            'content_text': prospect_row[6],
            'sustainability_score': prospect_row[7]
        }
        
        outreach_engine = PersonalizedOutreachEngine(API_KEY, DB_PATH)
        
        email_content = outreach_engine.generate_personalized_email(prospect_data, {})
        social_content = outreach_engine.generate_social_media_content(prospect_data)
        call_script = outreach_engine.generate_call_script(prospect_data)
        
        return jsonify({
            'success': True,
            'email': email_content,
            'social_media': social_content,
            'call_script': call_script
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/outreach/campaign', methods=['POST'])
def create_campaign():
    try:
        data = request.get_json()
        prospect_id = data.get('prospect_id')
        sequence_type = data.get('sequence_type', 'standard')
        
        outreach_engine = PersonalizedOutreachEngine(API_KEY, DB_PATH)
        campaign_id = outreach_engine.schedule_outreach_campaign(prospect_id, sequence_type)
        
        if campaign_id:
            return jsonify({
                'success': True,
                'campaign_id': campaign_id,
                'message': 'Outreach campaign created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create campaign'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/outreach/tasks', methods=['GET'])
def get_outreach_tasks():
    try:
        outreach_engine = PersonalizedOutreachEngine(API_KEY, DB_PATH)
        tasks = outreach_engine.get_pending_outreach_tasks()
        
        formatted_tasks = []
        for task in tasks:
            formatted_task = {
                'id': task[0],
                'campaign_id': task[1],
                'step_number': task[2],
                'step_type': task[3],
                'scheduled_date': task[4],
                'content': task[5],
                'status': task[6],
                'prospect_id': task[8],
                'organization_name': task[9],
                'emails': json.loads(task[10]),
                'phones': json.loads(task[11])
            }
            formatted_tasks.append(formatted_task)
        
        return jsonify({
            'success': True,
            'tasks': formatted_tasks
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM prospects')
        total_prospects = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM prospects WHERE final_score > 0.7')
        high_priority = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(final_score) FROM prospects')
        avg_score = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT COUNT(*) FROM outreach_campaigns 
            WHERE status = "active"
        ''')
        active_campaigns = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_prospects': total_prospects,
                'high_priority_prospects': high_priority,
                'average_score': round(avg_score, 3),
                'active_campaigns': active_campaigns
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@donor_bp.route('/n8n/webhook', methods=['POST'])
def n8n_webhook():
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'start_crawl':
            campaign_description = data.get('campaign_description', '')
            max_organizations = data.get('max_organizations', 3)
            
            crawler = IntelligentDonorCrawler(API_KEY, DB_PATH)
            results = crawler.run_intelligent_campaign(campaign_description, max_organizations)
            
            return jsonify({
                'success': True,
                'results_count': len(results),
                'top_prospect': results[0] if results else None
            })
        
        elif action == 'score_prospects':
            scoring_engine = AIProspectScoringEngine(API_KEY, DB_PATH)
            scored_prospects = scoring_engine.batch_score_prospects()
            
            return jsonify({
                'success': True,
                'scored_count': len(scored_prospects),
                'top_scored': scored_prospects[:3] if scored_prospects else []
            })
        
        elif action == 'execute_outreach':
            task_id = data.get('task_id')
            outreach_engine = PersonalizedOutreachEngine(API_KEY, DB_PATH)
            success = outreach_engine.execute_outreach_task(task_id)
            
            return jsonify({
                'success': success,
                'message': 'Task executed' if success else 'Task not found'
            })
        
        else:
            return jsonify({'success': False, 'error': 'Unknown action'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

