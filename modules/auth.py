import csv
import hashlib
import secrets
from datetime import datetime
import os
from modules.password_check import verifier_mot_de_passe_compromis

FICHIER_UTILISATEURS = "data/utilisateurs.csv"


def generer_salt():
    """Génère un salt aléatoire de 32 caractères."""
    return secrets.token_hex(16)


def hacher_mot_de_passe(mot_de_passe, salt):
    """Hache un mot de passe avec son salt en SHA-256."""
    combinaison = mot_de_passe + salt
    return hashlib.sha256(combinaison.encode()).hexdigest()


def charger_utilisateurs():
    """Charge tous les utilisateurs depuis le CSV."""
    utilisateurs = []
    try:
        with open(FICHIER_UTILISATEURS, mode="r", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                utilisateurs.append({
                    "id": int(ligne["id"]),
                    "username": ligne["username"],
                    "password_hash": ligne["password_hash"],
                    "salt": ligne["salt"],
                    "created_at": ligne["created_at"]
                })
    except FileNotFoundError:
        pass
    return utilisateurs


def sauvegarder_utilisateurs(utilisateurs):
    """Sauvegarde les utilisateurs dans le CSV."""
    with open(FICHIER_UTILISATEURS, mode="w", encoding="utf-8", newline="") as fichier:
        colonnes = ["id", "username", "password_hash", "salt", "created_at"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(utilisateurs)


def trouver_utilisateur(utilisateurs, username):
    """Trouve un utilisateur par son nom."""
    for user in utilisateurs:
        if user["username"] == username:
            return user
    return None


def creer_compte(username, mot_de_passe):
    """Crée un nouveau compte utilisateur."""
    utilisateurs = charger_utilisateurs()

#Vérifier si l'utilisateur existe déjà
    if trouver_utilisateur(utilisateurs, username):
        enregistrer_log(username, "creation_compte", False)
        return None, "Ce nom d'utilisateur existe déjà."

#Valider le mot de passe
    valide, erreurs = valider_mot_de_passe(mot_de_passe)
    if not valide:
        enregistrer_log(username, "creation_compte", False)
        return None, "Mot de passe invalide : " + " ".join(erreurs)

#Vérifier si le mot de passe est compromis
    compromis, count = verifier_mot_de_passe_compromis(mot_de_passe)
    if compromis:
        enregistrer_log(username, "creation_compte", False)
        return None, f"Ce mot de passe a été compromis {count} fois. Choisissez-en un autre."
    elif compromis is None:
        # Erreur API - on prévient mais on continue
        print("Attention : impossible de vérifier si le mot de passe est compromis.")

#Générer salt et hacher le mot de passe
    salt = generer_salt()
    password_hash = hacher_mot_de_passe(mot_de_passe, salt)

#Créer le nouvel utilisateur
    nouvel_id = max([u["id"] for u in utilisateurs], default=0) + 1
    nouvel_utilisateur = {
        "id": nouvel_id,
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "created_at": datetime.now().isoformat()
    }

    utilisateurs.append(nouvel_utilisateur)
    sauvegarder_utilisateurs(utilisateurs)
    enregistrer_log(username, "creation_compte", True)

    return nouvel_utilisateur, "Compte créé avec succès."



def verifier_connexion(username, mot_de_passe):
    """Vérifie les identifiants de connexion."""
    utilisateurs = charger_utilisateurs()
    utilisateur = trouver_utilisateur(utilisateurs, username)
    
    if not utilisateur:
        enregistrer_log(username, "connexion", False)
        return None, "Utilisateur introuvable."
    
    # Hacher le mot de passe saisi avec le salt stocké
    hash_saisi = hacher_mot_de_passe(mot_de_passe, utilisateur["salt"])
    
    # Comparaison sécurisée (temps constant)
    if secrets.compare_digest(hash_saisi, utilisateur["password_hash"]):
        enregistrer_log(username, "connexion", True)
        return utilisateur, "Connexion réussie."
    
    enregistrer_log(username, "connexion", False)
    return None, "Mot de passe incorrect."

FICHIER_LOGS = "data/logs.csv"


def valider_mot_de_passe(mot_de_passe):
    """Vérifie que le mot de passe respecte les règles de sécurité."""
    erreurs = []

    if len(mot_de_passe) < 8:
        erreurs.append("Au moins 8 caractères requis.")

    if not any(c.isupper() for c in mot_de_passe):
        erreurs.append("Au moins une majuscule requise.")

    if not any(c.islower() for c in mot_de_passe):
        erreurs.append("Au moins une minuscule requise.")

    if not any(c.isdigit() for c in mot_de_passe):
        erreurs.append("Au moins un chiffre requis.")

    return len(erreurs) == 0, erreurs

def enregistrer_log(username, action, succes):
    """Enregistre une action dans les logs."""
    fichier_existe = os.path.exists(FICHIER_LOGS)

    with open(FICHIER_LOGS, mode="a", encoding="utf-8", newline="") as fichier:
        colonnes = ["timestamp", "username", "action", "succes"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)

        if not fichier_existe:
            ecrivain.writeheader()

        ecrivain.writerow({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "succes": succes
        })