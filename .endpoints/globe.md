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


## Endpoints Escape Game

### Gestion des jeux d'évasion

- **GET /api/escapegame/escape-rooms/** - Liste tous les jeux d'évasion disponibles
- **GET /api/escapegame/escape-rooms/id/** - Détails d'un jeu d'évasion spécifique
- **POST /api/escapegame/escape-rooms/** - Crée un nouveau jeu d'évasion (admin uniquement)
- **PUT /api/escapegame/escape-rooms/id/** - Met à jour un jeu d'évasion (admin uniquement)
- **DELETE /api/escapegame/escape-rooms/id/** - Supprime un jeu d'évasion (admin uniquement)
- **GET /api/escapegame/escape-rooms/featured/** - Liste les jeux d'évasion mis en avant


### Pièces

- **GET /api/escapegame/rooms/** - Liste toutes les pièces
- **GET /api/escapegame/rooms/id/** - Détails d'une pièce spécifique
- **GET /api/escapegame/escape-rooms/escape_room_id/rooms/** - Pièces pour un jeu d'évasion spécifique
- **POST /api/escapegame/rooms/** - Crée une nouvelle pièce (admin uniquement)
- **PUT /api/escapegame/rooms/id/** - Met à jour une pièce (admin uniquement)


### Connexions entre pièces

- **GET /api/escapegame/room-connections/** - Liste toutes les connexions
- **GET /api/escapegame/room-connections/id/** - Détails d'une connexion spécifique
- **GET /api/escapegame/rooms/room_id/connections/** - Connexions pour une pièce spécifique
- **POST /api/escapegame/room-connections/** - Crée une nouvelle connexion (admin uniquement)


### Énigmes

- **GET /api/escapegame/puzzles/** - Liste toutes les énigmes
- **GET /api/escapegame/puzzles/id/** - Détails d'une énigme spécifique
- **GET /api/escapegame/rooms/room_id/puzzles/** - Énigmes pour une pièce spécifique
- **POST /api/escapegame/puzzles/** - Crée une nouvelle énigme (admin uniquement)
- **PUT /api/escapegame/puzzles/id/** - Met à jour une énigme (admin uniquement)
- **POST /api/escapegame/puzzles/id/solve/** - Tente de résoudre une énigme


### Objets d'inventaire

- **GET /api/escapegame/inventory-items/** - Liste tous les objets
- **GET /api/escapegame/inventory-items/id/** - Détails d'un objet spécifique
- **GET /api/escapegame/escape-rooms/escape_room_id/inventory-items/** - Objets pour un jeu d'évasion
- **POST /api/escapegame/inventory-items/** - Crée un nouvel objet (admin uniquement)
- **PUT /api/escapegame/inventory-items/id/** - Met à jour un objet (admin uniquement)


### Emplacements d'objets

- **GET /api/escapegame/item-locations/** - Liste tous les emplacements d'objets
- **GET /api/escapegame/item-locations/id/** - Détails d'un emplacement spécifique
- **GET /api/escapegame/rooms/room_id/item-locations/** - Emplacements dans une pièce
- **POST /api/escapegame/item-locations/** - Crée un nouvel emplacement (admin uniquement)


### Sessions de jeu

- **GET /api/escapegame/game-sessions/** - Liste les sessions de l'utilisateur connecté
- **GET /api/escapegame/game-sessions/id/** - Détails d'une session spécifique
- **POST /api/escapegame/escape-rooms/escape_room_id/start/** - Démarre une nouvelle session
- **PUT /api/escapegame/game-sessions/id/save/** - Sauvegarde l'état d'une session
- **GET /api/escapegame/game-sessions/active/** - Obtient la session active de l'utilisateur
- **POST /api/escapegame/game-sessions/id/end/** - Termine une session


### Événements de jeu

- **GET /api/escapegame/game-events/** - Liste les événements de l'utilisateur
- **GET /api/escapegame/game-events/id/** - Détails d'un événement spécifique
- **POST /api/escapegame/game-events/** - Enregistre un nouvel événement
- **GET /api/escapegame/game-sessions/session_id/events/** - Événements d'une session


### Indices

- **GET /api/escapegame/hints/** - Liste tous les indices
- **GET /api/escapegame/hints/id/** - Détails d'un indice spécifique
- **GET /api/escapegame/puzzles/puzzle_id/hints/** - Indices pour une énigme
- **POST /api/escapegame/puzzles/puzzle_id/request-hint/** - Demande un indice


### Statistiques et progression

- **GET /api/escapegame/user-stats/** - Statistiques de l'utilisateur
- **GET /api/escapegame/escape-rooms/escape_room_id/leaderboard/** - Classement pour un jeu d'évasion
- **GET /api/escapegame/user-progress/** - Progression globale de l'utilisateur