from django.contrib import admin
from .models import Produit, ProduitVariant, Commande, LigneCommande

class ProduitVariantInline(admin.TabularInline):
    model = ProduitVariant
    extra = 1
    fields = ['couleur', 'taille', 'stock']

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'sous_categorie', 'prix', 'disponible', 'stock_total']
    list_filter = ['categorie', 'sous_categorie', 'disponible']
    search_fields = ['nom']
    list_editable = ['disponible', 'prix']
    inlines = [ProduitVariantInline]

@admin.register(ProduitVariant)
class ProduitVariantAdmin(admin.ModelAdmin):
    list_display = ['produit', 'couleur', 'taille', 'stock']
    list_filter = ['couleur', 'taille']
    list_editable = ['stock']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_client', 'telephone', 'total', 'statut', 'date_commande']
    list_filter = ['statut']
    search_fields = ['nom_client', 'telephone']
    list_editable = ['statut']
    inlines = [LigneCommandeInline]

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'produit', 'couleur', 'taille', 'quantite', 'prix_unitaire']