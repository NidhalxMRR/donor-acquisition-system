# Guide d'utilisation des fournisseurs d'API IA

Le système d'acquisition de donateurs par IA est conçu pour fonctionner avec différents fournisseurs d'API d'intelligence artificielle. Actuellement, il prend en charge :

1. **OpenAI** (par défaut)
2. **DeepSeek**

Ce guide explique comment configurer et basculer entre ces différents fournisseurs.

## Configuration de base

La configuration se fait principalement via des variables d'environnement dans le fichier `.env` :

```
# Choix du fournisseur d'API IA (openai ou deepseek)
AI_PROVIDER=openai

# Configuration OpenAI
OPENAI_API_KEY=votre_clé_api_openai
OPENAI_API_BASE=https://api.openai.com/v1

# Configuration DeepSeek
DEEPSEEK_API_KEY=votre_clé_api_deepseek
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

## Utilisation d'OpenAI (par défaut)

Pour utiliser OpenAI :

1. Obtenez une clé API sur [platform.openai.com](https://platform.openai.com)
2. Configurez votre fichier `.env` :
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=votre_clé_api_openai
   ```
3. Les modèles recommandés sont :
   - `gpt-3.5-turbo` (bon équilibre performance/coût)
   - `gpt-4` (meilleure qualité mais plus coûteux)

## Utilisation de DeepSeek

Pour utiliser DeepSeek :

1. Obtenez une clé API sur [deepseek.ai](https://deepseek.ai)
2. Configurez votre fichier `.env` :
   ```
   AI_PROVIDER=deepseek
   DEEPSEEK_API_KEY=votre_clé_api_deepseek
   ```
3. Les modèles recommandés sont :
   - `deepseek-chat` (modèle général)
   - `deepseek-coder` (pour les tâches liées au code)

## Modification des modèles utilisés

Si vous souhaitez modifier les modèles utilisés par défaut, vous pouvez éditer les fichiers suivants :

- `src/intelligent_donor_crawler.py`
- `src/ai_scoring_engine.py`
- `src/personalized_outreach.py`

Recherchez les appels à `client.chat.completions.create` et modifiez le paramètre `model`.

## Comparaison des performances

| Fournisseur | Avantages | Inconvénients |
|-------------|-----------|---------------|
| **OpenAI**  | - Excellente qualité de réponse<br>- Documentation complète<br>- Stable et fiable | - Plus coûteux<br>- Limites de rate plus strictes |
| **DeepSeek**| - Généralement moins cher<br>- Bonne qualité pour les tâches générales<br>- Moins de restrictions | - Documentation plus limitée<br>- Moins de fonctionnalités avancées |

## Dépannage

### Problèmes avec OpenAI

1. **Erreur d'authentification** : Vérifiez que votre clé API est correcte et active
2. **Limites de rate** : Ajoutez une logique de retry avec backoff exponentiel
3. **Coûts élevés** : Utilisez des modèles moins coûteux comme `gpt-3.5-turbo`

### Problèmes avec DeepSeek

1. **Format de réponse** : Le client AI unifié normalise les réponses, mais certaines différences subtiles peuvent persister
2. **Disponibilité** : L'API DeepSeek peut avoir une disponibilité différente selon les régions

## Ajout de nouveaux fournisseurs

Pour ajouter un nouveau fournisseur d'API :

1. Modifiez `src/ai_client.py` pour ajouter une nouvelle classe compatible
2. Ajoutez la logique d'initialisation dans la classe `AIClient`
3. Mettez à jour le fichier `.env.example` avec les nouvelles variables

## Recommandations

- Commencez avec OpenAI pour la fiabilité et la qualité
- Testez DeepSeek pour réduire les coûts si votre cas d'utilisation le permet
- Gardez les deux configurations dans votre fichier `.env` pour pouvoir basculer facilement

