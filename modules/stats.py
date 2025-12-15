from collections import defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

from modules.commandes import charger_commandes
from modules.produits import charger_produits


def calculer_statistiques():
    """Calcule les statistiques globales."""
    commandes = charger_commandes()
    produits = charger_produits()

    # Filtrer les commandes validées uniquement
    commandes_valides = [c for c in commandes if c["statut"] == "validee"]

    stats = {
        "total_commandes": len(commandes_valides),
        "chiffre_affaires": sum(c["total"] for c in commandes_valides),
        "produits_vendus": sum(c["quantite"] for c in commandes_valides),
        "nombre_produits": len(produits),
        "valeur_stock": sum(p["prix"] * p["quantite"] for p in produits),
    }

    return stats


def top_produits(limite=5):
    """Retourne les produits les plus vendus."""
    commandes = charger_commandes()
    produits = charger_produits()

    # Compter les ventes par produit
    ventes = defaultdict(int)
    revenus = defaultdict(float)

    for c in commandes:
        if c["statut"] == "validee":
            ventes[c["produit_id"]] += c["quantite"]
            revenus[c["produit_id"]] += c["total"]

    # Associer avec les noms des produits
    resultats = []
    for produit_id, quantite in ventes.items():
        produit = next((p for p in produits if p["id"] == produit_id), None)
        if produit:
            resultats.append(
                {
                    "id": produit_id,
                    "nom": produit["nom"],
                    "quantite_vendue": quantite,
                    "revenus": revenus[produit_id],
                }
            )

    # Trier par quantité vendue
    resultats.sort(key=lambda x: x["quantite_vendue"], reverse=True)

    return resultats[:limite]


def graphique_top_produits():
    """Génère un graphique des produits les plus vendus."""
    top = top_produits(5)

    if not top:
        print("Aucune donnée à afficher.")
        return

    noms = [p["nom"] for p in top]
    quantites = [p["quantite_vendue"] for p in top]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=quantites, y=noms, palette="viridis")
    plt.xlabel("Quantité vendue")
    plt.ylabel("Produit")
    plt.title("Top 5 des produits les plus vendus")
    plt.tight_layout()
    plt.show()


def graphique_revenus():
    """Génère un graphique des revenus par produit."""
    top = top_produits(5)

    if not top:
        print("Aucune donnée à afficher.")
        return

    noms = [p["nom"] for p in top]
    revenus = [p["revenus"] for p in top]

    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("Blues_r", len(noms))
    plt.pie(
        revenus,
        labels=noms,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90)
    plt.title("Répartition du chiffre d'affaires par produit")
    plt.tight_layout()
    plt.show()


def graphique_evolution_ventes():
    """Génère un graphique de l'évolution des ventes."""
    commandes = charger_commandes()
    commandes_valides = [c for c in commandes if c["statut"] == "validee"]

    if not commandes_valides:
        print("Aucune donnée à afficher.")
        return

    # Grouper par date
    ventes_par_jour = defaultdict(float)
    for c in commandes_valides:
        date = c["date"][:10]  # Garder seulement YYYY-MM-DD
        ventes_par_jour[date] += c["total"]

    # Trier par date
    dates = sorted(ventes_par_jour.keys())
    totaux = [ventes_par_jour[d] for d in dates]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, totaux, marker="o", linewidth=2, markersize=8)
    plt.xlabel("Date")
    plt.ylabel("Chiffre d'affaires (€)")
    plt.title("Évolution des ventes")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def afficher_tableau_bord():
    """Affiche un tableau de bord complet."""
    stats = calculer_statistiques()

    print("\n" + "=" * 50)
    print("          TABLEAU DE BORD")
    print("=" * 50)
    print(f"  Commandes validées    : {stats['total_commandes']}")
    print(f"  Chiffre d'affaires    : {stats['chiffre_affaires']:.2f}€")
    print(f"  Produits vendus       : {stats['produits_vendus']}")
    print(f"  Produits en catalogue : {stats['nombre_produits']}")
    print(f"  Valeur du stock       : {stats['valeur_stock']:.2f}€")
    print("=" * 50)

    print("\n--- Top 5 Produits ---")
    for i, p in enumerate(top_produits(5), 1):
        print(
            f"{i}. {p['nom']} : {p['quantite_vendue']} vendus ({p['revenus']:.2f}€)"
        )
