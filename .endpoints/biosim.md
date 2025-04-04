### Endpoints API pour BioSim et Escape Game

## Endpoints BioSim

### Gestion des expériences

- **GET /api/biosim/experiments/** - Liste toutes les expériences disponibles
- **GET /api/biosim/experiments/id/** - Détails d'une expérience spécifique
- **POST /api/biosim/experiments/** - Crée une nouvelle expérience (admin uniquement)
- **PUT /api/biosim/experiments/id/** - Met à jour une expérience (admin uniquement)
- **DELETE /api/biosim/experiments/id/** - Supprime une expérience (admin uniquement)
- **GET /api/biosim/experiments/featured/** - Liste les expériences mises en avant


### Variables d'expérience

- **GET /api/biosim/variables/** - Liste toutes les variables
- **GET /api/biosim/variables/id/** - Détails d'une variable spécifique
- **GET /api/biosim/experiments/experiment_id/variables/** - Variables pour une expérience spécifique
- **POST /api/biosim/variables/** - Crée une nouvelle variable (admin uniquement)
- **PUT /api/biosim/variables/id/** - Met à jour une variable (admin uniquement)


### Résultats de simulation

- **GET /api/biosim/results/** - Liste les résultats de l'utilisateur connecté
- **GET /api/biosim/results/id/** - Détails d'un résultat spécifique
- **POST /api/biosim/results/** - Enregistre un nouveau résultat de simulation
- **GET /api/biosim/experiments/experiment_id/results/** - Résultats pour une expérience spécifique
- **GET /api/biosim/results/stats/** - Statistiques sur les résultats de l'utilisateur


### Notes utilisateur

- **GET /api/biosim/notes/** - Liste les notes de l'utilisateur connecté
- **GET /api/biosim/notes/id/** - Détails d'une note spécifique
- **POST /api/biosim/notes/** - Crée une nouvelle note
- **PUT /api/biosim/notes/id/** - Met à jour une note
- **DELETE /api/biosim/notes/id/** - Supprime une note
- **GET /api/biosim/experiments/experiment_id/notes/** - Notes pour une expérience spécifique


### Réalisations

- **GET /api/biosim/achievements/** - Liste toutes les réalisations disponibles
- **GET /api/biosim/achievements/id/** - Détails d'une réalisation spécifique
- **GET /api/biosim/user-achievements/** - Réalisations débloquées par l'utilisateur
- **POST /api/biosim/user-achievements/unlock/achievement_id/** - Débloque une réalisation


### Préférences utilisateur

- **GET /api/biosim/preferences/** - Obtient les préférences de l'utilisateur
- **PUT /api/biosim/preferences/** - Met à jour les préférences de l'utilisateur

## Format des requêtes et réponses

Toutes les API renvoient et acceptent des données au format JSON. Voici un exemple de réponse pour une requête d'expérience BioSim :

```json
{
  "id": 1,
  "title": "Photosynthèse",
  "description": "Explorez le processus de photosynthèse dans les plantes",
  "difficulty": "MEDIUM",
  "subject": "BIOLOGY",
  "thumbnail_url": "/media/experiments/photosynthesis.jpg",
  "created_at": "2023-04-15T10:30:00Z",
  "updated_at": "2023-04-15T10:30:00Z",
  "is_featured": true,
  "variables": [
    {
      "id": 1,
      "name": "light_intensity",
      "display_name": "Intensité lumineuse",
      "min_value": 0,
      "max_value": 100,
      "default_value": 50,
      "unit": "lux"
    },
    {
      "id": 2,
      "name": "co2_level",
      "display_name": "Niveau de CO2",
      "min_value": 0,
      "max_value": 1000,
      "default_value": 400,
      "unit": "ppm"
    }
  ]
}
```

## Authentification

Toutes les API nécessitent une authentification, à l'exception de certains endpoints publics. L'authentification se fait via JWT (JSON Web Token) :

- **POST /api/token/** - Obtenir un token JWT (fournir username/password)
- **POST /api/token/refresh/** - Rafraîchir un token JWT expiré


Incluez le token dans l'en-tête HTTP de chaque requête :

```plaintext
Authorization: Bearer <votre_token_jwt>
```

Ces endpoints vous permettront d'intégrer complètement les fonctionnalités BioSim et Escape Game dans votre application frontend.