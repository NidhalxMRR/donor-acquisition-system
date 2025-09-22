import os
import requests
import json
from typing import List, Dict, Any, Optional, Union

class AIClient:
    """
    Client unifié pour les APIs OpenAI et DeepSeek
    """
    
    def __init__(self, provider=None, api_key=None, api_base=None):
        """
        Initialise le client AI
        
        Args:
            provider: Fournisseur d'API ('openai' ou 'deepseek')
            api_key: Clé API
            api_base: URL de base de l'API
        """
        # Déterminer le fournisseur
        self.provider = provider or os.getenv("AI_PROVIDER", "openai").lower()
        
        if self.provider not in ["openai", "deepseek"]:
            raise ValueError("Provider must be 'openai' or 'deepseek'")
        
        # Initialiser le client approprié
        if self.provider == "openai":
            self._init_openai(api_key, api_base)
        else:
            self._init_deepseek(api_key, api_base)
    
    def _init_openai(self, api_key=None, api_base=None):
        """Initialise le client OpenAI"""
        try:
            import openai
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            
            if not self.api_key:
                raise ValueError("OpenAI API key is required. Set it as OPENAI_API_KEY environment variable or pass it to the constructor.")
            
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.api_base)
            self.chat = self.client.chat
            self._is_native = True
            
        except ImportError:
            print("OpenAI package not found. Using custom implementation.")
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            
            if not self.api_key:
                raise ValueError("OpenAI API key is required. Set it as OPENAI_API_KEY environment variable or pass it to the constructor.")
            
            self.chat = OpenAICompatClient(self.api_key, self.api_base)
            self._is_native = False
    
    def _init_deepseek(self, api_key=None, api_base=None):
        """Initialise le client DeepSeek"""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set it as DEEPSEEK_API_KEY environment variable or pass it to the constructor.")
        
        self.chat = DeepSeekCompatClient(self.api_key, self.api_base)
        self._is_native = False
    
    def is_native_client(self):
        """Vérifie si le client est natif ou une implémentation personnalisée"""
        return self._is_native


class OpenAICompatClient:
    """
    Client compatible avec l'API OpenAI
    """
    
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base
        self.completions = self
    
    def create(self, 
               model: str = "gpt-3.5-turbo", 
               messages: List[Dict[str, str]] = None,
               temperature: float = 0.7,
               max_tokens: int = 1000,
               top_p: float = 1.0,
               frequency_penalty: float = 0.0,
               presence_penalty: float = 0.0,
               stop: Optional[Union[str, List[str]]] = None) -> Dict[str, Any]:
        """
        Crée une complétion de chat
        """
        if not messages:
            messages = [{"role": "user", "content": "Hello"}]
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
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
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            try:
                if response and response.text:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", str(e))
            except:
                pass
            
            return {
                "error": {
                    "message": error_msg,
                    "type": "api_error",
                    "code": response.status_code if response else 500
                }
            }


class DeepSeekCompatClient:
    """
    Client compatible avec l'API DeepSeek
    """
    
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base
        self.completions = self
    
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
        Crée une complétion de chat
        """
        if not messages:
            messages = [{"role": "user", "content": "Hello"}]
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
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
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            result = response.json()
            
            # Adapter le format si nécessaire (DeepSeek vers OpenAI)
            if "choices" not in result and "response" in result:
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
            error_msg = str(e)
            try:
                if response and response.text:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", str(e))
            except:
                pass
            
            return {
                "error": {
                    "message": error_msg,
                    "type": "api_error",
                    "code": response.status_code if response else 500
                }
            }


def update_project_files():
    """
    Met à jour les fichiers du projet pour utiliser le client AI unifié
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
            'from src.ai_client import AIClient',
            content
        )
        
        # Remplacer les utilisations
        content = re.sub(
            r'openai\.OpenAI\(api_key=([^)]+)\)',
            r'AIClient(api_key=\1)',
            content
        )
        
        # Remplacer les références au client
        content = re.sub(
            r'self\.client\s*=\s*openai\.OpenAI\(api_key=([^)]+)\)',
            r'self.client = AIClient(api_key=\1)',
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
        
        # Ajouter les variables DeepSeek et AI_PROVIDER
        if 'AI_PROVIDER' not in content:
            content = content.replace(
                'OPENAI_API_KEY=your_openai_api_key_here',
                '# AI Provider Configuration (openai or deepseek)\n'
                'AI_PROVIDER=openai\n\n'
                '# OpenAI Configuration\n'
                'OPENAI_API_KEY=your_openai_api_key_here\n'
                'OPENAI_API_BASE=https://api.openai.com/v1\n\n'
                '# DeepSeek Configuration\n'
                'DEEPSEEK_API_KEY=your_deepseek_api_key_here\n'
                'DEEPSEEK_API_BASE=https://api.deepseek.com/v1'
            )
            
            with open(env_example_path, 'w') as file:
                file.write(content)
            
            print(f"Modified: {env_example_path}")


if __name__ == "__main__":
    # Test du client
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY not set. Cannot test OpenAI client.")
        else:
            client = AIClient(provider="openai", api_key=api_key)
            print(f"Testing OpenAI client (native: {client.is_native_client()})...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, AI!"}],
                max_tokens=50
            )
            print(json.dumps(response, indent=2))
    
    elif provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("DEEPSEEK_API_KEY not set. Cannot test DeepSeek client.")
        else:
            client = AIClient(provider="deepseek", api_key=api_key)
            print("Testing DeepSeek client...")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Hello, AI!"}],
                max_tokens=50
            )
            print(json.dumps(response, indent=2))
    
    # Mettre à jour les fichiers du projet
    update_project_files()

