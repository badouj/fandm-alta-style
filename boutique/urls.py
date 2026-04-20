from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('panier/', views.panier, name='panier'),
    path('commande/', views.commande, name='commande'),
    path('produit/<int:pk>/', views.produit_detail, name='produit_detail'),

    # ADMIN CUSTOM
    path('mon-admin/login/', views.admin_login, name='admin_login'),
    path('mon-admin/logout/', views.admin_logout, name='admin_logout'),
    path('mon-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('mon-admin/produit/ajouter/', views.admin_produit_ajouter, name='admin_produit_ajouter'),
    path('mon-admin/produit/modifier/<int:pk>/', views.admin_produit_modifier, name='admin_produit_modifier'),
    path('mon-admin/produit/supprimer/<int:pk>/', views.admin_produit_supprimer, name='admin_produit_supprimer'),
    path('mon-admin/commande/<int:pk>/', views.admin_commande_detail, name='admin_commande_detail'),

    # STOCK
    path('mon-admin/stock/', views.admin_stock, name='admin_stock'),
    path('mon-admin/stock/ajouter/<int:produit_pk>/', views.admin_variant_ajouter, name='admin_variant_ajouter'),
    path('mon-admin/stock/supprimer/<int:pk>/', views.admin_variant_supprimer, name='admin_variant_supprimer'),
    path('mon-admin/stock/update/<int:pk>/', views.admin_stock_update, name='admin_stock_update'),
]