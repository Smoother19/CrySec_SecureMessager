# CrySec_SecureMessager

CrySec Secure Messenger - Client CLI

Ce projet est un client de messagerie sécurisé en ligne de commande (CLI) développé en Python. Il permet de communiquer avec un serveur distant et d'exécuter diverses opérations cryptographiques (Chiffrement par décalage, Vigenère, RSA, Diffie-Hellman, Hachage SHA-256). Il intègre également un système d'automatisation pour intercepter et résoudre les tâches (challenges) envoyées par le serveur.
# Concept Principal : Les Buffers

Le client fonctionne autour d'un système de "Buffers" (mémoire temporaire) pour manipuler les données avant de les envoyer ou après les avoir reçues :

    Buffer Plain : Contient le texte en clair (lisible).

    Buffer Encoded : Contient le texte chiffré (liste de nombres RSA, hexadécimal Vigenère) ou le résultat d'un hachage.

Le flux de travail classique : on place un texte dans un buffer, on applique un algorithme (qui déplace/transforme le résultat dans l'autre buffer), puis on envoie le contenu final.
Liste des Commandes
1. Commandes Générales

    /help : Affiche la liste de toutes les commandes disponibles.

    /quit : Ferme la connexion proprement et quitte l'application.

2. Gestion des Buffers

    /set <plain|encoded> <texte> : Insère manuellement du texte ou des chiffres dans le buffer spécifié.

    /show : Affiche le contenu actuel des buffers plain et encoded.

    /clearbuf [plain|encoded] : Vide le buffer spécifié, ou les deux si aucun n'est précisé.

3. Communication Réseau

    /send <texte> : Envoie un message texte simple (type t) au serveur ou aux autres clients.

    /send <plain|encoded> : Envoie le contenu brut du buffer spécifié.

    /send <...> -s : Ajoute le flag -s pour envoyer le message en tant qu'instruction Système/Serveur (indispensable pour répondre aux exercices).

4. Cryptographie de base

    /encode <shift|vigenere> <clé> : Chiffre le contenu de plain vers encoded.

    /decode <shift|vigenere> <clé> : Déchiffre le contenu de encoded vers plain.

5. Cryptographie Avancée (RSA)

    /rsa <taille_en_bits> : Génère une paire de clés RSA (Publique et Privée) de la taille spécifiée.

    /encode rsa [n e] : Chiffre le plain vers encoded. Utilise la clé automatique du serveur si détectée.

    /decode rsa <n> <d> : Déchiffre le contenu de encoded (liste de nombres) vers plain.

6. Échange de clés (Diffie-Hellman)

    /dh_gen : Génère les paramètres initiaux (p,g,a,A) pour un échange.

    /dh_sec <B> : Calcule le secret partagé final à partir de la clé publique (B) reçue du serveur.

7. Hachage (SHA-256)

    /hash [texte] : Hache le texte fourni (ou le buffer plain) et stocke le résultat SHA-256 dans encoded.

# Tutoriels de Résolution des Tâches (Serveur)

Le client détecte automatiquement les instructions du serveur. Voici les protocoles de réponse :
## Encodage RSA

    Demandez la tâche : /send -s task RSA encode 100

    Le serveur envoie la clé et le mot. Le client capture le mot dans plain.

    Chiffrez : /encode rsa

    Envoyez : /send -s encoded

## Décodage RSA

    Demandez la tâche : /send -s task RSA decode 10

    Générez vos clés : /rsa 12

    Envoyez votre clé publique au serveur : /send -s <n>,<e>

    Le serveur envoie des nombres. Copiez-les : /set encoded <nombres>

    Décodez : /decode rsa <votre_n> <votre_d>

    Envoyez la réponse : /send -s plain

## Diffie-Hellman (DifHel)

    Demandez la tâche : /send -s task DifHel

    Générez vos paramètres : /dh_gen

    Suivez l'étape 1 (envoyer p et g) : /send -s <p>,<g>

    Suivez l'étape 2 (envoyer votre clé A) : /send -s <A>

    Le serveur donne sa clé B. Calculez le secret : /dh_sec <B>

    Envoyez le secret calculé : /send -s <secret>

## Hachage SHA-256

    Demandez la tâche : /send -s task hash hash

    Le client capture le texte dans plain (et gère les bugs d'affichage du serveur).

    Hachez : /hash

    Envoyez : /send -s encoded