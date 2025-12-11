from modules.produits import (
    charger_produits,
    ajouter_produit,
    modifier_produit,
    supprimer_produit,
    trouver_produit,
)


def afficher_menu():
    """Affiche le menu principal."""
    print("\n" + "=" * 40)
    print("   GESTION DES PRODUITS - E-COMMERCE")
    print("=" * 40)
    print("1. Afficher tous les produits")
    print("2. Rechercher un produit")
    print("3. Ajouter un produit")
    print("4. Modifier un produit")
    print("5. Supprimer un produit")
    print("6. Quitter")
    print("=" * 40)


def afficher_produits(produits):
    """Affiche la liste des produits."""
    if not produits:
        print("\nAucun produit enregistré.")
        return
    print(f"\n{'ID':<5} {'Nom':<20} {'Prix':<10} {'Stock':<10}")
    print("-" * 45)
    for p in produits:
        print(f"{p['id']:<5} {p['nom']:<20} {p['prix']:<10.2f} {p['quantite']:<10}")


def rechercher_produit(produits):
    """Recherche un produit par ID."""
    try:
        id_produit = int(input("ID du produit : "))
        produit = trouver_produit(produits, id_produit)
        if produit:
            print(f"\nNom : {produit['nom']}")
            print(f"Description : {produit['description']}")
            print(f"Prix : {produit['prix']}€")
            print(f"Stock : {produit['quantite']}")
        else:
            print("Produit introuvable.")
    except ValueError:
        print("ID invalide.")


def saisir_nouveau_produit(produits):
    """Saisie d'un nouveau produit."""
    try:
        nom = input("Nom : ")
        description = input("Description : ")
        prix = float(input("Prix : "))
        quantite = int(input("Quantité : "))

        if prix < 0 or quantite < 0:
            print("Le prix et la quantité doivent être positifs.")
            return

        nouveau = ajouter_produit(produits, nom, description, prix, quantite)
        print(f"Produit '{nouveau['nom']}' ajouté avec l'ID {nouveau['id']}.")
    except ValueError:
        print("Erreur de saisie. Vérifiez le prix et la quantité.")


def saisir_modification(produits):
    """Modifie un produit existant."""
    try:
        id_produit = int(input("ID du produit à modifier : "))
        produit = trouver_produit(produits, id_produit)

        if not produit:
            print("Produit introuvable.")
            return

        print(f"Produit actuel : {produit['nom']} - {produit['prix']}€")
        print("Laissez vide pour garder la valeur actuelle.")

        nom = input(f"Nouveau nom ({produit['nom']}) : ") or produit["nom"]
        description = (
            input(f"Description ({produit['description']}) : ")
            or produit["description"]
        )
        prix_input = input(f"Prix ({produit['prix']}) : ")
        quantite_input = input(f"Quantité ({produit['quantite']}) : ")

        prix = float(prix_input) if prix_input else produit["prix"]
        quantite = int(
            quantite_input) if quantite_input else produit["quantite"]

        modifier_produit(
            produits,
            id_produit,
            nom=nom,
            description=description,
            prix=prix,
            quantite=quantite,
        )
        print("Produit modifié avec succès.")
    except ValueError:
        print("Erreur de saisie.")


def confirmer_suppression(produits):
    """Supprime un produit après confirmation."""
    try:
        id_produit = int(input("ID du produit à supprimer : "))
        produit = trouver_produit(produits, id_produit)

        if not produit:
            print("Produit introuvable.")
            return

        confirmation = input(f"Supprimer '{produit['nom']}' ? (oui/non) : ")
        if confirmation.lower() == "oui":
            supprimer_produit(produits, id_produit)
            print("Produit supprimé.")
        else:
            print("Suppression annulée.")
    except ValueError:
        print("ID invalide.")


def main():
    """Boucle principale du programme."""
    produits = charger_produits()

    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        if choix == "1":
            afficher_produits(produits)
        elif choix == "2":
            rechercher_produit(produits)
        elif choix == "3":
            saisir_nouveau_produit(produits)
        elif choix == "4":
            saisir_modification(produits)
        elif choix == "5":
            confirmer_suppression(produits)
        elif choix == "6":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    main()
