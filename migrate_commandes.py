import csv
import os
import shutil
from datetime import datetime

FICHIER_COMMANDES = "data/commandes.csv"
FICHIER_LIGNES = "data/lignes_commandes.csv"
FICHIER_BACKUP = "data/commandes_backup_old_format.csv"


def migrer_vers_nouvelle_structure():
    """Migre les anciennes commandes vers la nouvelle structure."""
    
    if not os.path.exists(FICHIER_COMMANDES):
        print("❌ Fichier commandes.csv introuvable.")
        return
    
    # Vérifier le format actuel
    with open(FICHIER_COMMANDES, mode="r", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        colonnes = lecteur.fieldnames
        
        # Si c'est déjà le nouveau format
        if colonnes == ["id", "username", "date", "statut", "total"]:
            print("✅ Les commandes sont déjà au nouveau format.")
            return
        
        # Si c'est l'ancien format avec produit_id
        if "produit_id" not in colonnes:
            print("⚠️  Format de commandes non reconnu.")
            return
    
    print("🔄 Migration de l'ancien format vers le nouveau format...")
    
    # Faire une sauvegarde
    shutil.copy(FICHIER_COMMANDES, FICHIER_BACKUP)
    print(f"✅ Sauvegarde créée : {FICHIER_BACKUP}")
    
    # Charger les anciennes commandes
    anciennes_commandes = []
    with open(FICHIER_COMMANDES, mode="r", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            anciennes_commandes.append(ligne)
    
    print(f"📋 {len(anciennes_commandes)} anciennes commandes trouvées")
    
    # Regrouper par utilisateur et date pour créer de nouvelles commandes
    # Stratégie simple : chaque ancienne commande devient une nouvelle commande avec 1 ligne
    nouvelles_commandes = []
    nouvelles_lignes = []
    ligne_id = 1
    
    for idx, ancienne in enumerate(anciennes_commandes, 1):
        # Créer la nouvelle commande
        nouvelle_commande = {
            "id": idx,
            "username": ancienne.get("username", ""),
            "date": ancienne.get("date", datetime.now().isoformat()),
            "statut": ancienne.get("statut", "en_attente"),
            "total": float(ancienne.get("total", 0))
        }
        nouvelles_commandes.append(nouvelle_commande)
        
        # Créer la ligne de commande correspondante
        ligne = {
            "id": ligne_id,
            "commande_id": idx,
            "produit_id": int(ancienne.get("produit_id", 0)),
            "quantite": int(ancienne.get("quantite", 1)),
            "prix_unitaire": float(ancienne.get("prix_unitaire", 0)),
            "total": float(ancienne.get("total", 0))
        }
        nouvelles_lignes.append(ligne)
        ligne_id += 1
    
    # Sauvegarder les nouvelles commandes
    with open(FICHIER_COMMANDES, mode="w", encoding="utf-8", newline="") as f:
        colonnes = ["id", "username", "date", "statut", "total"]
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(nouvelles_commandes)
    
    print(f"✅ {len(nouvelles_commandes)} nouvelles commandes créées")
    
    # Sauvegarder les lignes de commandes
    with open(FICHIER_LIGNES, mode="w", encoding="utf-8", newline="") as f:
        colonnes = ["id", "commande_id", "produit_id", "quantite", "prix_unitaire", "total"]
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(nouvelles_lignes)
    
    print(f"✅ {len(nouvelles_lignes)} lignes de commandes créées")
    print("\n✨ Migration terminée avec succès !")
    print(f"📁 Ancienne structure sauvegardée dans : {FICHIER_BACKUP}")
    print("💡 Note : Les anciennes commandes ont été converties en commandes à 1 produit.")


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 MIGRATION VERS NOUVELLE STRUCTURE DE COMMANDES")
    print("=" * 60)
    migrer_vers_nouvelle_structure()
    print("=" * 60)
