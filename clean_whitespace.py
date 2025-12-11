import os

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Supprime les espaces en fin de ligne et ajoute un retour final
    cleaned_lines = [line.rstrip() + '\n' for line in lines]

    # Ajoute un retour à la ligne final si manquant
    if cleaned_lines and not cleaned_lines[-1].endswith('\n'):
        cleaned_lines[-1] += '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

# Parcourt tous les fichiers Python
for root, dirs, files in os.walk('.'):
    # Ignore .git et venv
    dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '.venv', '__pycache__']]

    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            print(f"Nettoyage: {filepath}")
            clean_file(filepath)

print("Terminé !")
