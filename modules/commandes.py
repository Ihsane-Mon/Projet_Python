import csv
import os
from datetime import datetime

from modules.produits import (charger_produits, sauvegarder_produits,
                              trouver_produit)

FICHIER_COMMANDES = "data/commandes.csv"


def charger_commandes(username=None):
    """Charge toutes les commandes depuis le CSV. Filtre par username si fourni."""
    commandes = []
    try:
        with open(FICHIER_COMMANDES, mode="r", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                commandes.append({
                    "id": int(ligne["id"]),
                    "produit_id": int(ligne["produit_id"]),
                    "quantite": int(ligne["quantite"]),
                    "prix_unitaire": float(ligne["prix_unitaire"]),
                    "total": float(ligne["total"]),
                    "date": ligne["date"],
                    "statut": ligne["statut"]
                })
    except FileNotFoundError:
        pass
    return commandes


def sauvegarder_commandes(commandes):
    """Sauvegarde les commandes dans le CSV."""
    with open(FICHIER_COMMANDES, mode="w", encoding="utf-8", newline="") as fichier:
        colonnes = ["id", "produit_id", "quantite", "prix_unitaire", "total", "date", "statut"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(commandes)


def generer_id_commande(commandes):
    """Génère un nouvel ID pour une commande."""
    if not commandes:
        return 1
    return max(c["id"] for c in commandes) + 1


def creer_commande(produit_id, quantite, username):
    """Crée une nouvelle commande avec vérification du stock."""
    produits = charger_produits()
    produit = trouver_produit(produits, produit_id)

    if not produit:
        return None, "Produit introuvable."

    if produit["quantite"] < quantite:
        return None, f"Stock insuffisant. Disponible : {produit['quantite']}"

    # Calculer le total
    total = produit["prix"] * quantite

    # Créer la commande
    commandes = charger_commandes()
    nouvelle_commande = {
        "id": generer_id_commande(commandes),
        "produit_id": produit_id,
        "quantite": quantite,
        "prix_unitaire": produit["prix"],
        "total": total,
        "date": datetime.now().isoformat(),
        "statut": "en_attente"
    }

    # Mettre à jour le stock
    produit["quantite"] -= quantite
    sauvegarder_produits(produits)

    # Sauvegarder la commande
    commandes.append(nouvelle_commande)
    sauvegarder_commandes(commandes)

    return nouvelle_commande, "Commande créée avec succès."


def annuler_commande(id_commande):
    """Annule une commande et restaure le stock."""
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

    # Restaurer le stock
    produits = charger_produits()
    produit = trouver_produit(produits, commande["produit_id"])
    if produit:
        produit["quantite"] += commande["quantite"]
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
