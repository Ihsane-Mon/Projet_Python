import hashlib

import requests


def verifier_mot_de_passe_compromis(mot_de_passe):
    """
    Vérifie si un mot de passe est dans la base de données
    des mots de passe compromis (Have I Been Pwned).

    Retourne : (est_compromis, nombre_de_fois)
    """
    # Étape 1 : Hacher en SHA-1 (requis par l'API)
    sha1_hash = hashlib.sha1(mot_de_passe.encode()).hexdigest().upper() # nosec

    # Étape 2 : Séparer le hash (5 premiers + reste)
    prefixe = sha1_hash[:5]
    suffixe = sha1_hash[5:]

    # Étape 3 : Appeler l'API avec le préfixe seulement
    try:
        url = f"https://api.pwnedpasswords.com/range/%7Bprefixe%7D"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None, "Erreur lors de la vérification."

        # Étape 4 : Chercher le suffixe dans les résultats
        for ligne in response.text.splitlines():
            hash_suffixe, count = ligne.split(":")
            if hash_suffixe == suffixe:
                return True, int(count)

        return False, 0

    except requests.RequestException:
        return None, "Impossible de contacter l'API."
