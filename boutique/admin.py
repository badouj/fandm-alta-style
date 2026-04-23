from django.contrib import admin
from .models import Produit, ProduitVariant, ProduitImage, Commande, LigneCommande

class ProduitVariantInline(admin.TabularInline):
    model = ProduitVariant
    extra = 1
    fields = ['taille', 'stock']

class ProduitImageInline(admin.TabularInline):
    model = ProduitImage
    extra = 3

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'sous_categorie', 'prix', 'disponible', 'stock_total']
    list_filter = ['categorie', 'sous_categorie', 'disponible']
    search_fields = ['nom']
    list_editable = ['disponible', 'prix']
    inlines = [ProduitVariantInline, ProduitImageInline]

@admin.register(ProduitVariant)
class ProduitVariantAdmin(admin.ModelAdmin):
    list_display = ['produit', 'taille', 'stock']
    list_filter = ['taille']
    list_editable = ['stock']

@admin.register(ProduitImage)
class ProduitImageAdmin(admin.ModelAdmin):
    list_display = ['produit', 'image']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_client', 'telephone', 'total', 'statut', 'date_commande']
    list_filter = ['statut']
    search_fields = ['nom_client', 'telephone']
    list_editable = ['statut']
    inlines = [LigneCommandeInline]

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'produit', 'taille', 'quantite', 'prix_unitaire']