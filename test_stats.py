from modules.commandes import creer_commande, valider_commande
from modules.stats import (
    afficher_tableau_bord,
    graphique_top_produits,
    graphique_revenus
)

#Créer quelques commandes pour avoir des données
print("=== Création de commandes test ===")
commandes_test = [
    (2, 5),  # produit 2, quantité 5
    (3, 2),  # produit 3, quantité 2
    (2, 3),  # produit 2, quantité 3
]

for produit_id, qte in commandes_test:
    commande, msg = creer_commande(produit_id, qte)
    if commande:
        valider_commande(commande["id"])
        print(f"Commande #{commande['id']} créée et validée")

#Afficher le tableau de bord
afficher_tableau_bord()

#Afficher les graphiques
print("\n=== Graphique Top Produits ===")
graphique_top_produits()

print("\n=== Graphique Revenus ===")
graphique_revenus()