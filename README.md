"BarCoktail — Simulation asynchrone d’un bar"

_ BarCoktail est une simulation pédagogique écrite en Python (asyncio) illustrant le fonctionnement d’un bar : prise de commandes, préparation des boissons, service, coordination entre employés et gestion concurrente des ressources.

_ Le projet montre comment organiser plusieurs tâches coopérantes (producteurs/consommateurs) en utilisant des coroutines, des queues asynchrones, des verrous, et une boucle d’événements asyncio.

Sommaire

-Description

-Fonctionnalités

-Prérequis

-Installation

-Utilisation

-Exemples de fonctionnement

-Architecture

-Journalisation (logs)

-Limites et améliorations possibles

-Contribution


 Description

Le projet simule un petit bar organisé autour de :

Serveurs qui prennent les commandes des clients et servent les consommations

Un Bariste qui prépare les boissons à partir des post-it récupérés sur le Pic

Un Bar où sont déposées les commandes prêtes

Des Clients dont les commandes arrivent selon un timing défini dans un fichier texte

Les interactions reposent sur :

asyncio.Queue (gestion FIFO asynchrone)

asyncio.Lock (verrous pour éviter qu’un serveur commence deux tâches en même temps)

tâches concurrentes orchestrées via asyncio.gather

Le tout est accompagné d’un système de logging écrivant toutes les actions dans un fichier.

Fonctionnalités
✔ Gestion complète d’un flux de commandes

prise de commande par un ou plusieurs serveurs

empilement sur un Pic (file FIFO via asyncio.Queue)

préparation par le Bariste

dépôt au Bar

service au client

✔ Concurrence et coopération (asyncio)

tâches asynchrones pour chaque employé

file d’attente asynchrone

verrou individuel pour empêcher qu’un serveur fasse 2 choses en même temps

chaque employé possède une productivité variable (temps d’attente personnalisé)

✔ Bariste polyvalent

prépare les commandes du Pic

mais peut aussi aller servir directement quand le Pic est vide ( objectif final du projet)

✔ Plusieurs employés

plusieurs serveurs peuvent travailler en parallèle ( Ici on s'est limité à deux serveurs )

tout le monde partage les mêmes structures protégées

✔ Journalisation

toutes les actions sont enregistrées dans un fichier log horodaté

affichage conditionné par un paramètre verbose

Prérequis

Python 3.8+

Aucune dépendance externe

📦 Installation
git clone https://github.com/Prosper1325/BarCoktail.git
cd BarCoktail


(Optionnel) environnement virtuel :

python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

Utilisation

Le script principal est : BAR_ASYNCRO.py

En effet pour comprendre chaque étape du projet il faut exécuter tous les codes par ordre; par exemple le script BAR_REFAIT1_2.py  est le code de la partie I n°2 du projet, BAR_REFAIT3_1.py est le code de la partie III n°1 du projet.


Il s’exécute avec un fichier listant des commandes clients :

python BAR_ASYNCRO.py commandes.txt

📄 Exemple de format du fichier clients
3 mojito,bierre
7 cappuccino
12 mojito
20 expresso,thé


Chaque ligne :

<seconde> <liste de consommations séparées par des virgules>

🎬 Exemples de fonctionnement

Au lancement, les tâches suivantes s’exécutent en parallèle :

Serveur 1 → prend une commande → la met sur le Pic → sert une commande prête

Serveur 2 → travaille au même rythme, chacun avec un verrou interne

Bariste → prépare les commandes → peut aller servir directement si le Pic est vide

L’affichage dépend du mode verbose.

Un fichier fichier_async.log est généré contenant tous les événements avec timestamps.

Pour lire le fichier log en continu :

Windows PowerShell
Get-Content .\fichier_async.log -Wait -Tail 10


Linux/macOS
tail -f fichier_async.log

🏗 Architecture
Clients

lit un fichier de commandes et génère les demandes selon un timer

Pic (asyncio.Queue)

reçoit les post-it (commandes brutes)

file FIFO asynchrone

Bar (asyncio.Queue)

reçoit les boissons prêtes

le serveur les récupère pour servir

Serveur

Tâches asynchrones :

prendre_commande()

servir()

Caractéristiques :

possède un asyncio.Lock interne

productivité réglable (temps d’attente paramétrable)

Bariste

Tâches asynchrones :

preparer()

servir_directement() quand il n’y a plus de post-it

Main

création des queues asynchrones

lancement de toutes les tâches via asyncio.gather

gestion des logs

📚 Journalisation (logs)

fichier généré automatiquement avec date/heure

encodage UTF-8

chaque message comprend : employé, action, timestamp

affichage console dépend de verbose

⚠️ Limites et améliorations possibles

le système pourrait intégrer une gestion d’arrêt propre (shutdown) des tâches

la productivité pourrait être rendue dynamique (fatigue, surcharge…)

possibilité d’ajouter une interface graphique (Tkinter / PySide / web)

simulation plus réaliste (caisse, file de clients, priorités…)

tests unitaires à ajouter

🤝 Contribution

Les contributions sont les bienvenues :

Forkez le dépôt

Créez une branche feature/ma-fonctionnalité

Commit + push

Ouvrez une pull request décrivant vos modifications