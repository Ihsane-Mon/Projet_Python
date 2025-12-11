from modules.commandes import (
    creer_commande,
    charger_commandes,
    valider_commande,
    annuler_commande,
)

# Créer une commande
print("=== Création d'une commande ===")
commande, message = creer_commande(produit_id=2, quantite=3)
print(message)
if commande:
    print(f"Commande #{commande['id']} - Total : {commande['total']}€")

# Afficher toutes les commandes
print("\n=== Liste des commandes ===")
for c in charger_commandes():
    print(
        f"#{
            c['id']} | Produit {
            c['produit_id']} | Qté: {
                c['quantite']} | Total: {
                    c['total']}€ | Statut: {
                        c['statut']}")

# Valider la commande
print("\n=== Validation ===")
if commande:
    succes, message = valider_commande(commande["id"])
    print(message)
