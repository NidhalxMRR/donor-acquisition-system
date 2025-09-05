import os
import requests
import json
from typing import List, Dict, Any, Optional, Union

class DeepSeekClient:
    """
    Client pour l'API DeepSeek, compatible avec l'interface OpenAI
    """
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """
        Initialise le client DeepSeek
        
        Args:
            api_key: Clé API DeepSeek (par défaut: variable d'environnement DEEPSEEK_API_KEY)
            api_base: URL de base de l'API (par défaut: https://api.deepseek.com/v1)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set it as DEEPSEEK_API_KEY environment variable or pass it to the constructor.")
        
        # Créer une structure similaire à celle du client OpenAI
        self.chat = ChatCompletions(self.api_key, self.api_base)

class ChatCompletions:
    """
    Classe pour gérer les completions de chat, similaire à l'interface OpenAI
    """
    
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
    
    def create(self, 
               model: str = "deepseek-chat", 
               messages: List[Dict[str, str]] = None,
               temperature: float = 0.7,
               max_tokens: int = 1000,
               top_p: float = 1.0,
               frequency_penalty: float = 0.0,
               presence_penalty: float = 0.0,
               stop: Optional[Union[str, List[str]]] = None) -> Dict[str, Any]:
        """
        Crée une complétion de chat, interface compatible avec OpenAI
        
        Args:
            model: Modèle à utiliser (par défaut: deepseek-chat)
            messages: Liste de messages pour la conversation
            temperature: Température pour la génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens à générer
            top_p: Valeur top_p pour la génération
            frequency_penalty: Pénalité de fréquence
            presence_penalty: Pénalité de présence
            stop: Séquence(s) d'arrêt
            
        Returns:
            Dictionnaire contenant la réponse formatée comme celle d'OpenAI
        """
        if not messages:
            messages = [{"role": "user", "content": "Hello"}]
        
        # Construire l'URL de l'endpoint
        url = f"{self.api_base}/chat/completions"
        
        # Préparer les headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Préparer les données
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        if stop:
            data["stop"] = stop
        
        # Faire la requête
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            # Formater la réponse pour qu'elle ressemble à celle d'OpenAI
            result = response.json()
            
            # Adapter le format si nécessaire
            if "choices" not in result and "response" in result:
                # Format DeepSeek vers format OpenAI
                formatted_result = {
                    "id": result.get("id", "deepseek-response"),
                    "object": "chat.completion",
                    "created": result.get("created", 0),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": result.get("response", "")
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": result.get("usage", {})
                }
                return formatted_result
            
            return result
            
        except requests.exceptions.RequestException as e:
            # Gérer les erreurs et formater une réponse d'erreur compatible
            error_msg = str(e)
            try:
                if response and response.text:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", str(e))
            except:
                pass
            
            # Créer une structure d'erreur similaire à OpenAI
            return {
                "error": {
                    "message": error_msg,
                    "type": "deepseek_error",
                    "code": response.status_code if response else 500
                }
            }

def replace_openai_with_deepseek():
    """
    Remplace l'importation d'OpenAI par DeepSeek dans les fichiers du projet
    """
    import os
    import re
    from pathlib import Path
    
    # Fichiers à modifier
    files_to_modify = [
        "intelligent_donor_crawler.py",
        "ai_scoring_engine.py",
        "personalized_outreach.py"
    ]
    
    # Chemin du répertoire source
    src_dir = Path(__file__).parent
    
    for filename in files_to_modify:
        file_path = src_dir / filename
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
        
        # Lire le contenu du fichier
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Remplacer les importations
        content = re.sub(
            r'import openai',
            'from src.deepseek_integration import DeepSeekClient as OpenAI',
            content
        )
        
        # Remplacer les utilisations
        content = re.sub(
            r'openai\.OpenAI\(api_key=([^)]+)\)',
            r'OpenAI(api_key=\1)',
            content
        )
        
        # Remplacer les références à l'environnement
        content = re.sub(
            r'OPENAI_API_KEY',
            'DEEPSEEK_API_KEY',
            content
        )
        
        # Écrire le contenu modifié
        with open(file_path, 'w') as file:
            file.write(content)
        
        print(f"Modified: {file_path}")
    
    # Mettre à jour le fichier .env.example
    env_example_path = src_dir.parent / '.env.example'
    if env_example_path.exists():
        with open(env_example_path, 'r') as file:
            content = file.read()
        
        # Ajouter les variables DeepSeek
        if 'DEEPSEEK_API_KEY' not in content:
            content = content.replace(
                'OPENAI_API_KEY=your_openai_api_key_here',
                'OPENAI_API_KEY=your_openai_api_key_here\n'
                'DEEPSEEK_API_KEY=your_deepseek_api_key_here\n'
                'DEEPSEEK_API_BASE=https://api.deepseek.com/v1'
            )
            
            with open(env_example_path, 'w') as file:
                file.write(content)
            
            print(f"Modified: {env_example_path}")

if __name__ == "__main__":
    # Test de l'intégration
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        client = DeepSeekClient(api_key)
        response = client.chat.create(
            messages=[{"role": "user", "content": "Hello, DeepSeek!"}],
            max_tokens=100
        )
        print(json.dumps(response, indent=2))
    else:
        print("DEEPSEEK_API_KEY not set. Please set it to test the integration.")
    
    # Remplacer OpenAI par DeepSeek dans les fichiers du projet
    replace_openai_with_deepseek()

