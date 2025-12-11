from modules.auth import creer_compte, verifier_connexion

# Test avec mot de passe compromis
print("=== Création avec mot de passe compromis ===")
user, message = creer_compte("pierre", "Password123")
print(message)

# Test avec mot de passe sûr
print("\n=== Création avec mot de passe sûr ===")
user, message = creer_compte("marie", "Xk9mP2qL7nB4vR")
print(message)

# Test connexion
print("\n=== Connexion ===")
user, message = verifier_connexion("marie", "Xk9mP2qL7nB4vR")
print(message)
