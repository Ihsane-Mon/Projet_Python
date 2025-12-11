import subprocess
import sys
import os
from datetime import datetime

DOSSIER_RAPPORTS = "rapports"


def creer_dossier_rapports():
    """Crée le dossier rapports s'il n'existe pas."""
    if not os.path.exists(DOSSIER_RAPPORTS):
        os.makedirs(DOSSIER_RAPPORTS)


def executer_bandit():
    """Analyse de sécurité avec Bandit."""
    print("\n" + "=" * 50)
    print("  BANDIT - Analyse de sécurité")
    print("=" * 50)

    creer_dossier_rapports()
    rapport = (
        f"{DOSSIER_RAPPORTS}/bandit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    try:
        # Exécuter et afficher dans le terminal
        resultat = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "modules/", "-ll"],
            capture_output=True,
            text=True,
        )

        print(resultat.stdout)
        if resultat.stderr:
            print(resultat.stderr)

        # Sauvegarder le rapport
        with open(rapport, "w", encoding="utf-8") as f:
            f.write(resultat.stdout)

        print(f"\nRapport sauvegardé : {rapport}")
        return True
    except Exception as e:
        print(f"Erreur : {e}")
        return False


def executer_pylint():
    """Analyse qualité du code avec Pylint."""
    print("\n" + "=" * 50)
    print("  PYLINT - Qualité du code")
    print("=" * 50)

    creer_dossier_rapports()
    rapport = (
        f"{DOSSIER_RAPPORTS}/pylint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    fichiers = [
        "modules/produits.py",
        "modules/auth.py",
        "modules/password_check.py",
        "modules/commandes.py",
        "modules/stats.py",
    ]

    try:
        with open(rapport, "w", encoding="utf-8") as f:
            for fichier in fichiers:
                if os.path.exists(fichier):
                    print(f"\n--- {fichier} ---")
                    resultat = subprocess.run(
                        [sys.executable, "-m", "pylint", fichier, "--score=y"],
                        capture_output=True,
                        text=True,
                    )

                    # Afficher le score
                    for ligne in resultat.stdout.split("\n"):
                        if "rated at" in ligne or "error" in ligne.lower():
                            print(ligne)

                    f.write(f"\n{'=' * 50}\n{fichier}\n{'=' * 50}\n")
                    f.write(resultat.stdout)

        print(f"\nRapport complet : {rapport}")
        return True
    except Exception as e:
        print(f"Erreur : {e}")
        return False


def executer_safety():
    """Vérifie les vulnérabilités des dépendances."""
    print("\n" + "=" * 50)
    print("  SAFETY - Vulnérabilités des dépendances")
    print("=" * 50)

    creer_dossier_rapports()
    rapport = (
        f"{DOSSIER_RAPPORTS}/safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    try:
        resultat = subprocess.run(
            [sys.executable, "-m", "safety", "check"], capture_output=True, text=True
        )

        print(resultat.stdout)
        if resultat.stderr:
            print(resultat.stderr)

        with open(rapport, "w", encoding="utf-8") as f:
            f.write(resultat.stdout)
            f.write(resultat.stderr)

        print(f"\nRapport sauvegardé : {rapport}")
        return True
    except Exception as e:
        print(f"Erreur : {e}")
        return False


def verifier_secrets():
    """Vérifie l'absence de secrets en dur dans le code."""
    print("\n" + "=" * 50)
    print("  SECRETS - Vérification manuelle")
    print("=" * 50)

    patterns_dangereux = [
        ("secret_key", "Clé secrète"),
        ("password", "Mot de passe"),
        ("api_key", "Clé API"),
    ]

    fichiers_a_verifier = [
        "api.py",
        "modules/auth.py",
        "modules/password_check.py"]

    problemes = []

    for fichier in fichiers_a_verifier:
        if os.path.exists(fichier):
            with open(fichier, "r", encoding="utf-8") as f:
                lignes = f.readlines()
                for i, ligne in enumerate(lignes, 1):
                    ligne_lower = ligne.lower()
                    for pattern, description in patterns_dangereux:
                        if pattern in ligne_lower and "=" in ligne and '"' in ligne:
                            if not ligne.strip().startswith("#"):
                                problemes.append(
                                    f"{fichier}:{i} - {description} potentiel"
                                )

    if problemes:
        print("ATTENTION - Secrets potentiels détectés :")
        for p in problemes:
            print(f"  - {p}")
        print("\nRecommandation : Utiliser des variables d'environnement")
    else:
        print("OK - Aucun secret en dur détecté")

    return len(problemes) == 0


def audit_complet():
    """Lance un audit complet du projet."""
    print("\n" + "#" * 60)
    print("#          AUDIT DE SECURITE COMPLET")
    print("#" * 60)

    resultats = {
        "bandit": executer_bandit(),
        "pylint": executer_pylint(),
        "safety": executer_safety(),
        "secrets": verifier_secrets(),
    }

    print("\n" + "=" * 50)
    print("  RESUME DE L'AUDIT")
    print("=" * 50)

    for outil, succes in resultats.items():
        status = "OK" if succes else "A verifier"
        print(f"  {outil.upper():12} : {status}")

    print(f"\nRapports disponibles dans le dossier '{DOSSIER_RAPPORTS}/'")

    return all(resultats.values())
