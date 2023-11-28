# Quiz

## Description du projet

Vous voulez réviser pour préparer votre QCM dans la matière Full Stack Application ? Cette application est faite pour vous !!
Toutes les questions essentielles pour vérifier vos connaissances et avoir 20 à cette unité !
Satisfait ou remboursé !


## Guide utilisateur

### Installation de Git et récupération des fichiers

Pour avoir un bon fonctionnement du projet, il faut vérifier que vous avez bien installé [Git](https://git-scm.com/) sur votre espace de travail afin de récupérer les fichiers.
Ensuite, il faut cloner le repository dans le dossier local souhaité en utilisant la commande `git clone https://github.com/mercierju/QuizAppFullStack.git` afin d'avoir accès au répertoire.

Le code s'organise en plusieurs conteneurs, permettant de gérer des fonctionnalités différentes. Il vous faudra donc vérifier que vous avez bien installé Docker.

Une fois le repository cloné sur votre machine, il faudra exécuter la commande `docker compose up -d` à la racine du projet. Cela va construire les conteneurs nécessaires au fonctionnement de l'application ainsi que les démarrer s'ils n'ont pas déjà été créés auparavant. 
Pour démarrer les conteneurs s'ils ont déjà été créés, il faudra exécuter la même commande.

Pour voir le dashboard, il faut aller sur votre navigateur et mettre `http://localhost:3000/`. 


### Les données utilisées

Les données que nous utilisons proviennent soit d'une injection initiale lors du démarrage de l'application dans la base de données, soit de données générées par les utilisateurs. Lorsque l'application démarre, nous vérifions si la base de données est vide, auquel cas nous la peuplons avec des questions et leurs réponses correspondantes. Nous ajoutons également un utilisateur avec son score pour simuler une participation antérieure à celle de l'utilisateur.

Concernant les données générées par les utilisateurs, elles comprennent le score obtenu au quiz ainsi que l'utilisateur lui-même, que nous ajoutons à la base de données s'il n'est pas déjà présent. À chaque participation au quiz, nous mettons à jour son meilleur score s'il dépasse le score précédent.

### Les paquets à utiliser

Des paquets sont nécessaires pour le bon fonctionnement du projet, ils sont dans les fichiers requirements.txt, et sont automatiquement installés dans les conteneurs correspondants lors de leur création.


### Fonctionnement du projet

Le projet se compose de trois éléments principaux :

- Une base de données PostgreSQL pour le stockage des données.
- L'interface utilisateur (front-end) qui affiche l'application de manière esthétique, présentant les données de manière compréhensible.
- Le serveur back-end, responsable de la gestion de la base de données et de la liaison avec le front-end pour la transmission des données.


Mais concrètement, comment ça marche ?

Lorsque notre application est lancée pour la première fois, nous procédons à l'ajout des données nécessaires au fonctionnement, telles que des questions/réponses et un utilisateur de test, dans la base de données. Ces opérations sont effectuées côté back-end.

Une fois la base de données complétée, le tableau des scores peut être affiché sur la page d'accueil, bien que pour l'instant il ne comporte qu'un seul utilisateur. Lorsqu'un utilisateur clique sur le bouton "Commencer le quiz", deux scénarios se présentent : soit il est déjà authentifié sur l'application et est redirigé vers le quiz, soit il ne l'est pas et doit d'abord s'authentifier. La gestion des utilisateurs revêt ici une importance cruciale, permettant d'attribuer des participations à des utilisateurs spécifiques et de maintenir un classement des meilleurs scores pour chaque utilisateur. L'authentification est gérée de manière externe par Clerk, simplifiant le processus avec une seule authentification.

Nous avons initialement tenté d'utiliser un webhook de Clerk pour ajouter automatiquement les utilisateurs à la base de données PostgreSQL dès leur création sur Clerk. Cependant, face à plusieurs échecs, nous avons opté pour une approche différente. Nous récupérons les données de l'utilisateur de la session en cours, et si cet utilisateur envoie une participation alors qu'il n'est pas encore dans la base de données, nous l'ajoutons. S'il existe déjà, nous vérifions simplement si son nouveau score est supérieur à celui enregistré précédemment.


## Model de données 

- Users : Contient les informations relatives aux utilisateurs.
Colonnes : id, username, clerk_id, best_score.

- Questions : Enregistre les questions du quiz.
Colonnes : id, question_text, position (indiquant la position de la question dans le quiz).

- Choices : Stocke les différentes options de réponse associées à chaque question du QCM.
Colonnes : id, choice_text, is_correct, question_id (permettant de lier le choix à la question correspondante).

- Participation :Rassemble les résultats du QCM réalisé par les utilisateurs.
Colonnes : id, clerk_id (identifiant l'utilisateur), score.

## Quide développeur

Le projet est divisé en 3 conteneurs : le front, le back, et la base de données.

La base de données PosgreSQL nous servira à stocker les données.

Le front sert à afficher les données et a rendre l'application agréable a utiliser :
- page d'accueil : `index.js` et `index.html`
- authentification des utilisateurs avec Clerk : `clerk-auth.js` et `clerk-auth.html`
- page du quiz : `quiz.js` et `quiz.html`
- page des résultats : `result.js` et `result.html`
- style de l'application : `global.css`
- barre de navigation : `navbar.html` et `navbar.css`
- le Dockerfile de ce conteneur : `Dockerfile`

Le fichier HTML définit la structure et le contenu de la page web, le fichier CSS stylise et formate l'apparence de la page, tandis que le fichier JavaScript gère la logique et l'interactivité, permettant des modifications dynamiques du contenu et de la présentation.


Le back sert à :
- définition des requêtes FastApi et remplissage de la bdd : `main.py`
- initialisation de la bdd : `database.py`
- définition du model de donnée : `models.py`
- les requirements pour ce conteneur : `requirements.txt`
- le Dockerfile de ce container : `Dockerfile`

La configuration permettant d'initialiser et de lancer le projet est stockée dans le fichier : `docker-compose.yml` se situant a la racine du projet.

