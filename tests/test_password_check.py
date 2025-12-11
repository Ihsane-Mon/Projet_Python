from modules.password_check import verifier_mot_de_passe_compromis

# Test avec un mot de passe très courant (compromis)
print("=== Test : 'password' ===")
compromis, count = verifier_mot_de_passe_compromis("password")
if compromis:
    print(f"COMPROMIS ! Trouvé {count} fois dans des fuites.")
else:
    print("Non compromis.")

# Test avec '123456'
print("\n=== Test : '123456' ===")
compromis, count = verifier_mot_de_passe_compromis("123456")
if compromis:
    print(f"COMPROMIS ! Trouvé {count} fois dans des fuites.")
else:
    print("Non compromis.")

# Test avec un mot de passe unique
print("\n=== Test : 'Xk9$mP2@qL7nB4vR' ===")
compromis, count = verifier_mot_de_passe_compromis("Xk9$mP2@qL7nB4vR")
if compromis:
    print(f"COMPROMIS ! Trouvé {count} fois.")
else:
    print("Non compromis - Ce mot de passe est sûr.")
