import tkinter as tk
from tkinter import ttk, messagebox
from modules.auth import creer_compte, verifier_connexion
from modules.produits import (
    charger_produits,
    ajouter_produit,
    modifier_produit,
    supprimer_produit,
    trouver_produit
)


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E-Commerce Manager")
        self.root.geometry("800x600")
        self.utilisateur_connecte = None
        
        # Afficher l'écran de connexion au démarrage
        self.afficher_ecran_connexion()
    
    def lancer(self):
        self.root.mainloop()
    
    def nettoyer_fenetre(self):
        """Supprime tous les widgets de la fenêtre."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ==================== ÉCRAN DE CONNEXION ====================
    
    def afficher_ecran_connexion(self):
        """Affiche l'écran de connexion."""
        self.nettoyer_fenetre()
        self.root.geometry("400x350")
        
        # Frame principal
        frame = ttk.Frame(self.root, padding="30")
        frame.pack(expand=True)
        
        # Titre
        ttk.Label(frame, text="Connexion", font=("Helvetica", 20, "bold")).pack(pady=(0, 20))
        
        # Username
        ttk.Label(frame, text="Nom d'utilisateur :").pack(anchor="w")
        self.entry_username = ttk.Entry(frame, width=30)
        self.entry_username.pack(pady=(0, 10))
        
        # Password
        ttk.Label(frame, text="Mot de passe :").pack(anchor="w")
        self.entry_password = ttk.Entry(frame, width=30, show="*")
        self.entry_password.pack(pady=(0, 20))
        
        # Boutons
        ttk.Button(frame, text="Se connecter", command=self.connexion).pack(fill="x", pady=5)
        ttk.Button(frame, text="Créer un compte", command=self.afficher_ecran_inscription).pack(fill="x")
    
    def connexion(self):
        """Gère la connexion."""
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        user, message = verifier_connexion(username, password)
        
        if user:
            self.utilisateur_connecte = user
            messagebox.showinfo("Succès", message)
            self.afficher_ecran_principal()
        else:
            messagebox.showerror("Erreur", message)
    
    # ==================== ÉCRAN D'INSCRIPTION ====================
    
    def afficher_ecran_inscription(self):
        """Affiche l'écran d'inscription."""
        self.nettoyer_fenetre()
        self.root.geometry("400x400")
        
        frame = ttk.Frame(self.root, padding="30")
        frame.pack(expand=True)
        
        ttk.Label(frame, text="Créer un compte", font=("Helvetica", 20, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Nom d'utilisateur :").pack(anchor="w")
        self.entry_new_username = ttk.Entry(frame, width=30)
        self.entry_new_username.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Mot de passe :").pack(anchor="w")
        self.entry_new_password = ttk.Entry(frame, width=30, show="*")
        self.entry_new_password.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Confirmer mot de passe :").pack(anchor="w")
        self.entry_confirm_password = ttk.Entry(frame, width=30, show="*")
        self.entry_confirm_password.pack(pady=(0, 20))
        
        # Info mot de passe
        ttk.Label(frame, text="Min. 8 caractères, 1 majuscule, 1 chiffre", 
                  font=("Helvetica", 9), foreground="gray").pack()
        
        ttk.Button(frame, text="Créer le compte", command=self.inscription).pack(fill="x", pady=(15, 5))
        ttk.Button(frame, text="Retour", command=self.afficher_ecran_connexion).pack(fill="x")
    
    def inscription(self):
        """Gère l'inscription."""
        username = self.entry_new_username.get()
        password = self.entry_new_password.get()
        confirm = self.entry_confirm_password.get()
        
        if not username or not password or not confirm:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        
        user, message = creer_compte(username, password)
        
        if user:
            messagebox.showinfo("Succès", message)
            self.afficher_ecran_connexion()
        else:
            messagebox.showerror("Erreur", message)
    
    # ==================== ÉCRAN PRINCIPAL ====================
    
    def afficher_ecran_principal(self):
        """Affiche l'écran principal de gestion."""
        self.nettoyer_fenetre()
        self.root.geometry("900x600")
        
        # Barre de menu
        menu_frame = ttk.Frame(self.root, padding="10")
        menu_frame.pack(fill="x")
        
        ttk.Label(menu_frame, text=f"Bienvenue, {self.utilisateur_connecte['username']}", 
                  font=("Helvetica", 12)).pack(side="left")
        ttk.Button(menu_frame, text="Déconnexion", command=self.deconnexion).pack(side="right")
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Liste des produits
        ttk.Label(main_frame, text="Liste des produits", font=("Helvetica", 14, "bold")).pack(anchor="w")
        
        # Treeview pour afficher les produits
        columns = ("ID", "Nom", "Description", "Prix", "Stock")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.column("ID", width=50)
        self.tree.column("Prix", width=80)
        self.tree.column("Stock", width=80)
        
        self.tree.pack(fill="both", expand=True, pady=10)
        
        # Boutons d'action
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Ajouter", command=self.popup_ajouter).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Modifier", command=self.popup_modifier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Supprimer", command=self.supprimer_selection).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Actualiser", command=self.rafraichir_liste).pack(side="left", padx=5)
        
        # Charger les produits
        self.rafraichir_liste()
    
    def rafraichir_liste(self):
        """Met à jour la liste des produits."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        produits = charger_produits()
        for p in produits:
            self.tree.insert("", "end", values=(p["id"], p["nom"], p["description"], f"{p['prix']:.2f}€", p["quantite"]))
    
    def deconnexion(self):
        """Déconnecte l'utilisateur."""
        self.utilisateur_connecte = None
        self.afficher_ecran_connexion()
    
    def popup_ajouter(self):
        """Ouvre une popup pour ajouter un produit."""
        popup = tk.Toplevel(self.root)
        popup.title("Ajouter un produit")
        popup.geometry("350x280")
        popup.grab_set()
        
        frame = ttk.Frame(popup, padding="20")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Nom :").pack(anchor="w")
        entry_nom = ttk.Entry(frame, width=35)
        entry_nom.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Description :").pack(anchor="w")
        entry_desc = ttk.Entry(frame, width=35)
        entry_desc.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Prix :").pack(anchor="w")
        entry_prix = ttk.Entry(frame, width=35)
        entry_prix.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Quantité :").pack(anchor="w")
        entry_qte = ttk.Entry(frame, width=35)
        entry_qte.pack(pady=(0, 15))
        
        def sauvegarder():
            try:
                produits = charger_produits()
                ajouter_produit(produits, entry_nom.get(), entry_desc.get(), 
                               float(entry_prix.get()), int(entry_qte.get()))
                self.rafraichir_liste()
                popup.destroy()
                messagebox.showinfo("Succès", "Produit ajouté.")
            except ValueError:
                messagebox.showerror("Erreur", "Prix ou quantité invalide.")
        
        ttk.Button(frame, text="Sauvegarder", command=sauvegarder).pack(fill="x")
    
    def popup_modifier(self):
        """Ouvre une popup pour modifier un produit."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un produit.")
            return
        
        item = self.tree.item(selection[0])
        id_produit = item["values"][0]
        produits = charger_produits()
        produit = trouver_produit(produits, id_produit)
        
        popup = tk.Toplevel(self.root)
        popup.title("Modifier un produit")
        popup.geometry("350x280")
        popup.grab_set()
        
        frame = ttk.Frame(popup, padding="20")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Nom :").pack(anchor="w")
        entry_nom = ttk.Entry(frame, width=35)
        entry_nom.insert(0, produit["nom"])
        entry_nom.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Description :").pack(anchor="w")
        entry_desc = ttk.Entry(frame, width=35)
        entry_desc.insert(0, produit["description"])
        entry_desc.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Prix :").pack(anchor="w")
        entry_prix = ttk.Entry(frame, width=35)
        entry_prix.insert(0, str(produit["prix"]))
        entry_prix.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Quantité :").pack(anchor="w")
        entry_qte = ttk.Entry(frame, width=35)
        entry_qte.insert(0, str(produit["quantite"]))
        entry_qte.pack(pady=(0, 15))
        
        def sauvegarder():
            try:
                modifier_produit(produits, id_produit, nom=entry_nom.get(), description=entry_desc.get(),
                                prix=float(entry_prix.get()), quantite=int(entry_qte.get()))
                self.rafraichir_liste()
                popup.destroy()
                messagebox.showinfo("Succès", "Produit modifié.")
            except ValueError:
                messagebox.showerror("Erreur", "Prix ou quantité invalide.")
        
        ttk.Button(frame, text="Sauvegarder", command=sauvegarder).pack(fill="x")
    
    def supprimer_selection(self):
        """Supprime le produit sélectionné."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un produit.")
            return
        
        if messagebox.askyesno("Confirmation", "Supprimer ce produit ?"):
            item = self.tree.item(selection[0])
            id_produit = item["values"][0]
            produits = charger_produits()
            supprimer_produit(produits, id_produit)
            self.rafraichir_liste()
            messagebox.showinfo("Succès", "Produit supprimé.")


if __name__ == "__main__":
    app = Application()
    app.lancer()