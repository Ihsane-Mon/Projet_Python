from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import datetime

from modules.produits import (
    charger_produits,
    ajouter_produit,
    modifier_produit,
    supprimer_produit,
    trouver_produit,
)
from modules.auth import verifier_connexion, creer_compte, charger_utilisateurs, creer_admin_initial
from modules.commandes import charger_commandes, creer_commande, valider_commande, annuler_commande
from modules.stats import calculer_statistiques, top_produits

app = Flask(__name__)
CORS(app)

# Clé secrète pour JWT (en production, utiliser une variable d'environnement)
SECRET_KEY = "votre_cle_secrete_tres_longue_et_complexe"


# ==================== MIDDLEWARE AUTH ====================


def token_requis(f):
    """Décorateur pour protéger les routes."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erreur": "Token manquant"}), 401

        try:
            # Enlever "Bearer " si présent
            if token.startswith("Bearer "):
                token = token[7:]

            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.utilisateur = data["username"]
            request.role = data.get("role", "user")
        except jwt.ExpiredSignatureError:
            return jsonify({"erreur": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erreur": "Token invalide"}), 401

        return f(*args, **kwargs)
    return decorated


def admin_requis(f):
    """Décorateur pour protéger les routes admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erreur": "Token manquant"}), 401

        try:
            # Enlever "Bearer " si présent
            if token.startswith("Bearer "):
                token = token[7:]

            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.utilisateur = data["username"]
            request.role = data.get("role", "user")

            # Vérifier le rôle admin
            if request.role != "admin":
                return jsonify({"erreur": "Accès refusé. Droits administrateur requis."}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"erreur": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erreur": "Token invalide"}), 401

        return f(*args, **kwargs)

    return decorated


# ==================== AUTH ENDPOINTS ====================


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authentification et génération du token JWT."""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"erreur": "Username et password requis"}), 400

    user, message = verifier_connexion(data["username"], data["password"])

    if user:
        # CORRECTION: Inclure le rôle dans le token JWT
        user_role = user.get("role", "user")
        token = jwt.encode({
            "username": user["username"],
            "role": user_role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        # CORRECTION: Renvoyer le rôle dans la réponse
        return jsonify({
            "message": message,
            "token": token,
            "username": user["username"],
            "role": user_role
        })

    return jsonify({"erreur": message}), 401


@app.route("/api/auth/register", methods=["POST"])
def register():
    """Création de compte."""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"erreur": "Username et password requis"}), 400

    user, message = creer_compte(data["username"], data["password"])

    if user:
        return jsonify({"message": message}), 201

    return jsonify({"erreur": message}), 400


# ==================== PRODUITS ENDPOINTS ====================


@app.route("/api/products", methods=["GET"])
def get_produits():
    """Liste tous les produits avec pagination."""
    produits = charger_produits()

    # Pagination
    page = request.args.get("page", 1, type=int)
    limite = request.args.get("limite", 10, type=int)

    debut = (page - 1) * limite
    fin = debut + limite

    return jsonify(
        {
            "produits": produits[debut:fin],
            "total": len(produits),
            "page": page,
            "pages": (len(produits) + limite - 1) // limite,
        }
    )


@app.route("/api/products/<int:id>", methods=["GET"])
def get_produit(id):
    """Détails d'un produit."""
    produits = charger_produits()
    produit = trouver_produit(produits, id)

    if produit:
        return jsonify(produit)

    return jsonify({"erreur": "Produit introuvable"}), 404


@app.route("/api/products", methods=["POST"])
@token_requis
def post_produit():
    """Créer un nouveau produit (auth requise)."""
    data = request.get_json()

    champs_requis = ["nom", "description", "prix", "quantite"]
    if not data or not all(champ in data for champ in champs_requis):
        return (
            jsonify({"erreur": "Champs requis: nom, description, prix, quantite"}),
            400,
        )

    try:
        produits = charger_produits()
        nouveau = ajouter_produit(
            produits,
            data["nom"],
            data["description"],
            float(data["prix"]),
            int(data["quantite"]),
        )
        return jsonify(nouveau), 201
    except ValueError:
        return jsonify({"erreur": "Prix ou quantité invalide"}), 400


@app.route("/api/products/<int:id>", methods=["PUT"])
@token_requis
def put_produit(id):
    """Modifier un produit (auth requise)."""
    data = request.get_json()

    if not data:
        return jsonify({"erreur": "Données requises"}), 400

    produits = charger_produits()
    produit = trouver_produit(produits, id)

    if not produit:
        return jsonify({"erreur": "Produit introuvable"}), 404

    try:
        modifications = {}
        if "nom" in data:
            modifications["nom"] = data["nom"]
        if "description" in data:
            modifications["description"] = data["description"]
        if "prix" in data:
            modifications["prix"] = float(data["prix"])
        if "quantite" in data:
            modifications["quantite"] = int(data["quantite"])

        modifier_produit(produits, id, **modifications)
        return jsonify(trouver_produit(charger_produits(), id))
    except ValueError:
        return jsonify({"erreur": "Données invalides"}), 400


@app.route("/api/products/<int:id>", methods=["DELETE"])
@token_requis
def delete_produit(id):
    """Supprimer un produit (auth requise)."""
    produits = charger_produits()

    if not trouver_produit(produits, id):
        return jsonify({"erreur": "Produit introuvable"}), 404

    supprimer_produit(produits, id)
    return jsonify({"message": "Produit supprimé"}), 200


# ==================== COMMANDES ENDPOINTS ====================


@app.route("/api/orders", methods=["GET"])
@token_requis
def get_commandes():
    """Liste toutes les commandes de l'utilisateur connecté."""
    commandes = charger_commandes(username=request.utilisateur)
    return jsonify({"commandes": commandes, "total": len(commandes)})


@app.route("/api/orders", methods=["POST"])
@token_requis
def post_commande():
    """Créer une commande."""
    data = request.get_json()

    if not data or "produit_id" not in data or "quantite" not in data:
        return jsonify({"erreur": "produit_id et quantite requis"}), 400

    try:
        # CORRECTION: Passer le username comme 3ème argument
        commande, message = creer_commande(
            int(data["produit_id"]),
            int(data["quantite"]),
            request.utilisateur
        )

        if commande:
            return jsonify({"commande": commande, "message": message}), 201
        return jsonify({"erreur": message}), 400
    except Exception as e:
        return jsonify({"erreur": f"Erreur: {str(e)}"}), 400


@app.route("/api/orders/<int:id>/validate", methods=["POST"])
@token_requis
def post_valider_commande(id):
    """Valider une commande."""
    succes, message = valider_commande(id)

    if succes:
        return jsonify({"message": message})
    return jsonify({"erreur": message}), 400


@app.route("/api/orders/<int:id>/cancel", methods=["POST"])
@token_requis
def post_annuler_commande(id):
    """Annuler une commande."""
    succes, message = annuler_commande(id)

    if succes:
        return jsonify({"message": message})
    return jsonify({"erreur": message}), 400


# ==================== STATS ENDPOINT ====================


@app.route("/api/stats", methods=["GET"])
@token_requis
def get_stats():
    """Statistiques agrégées."""
    stats = calculer_statistiques()
    top = top_produits(5)

    return jsonify({"statistiques": stats, "top_produits": top})


# ==================== ADMIN ENDPOINTS ====================

@app.route("/api/admin/stats", methods=["GET"])
@admin_requis
def get_admin_stats():
    """Statistiques globales pour l'admin."""
    produits = charger_produits()
    commandes = charger_commandes()
    utilisateurs = charger_utilisateurs()

    # Calculer les stats
    total_produits = len(produits)
    stock_total = sum(p["quantite"] for p in produits)
    valeur_stock = sum(p["prix"] * p["quantite"] for p in produits)

    total_commandes = len(commandes)
    commandes_attente = len([c for c in commandes if c["statut"] == "en_attente"])
    commandes_validees = len([c for c in commandes if c["statut"] == "validee"])

    ca_total = sum(c["total"] for c in commandes if c["statut"] == "validee")

    total_users = len(utilisateurs)

    return jsonify({
        "produits": {
            "total": total_produits,
            "stock_total": stock_total,
            "valeur_stock": round(valeur_stock, 2)
        },
        "commandes": {
            "total": total_commandes,
            "en_attente": commandes_attente,
            "validees": commandes_validees,
            "ca_total": round(ca_total, 2)
        },
        "utilisateurs": {
            "total": total_users
        }
    })


@app.route("/api/admin/users", methods=["GET"])
@admin_requis
def get_all_users():
    """Liste tous les utilisateurs (admin only)."""
    utilisateurs = charger_utilisateurs()

    # Ne pas exposer les mots de passe hashés
    users_safe = []
    for user in utilisateurs:
        users_safe.append({
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "created_at": user["created_at"]
        })

    return jsonify({"utilisateurs": users_safe, "total": len(users_safe)})


@app.route("/api/admin/orders", methods=["GET"])
@admin_requis
def get_all_orders():
    """Liste toutes les commandes (admin only)."""
    commandes = charger_commandes()
    return jsonify({"commandes": commandes, "total": len(commandes)})


@app.route("/api/admin/orders/<int:id>/validate", methods=["POST"])
@admin_requis
def admin_validate_order(id):
    """Valider une commande (admin only)."""
    succes, message = valider_commande(id)

    if succes:
        return jsonify({"message": message})
    return jsonify({"erreur": message}), 400


@app.route("/api/admin/orders/<int:id>/cancel", methods=["POST"])
@admin_requis
def admin_cancel_order(id):
    """Annuler une commande (admin only)."""
    succes, message = annuler_commande(id)

    if succes:
        return jsonify({"message": message})
    return jsonify({"erreur": message}), 400


@app.route("/api/admin/products", methods=["POST"])
@admin_requis
def admin_create_product():
    """Créer un produit (admin only)."""
    data = request.get_json()

    champs_requis = ["nom", "description", "prix", "quantite"]
    if not data or not all(champ in data for champ in champs_requis):
        return jsonify({"erreur": "Champs requis: nom, description, prix, quantite"}), 400

    try:
        produits = charger_produits()
        nouveau = ajouter_produit(
            produits,
            data["nom"],
            data["description"],
            float(data["prix"]),
            int(data["quantite"])
        )
        return jsonify(nouveau), 201
    except ValueError:
        return jsonify({"erreur": "Prix ou quantité invalide"}), 400


@app.route("/api/admin/products/<int:id>", methods=["PUT"])
@admin_requis
def admin_update_product(id):
    """Modifier un produit (admin only)."""
    data = request.get_json()

    if not data:
        return jsonify({"erreur": "Données requises"}), 400

    produits = charger_produits()
    produit = trouver_produit(produits, id)

    if not produit:
        return jsonify({"erreur": "Produit introuvable"}), 404

    try:
        modifications = {}
        if "nom" in data:
            modifications["nom"] = data["nom"]
        if "description" in data:
            modifications["description"] = data["description"]
        if "prix" in data:
            modifications["prix"] = float(data["prix"])
        if "quantite" in data:
            modifications["quantite"] = int(data["quantite"])

        modifier_produit(produits, id, **modifications)
        return jsonify(trouver_produit(charger_produits(), id))
    except ValueError:
        return jsonify({"erreur": "Données invalides"}), 400


@app.route("/api/admin/products/<int:id>", methods=["DELETE"])
@admin_requis
def admin_delete_product(id):
    """Supprimer un produit (admin only)."""
    produits = charger_produits()

    if not trouver_produit(produits, id):
        return jsonify({"erreur": "Produit introuvable"}), 404

    supprimer_produit(produits, id)
    return jsonify({"message": "Produit supprimé"}), 200


@app.route("/api/admin/init", methods=["POST"])
def init_admin():
    """Créer le compte admin initial."""
    admin, message = creer_admin_initial()

    if admin:
        return jsonify({"message": message, "username": "admin", "password": "Admin123"}), 201
    return jsonify({"message": message}), 400


# ==================== LANCEMENT ====================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
