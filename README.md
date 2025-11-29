# BarCoktail
BarCoktail est une petite simulation de bar écrite en Python(asyncrone) qui illustre la prise de commande, la préparation et le service de boissons en mélangeant threading et asyncio. Le script principal est BAR_ASYNCRO.py.

Sommaire
Description
Fonctionnalités
Prérequis
Installation
Utilisation
Exemple d'exécution
Architecture et conception
Limites connues et améliorations proposées
Contribution
Licence
Description
Le projet simule le fonctionnement simplifié d'un bar : un Serveur prend des commandes (représentées par des post‑it), les empile sur un Pic, un Barman récupère les post‑it, prépare les boissons et les dépose sur un Bar, puis le Serveur sert les clients. Le but est pédagogique : montrer la coordination entre producteurs/consommateurs avec des primitives asynchrones et multi‑threads.

Fonctionnalités
Prise de commande (Serveur)
Empilement des commandes sur un Pic (pile LIFO)
Préparation des boissons (Barman)
Dépôt des boissons prêtes sur le Bar
Service aux clients et encaissement
Trois niveaux de verbosité pour afficher plus ou moins d'informations
Journalisation basique des événements dans un fichier log
Prérequis
Python 3.8 ou supérieur
Aucune dépendance externe
Installation
Cloner le dépôt :
Code
git clone https://github.com/Prosper1325/BarCoktail.git
Se placer dans le répertoire :
Code
cd BarCoktail
(Optionnel) Créer un environnement virtuel :
Code
python3 -m venv venv
source venv/bin/activate  # Linux / macOS
venv\\Scripts\\activate   # Windows
Utilisation
Le script principal s'appelle BAR_ASYNCRO.py et accepte les commandes (noms de boissons) en arguments de ligne de commande.

Commande exemple :

Code
python3 BAR_ASYNCRO.py mojito margarita espresso
Au démarrage, le programme demande le niveau de verbosité :

1 : affichage minimal
2 : affichage détaillé
3 : affichage très verbeux (états internes)
Exemple d'exécution
Après avoir lancé la commande ci‑dessus et choisi la verbosité, le Serveur commencera à prendre les commandes (post‑it), le Barman préparera les boissons puis le Serveur servira les clients. Des messages sont affichés en console et un fichier de log est créé (nom généré avec la date/heure).

Architecture et points importants du code
Accessoire : classe de base contenant deux listes (liste, etat).
Pic : pile LIFO pour empiler les post‑it (méthodes embrocher/liberer).
Bar : zone de dépôt des boissons prêtes (méthodes recevoir/evacuer).
Serveur : thread qui exécute un loop asyncio pour prendre les commandes et servir.
Barman : thread qui exécute un loop asyncio pour préparer et encaisser.


Pour accéder au contenu du fichier log: Get-Content .\borabora.log -Wait ( commande windows)


Remarques techniques :

Le code mélange threading.Thread et asyncio (chaque thread lance son propre asyncio.run()).
Certaines boucles utilisent du busy‑waiting (while ...: pass) ce qui peut consommer CPU.
Les structures partagées (listes) ne sont pas protégées par des verrous, ce qui peut provoquer des conditions de course.
Le fichier de log utilise un nom contenant la date/heure ; la chaîne actuelle peut contenir des caractères inattendus.
Limites connues et améliorations proposées
Remplacer les listes partagées par des structures thread‑safe (queue.Queue ou asyncio.Queue).
Éviter le busy‑waiting en utilisant des primitives de synchronisation (Condition, Event, Queue).
Centraliser l'utilisation d'un seul event loop asyncio, ou passer à une implémentation entièrement multi‑threads/puresynchronisation.
Améliorer le format du nom du fichier de log et ajouter des rotations (RotatingFileHandler).
Ajouter des tests unitaires et des exemples automatisés.
Contribution
Les contributions sont bienvenues. Pour contribuer :

Forkez le dépôt.
Créez une branche feature/mon‑amelioration.
Faites vos modifications et ajoutez des tests si possible.
Ouvrez une pull request décrivant les changements.
