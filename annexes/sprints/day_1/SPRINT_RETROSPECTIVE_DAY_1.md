# Rétrospective du sprint jour 1 (05/01)

## Lecture du sujet

On a lu dans la matinée le sujet tous ensemble sur un vidéo projecteur !

## Écoute et partage des idées concernant les approches de design global et de mécaniques de jeu

Plusieurs choix ont été faits :
- Notre jeu se passera sous l'eau, et il faudra protéger un coffre englouti contenant toutes les économies du poisson orange.
- On n'autoriserait pas de construire notre dongeon comme on veut : seuls des endroits prédéterminés par le **niveau** autorisent la construction.
- On veut que la phase de construction soit limitée dans le temps, et qu'on puisse construire pendant les vagues.
- Puisqu'on doit implémenter une version en terminal, les ennemis se déplaceront tuile par tuile (potentiellement en diagonale)
- Les ennemis devront non seulement atteindre le trésor mais aussi **le ramener à l'entrée** du dongeon. Ils peuvent alors mourir lors du retour et faire tomber une partir du trésor

## Discussion concernant les technologies

Le java c'est non : on ne sait pas faire d'interface web, alors qu'en **Python**, on peut se débrouiller.

Concernant le terminal, on connait déjà la bibliothèque **curses** qu'on a pu utiliser pendant le PP2I-2.

Concernant le web, on pense utiliser **FastAPI** et **Jinja**, mais ça reste à étudier.

## Diagramme de classes

Dessiné sur un tableau blanc, on décide alors de l'implémentation des niveaux, de l'état de jeu, des ennemis, des tuiles, des tours, des pièges...

## Mise en place du serveur Discord et crochet web Gitlab

C'est fait !

## Mise en place de la structure du dépôt Git

Fait aussi ! On a chacun notre branche, et les dossiers principaux sont là : `assets`, `src`, `data`, `tests`... On a évidemment un ``.gitignore``, et même une *pipeline* pour les quelques tests unitaires déjà écrits !

## Mise en place des classes principales et du système de stockage de dongeons

Après quelques problèmes d'imports en Python, on cerne le fonctionnement et on a de suite des première classes : `Position`, `Level_template`, `Game_instance`, `Tile`... On décide du système de position (x vertical, y horizontal, origine en haut à gauche)

## Étude première d'implémentation en CLI

Connaissant déjà la version C de la bibliothèque `curses`, on a en fin de la journée : 
- Une structure globale de fichiers (principal, affichage, couleurs)
- Une boucle avec un automate pour l'état de jeu
- Un écran titre avec un texte *splash* aléatoirement choisi parmi une liste
- Un écran de sélection de niveaux qui affiche la carte et le nombre de vagues de celui-ci
- Un premier système de curseur et de sélection de tuiles

## Rédaction de la *roadmap* et des premiers fichiers de sprint
- Faits !