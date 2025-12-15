import csv
import os
from datetime import datetime

from modules.produits import (charger_produits, sauvegarder_produits,
                              trouver_produit)

FICHIER_COMMANDES = "data/commandes.csv"
FICHIER_LIGNES_COMMANDES = "data/lignes_commandes.csv"


def charger_commandes(username=None):
    """Charge toutes les commandes depuis le CSV. Filtre par username si fourni."""
    commandes = []
    try:
        with open(FICHIER_COMMANDES, mode="r", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                commande = {
                    "id": int(ligne["id"]),
                    "username": ligne.get("username", ""),
                    "date": ligne["date"],
                    "statut": ligne["statut"],
                    "total": float(ligne["total"])
                }
                
                # Filtrer par username si fourni
                if username is None or commande["username"] == username:
                    commandes.append(commande)
    except FileNotFoundError:
        pass
    return commandes


def charger_lignes_commandes(commande_id=None):
    """Charge les lignes de commandes (produits). Filtre par commande_id si fourni."""
    lignes = []
    try:
        with open(FICHIER_LIGNES_COMMANDES, mode="r", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                ligne_commande = {
                    "id": int(ligne["id"]),
                    "commande_id": int(ligne["commande_id"]),
                    "produit_id": int(ligne["produit_id"]),
                    "quantite": int(ligne["quantite"]),
                    "prix_unitaire": float(ligne["prix_unitaire"]),
                    "total": float(ligne["total"])
                }
                
                # Filtrer par commande_id si fourni
                if commande_id is None or ligne_commande["commande_id"] == commande_id:
                    lignes.append(ligne_commande)
    except FileNotFoundError:
        pass
    return lignes


def charger_commande_complete(commande_id):
    """Charge une commande avec toutes ses lignes de produits."""
    commandes = charger_commandes()
    commande = None
    for c in commandes:
        if c["id"] == commande_id:
            commande = c.copy()
            break
    
    if not commande:
        return None
    
    # Ajouter les lignes de produits
    commande["lignes"] = charger_lignes_commandes(commande_id)
    return commande


def sauvegarder_commandes(commandes):
    """Sauvegarde les commandes dans le CSV."""
    with open(FICHIER_COMMANDES, mode="w", encoding="utf-8", newline="") as fichier:
        colonnes = ["id", "username", "date", "statut", "total"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(commandes)


def sauvegarder_lignes_commandes(lignes):
    """Sauvegarde les lignes de commandes dans le CSV."""
    with open(FICHIER_LIGNES_COMMANDES, mode="w", encoding="utf-8", newline="") as fichier:
        colonnes = ["id", "commande_id", "produit_id", "quantite", "prix_unitaire", "total"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def generer_id_commande(commandes):
    """Génère un nouvel ID pour une commande."""
    if not commandes:
        return 1
    return max(c["id"] for c in commandes) + 1


def generer_id_ligne(lignes):
    """Génère un nouvel ID pour une ligne de commande."""
    if not lignes:
        return 1
    return max(l["id"] for l in lignes) + 1


def creer_commande(items_panier, username):
    """
    Crée une nouvelle commande avec plusieurs produits (panier).
    
    Args:
        items_panier: Liste de dict avec {produit_id, quantite}
        username: Nom de l'utilisateur
        
    Returns:
        tuple: (commande, message) ou (None, message_erreur)
    """
    if not items_panier:
        return None, "Le panier est vide."
    
    produits = charger_produits()
    
    # Vérifier le stock pour tous les produits
    for item in items_panier:
        produit = trouver_produit(produits, item["produit_id"])
        if not produit:
            return None, f"Produit #{item['produit_id']} introuvable."
        if produit["quantite"] < item["quantite"]:
            return None, f"Stock insuffisant pour {produit['nom']}. Disponible : {produit['quantite']}"
    
    # Créer la commande principale
    commandes = charger_commandes()
    lignes_existantes = charger_lignes_commandes()
    
    commande_id = generer_id_commande(commandes)
    total_commande = 0
    nouvelles_lignes = []
    
    # Créer les lignes de commande et mettre à jour le stock
    for item in items_panier:
        produit = trouver_produit(produits, item["produit_id"])
        total_ligne = produit["prix"] * item["quantite"]
        total_commande += total_ligne
        
        # Créer la ligne
        nouvelle_ligne = {
            "id": generer_id_ligne(lignes_existantes),
            "commande_id": commande_id,
            "produit_id": item["produit_id"],
            "quantite": item["quantite"],
            "prix_unitaire": produit["prix"],
            "total": total_ligne
        }
        nouvelles_lignes.append(nouvelle_ligne)
        lignes_existantes.append(nouvelle_ligne)
        
        # Mettre à jour le stock
        produit["quantite"] -= item["quantite"]
    
    # Créer la commande
    nouvelle_commande = {
        "id": commande_id,
        "username": username,
        "date": datetime.now().isoformat(),
        "statut": "en_attente",
        "total": total_commande
    }
    
    # Sauvegarder tout
    commandes.append(nouvelle_commande)
    sauvegarder_commandes(commandes)
    sauvegarder_lignes_commandes(lignes_existantes)
    sauvegarder_produits(produits)
    
    # Retourner la commande complète avec ses lignes
    nouvelle_commande["lignes"] = nouvelles_lignes
    return nouvelle_commande, "Commande créée avec succès."


def annuler_commande(id_commande):
    """Annule une commande et restaure le stock de tous les produits."""
    commandes = charger_commandes()
    
    commande = None
    for c in commandes:
        if c["id"] == id_commande:
            commande = c
            break
    
    if not commande:
        return False, "Commande introuvable."
    
    if commande["statut"] == "annulee":
        return False, "Commande déjà annulée."
    
    # Restaurer le stock pour toutes les lignes
    lignes = charger_lignes_commandes(id_commande)
    produits = charger_produits()
    
    for ligne in lignes:
        produit = trouver_produit(produits, ligne["produit_id"])
        if produit:
            produit["quantite"] += ligne["quantite"]
    
    sauvegarder_produits(produits)
    
    # Mettre à jour le statut
    commande["statut"] = "annulee"
    sauvegarder_commandes(commandes)
    
    return True, "Commande annulée."


def valider_commande(id_commande):
    """Valide une commande."""
    commandes = charger_commandes()
    
    for c in commandes:
        if c["id"] == id_commande:
            if c["statut"] != "en_attente":
                return False, "Cette commande ne peut pas être validée."
            c["statut"] = "validee"
            sauvegarder_commandes(commandes)
            return True, "Commande validée."
    
    return False, "Commande introuvable."
