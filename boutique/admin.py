from django.contrib import admin
from .models import Produit, Commande, LigneCommande

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix', 'disponible']
    list_filter = ['categorie', 'disponible']
    search_fields = ['nom']
    list_editable = ['disponible', 'prix']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_client', 'telephone', 'total', 'statut', 'date_commande']
    list_filter = ['statut']
    search_fields = ['nom_client', 'telephone']
    list_editable = ['statut']
    inlines = [LigneCommandeInline]

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'produit', 'quantite', 'prix_unitaire']