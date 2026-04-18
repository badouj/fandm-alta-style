from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('panier/', views.panier, name='panier'),
    path('commande/', views.commande, name='commande'),
]
urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('panier/', views.panier, name='panier'),
    path('commande/', views.commande, name='commande'),

    # ADMIN CUSTOM
    path('mon-admin/login/', views.admin_login, name='admin_login'),
    path('mon-admin/logout/', views.admin_logout, name='admin_logout'),
    path('mon-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('mon-admin/produit/ajouter/', views.admin_produit_ajouter, name='admin_produit_ajouter'),
    path('mon-admin/produit/modifier/<int:pk>/', views.admin_produit_modifier, name='admin_produit_modifier'),
    path('mon-admin/produit/supprimer/<int:pk>/', views.admin_produit_supprimer, name='admin_produit_supprimer'),
    path('mon-admin/commande/<int:pk>/', views.admin_commande_detail, name='admin_commande_detail'),
    path('produit/<int:pk>/', views.produit_detail, name='produit_detail'),
]