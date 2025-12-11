import csv

FICHIER_PRODUITS = "data/produits.csv"


def charger_produits():
    """Charge tous les produits depuis le fichier CSV."""
    produits = []
    try:
        with open(FICHIER_PRODUITS, mode="r", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                produit = {
                    "id": int(ligne["id"]),
                    "nom": ligne["nom"],
                    "description": ligne["description"],
                    "prix": float(ligne["prix"]),
                    "quantite": int(ligne["quantite"]),
                }
                produits.append(produit)
    except FileNotFoundError:
        print("Fichier produits.csv introuvable.")
    return produits


def sauvegarder_produits(produits):
    """Sauvegarde la liste des produits dans le fichier CSV."""
    with open(FICHIER_PRODUITS, mode="w", encoding="utf-8", newline="") as fichier:
        colonnes = ["id", "nom", "description", "prix", "quantite"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(produits)


def generer_id(produits):
    """Génère un nouvel ID unique."""
    if not produits:
        return 1
    return max(p["id"] for p in produits) + 1


def ajouter_produit(produits, nom, description, prix, quantite):
    """Ajoute un nouveau produit à la liste."""
    nouveau = {
        "id": generer_id(produits),
        "nom": nom,
        "description": description,
        "prix": float(prix),
        "quantite": int(quantite),
    }
    produits.append(nouveau)
    sauvegarder_produits(produits)
    return nouveau


def trouver_produit(produits, id_produit):
    """Trouve un produit par son ID."""
    for produit in produits:
        if produit["id"] == id_produit:
            return produit
    return None


def modifier_produit(produits, id_produit, **modifications):
    """Modifie un produit existant."""
    produit = trouver_produit(produits, id_produit)
    if produit:
        for cle, valeur in modifications.items():
            if cle in produit and cle != "id":
                produit[cle] = valeur
        sauvegarder_produits(produits)
        return produit
    return None


def supprimer_produit(produits, id_produit):
    """Supprime un produit par son ID."""
    produit = trouver_produit(produits, id_produit)
    if produit:
        produits.remove(produit)
        sauvegarder_produits(produits)
        return True
    return False
