# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Produit, ProduitVariant, ProduitImage, Commande, LigneCommande
import json

def accueil(request):
    produits = Produit.objects.filter(disponible=True)[:3]
    return render(request, 'boutique/accueil.html', {'produits': produits})

def catalogue(request):
    categorie = request.GET.get('cat', 'all')
    sous_categorie = request.GET.get('sous', '')
    if categorie == 'all':
        produits = Produit.objects.filter(disponible=True)
    elif sous_categorie:
        produits = Produit.objects.filter(disponible=True, categorie=categorie, sous_categorie=sous_categorie)
    else:
        produits = Produit.objects.filter(disponible=True, categorie=categorie)
    return render(request, 'boutique/catalogue.html', {
        'produits': produits,
        'categorie': categorie,
        'sous_categorie': sous_categorie
    })

def panier(request):
    return render(request, 'boutique/panier.html')

def produit_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    variants = produit.variants.filter(stock__gt=0)
    images = list(produit.images.all())
    variants_data = []
    for v in variants:
        variants_data.append({
            'id': v.id,
            'taille': v.taille,
            'stock': v.stock
        })
    variants_json = json.dumps(variants_data)
    return render(request, 'boutique/produit_detail.html', {
        'produit': produit,
        'variants': variants,
        'variants_json': variants_json,
        'images': images,
    })

def commande(request):
    if request.method == 'POST':
        panier_data = json.loads(request.POST.get('panier', '[]'))
        if not panier_data:
            return redirect('panier')
        total = sum(item['prix'] * item['qty'] for item in panier_data)
        cmd = Commande.objects.create(
            nom_client=request.POST['nom'],
            telephone=request.POST['telephone'],
            adresse=request.POST['adresse'],
            notes=request.POST.get('notes', ''),
            total=total
        )
        for item in panier_data:
            produit = Produit.objects.get(id=item['id'])
            variant = None
            if item.get('variant_id'):
                try:
                    variant = ProduitVariant.objects.get(id=item['variant_id'])
                    if variant.stock >= item['qty']:
                        variant.stock -= item['qty']
                        variant.save()
                except ProduitVariant.DoesNotExist:
                    pass
            LigneCommande.objects.create(
                commande=cmd,
                produit=produit,
                variant=variant,
                quantite=item['qty'],
                prix_unitaire=item['prix'],
                taille=item.get('taille', '')
            )
        return render(request, 'boutique/success.html', {'commande': cmd})
    return render(request, 'boutique/commande.html')

def admin_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Identifiants incorrects ou accès refusé."
    return render(request, 'boutique/admin_login.html', {'error': error})

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url='/mon-admin/login/')
def admin_dashboard(request):
    produits = Produit.objects.all()
    commandes = Commande.objects.all().order_by('-date_commande')
    return render(request, 'boutique/admin_dashboard.html', {
        'produits': produits,
        'commandes': commandes
    })

@login_required(login_url='/mon-admin/login/')
def admin_produit_ajouter(request):
    if request.method == 'POST':
        produit = Produit.objects.create(
            nom=request.POST['nom'],
            description=request.POST['description'],
            prix=request.POST['prix'],
            categorie=request.POST['categorie'],
            sous_categorie=request.POST.get('sous_categorie', ''),
            image=request.FILES.get('image'),
            disponible='disponible' in request.POST
        )
        for img in request.FILES.getlist('images'):
            ProduitImage.objects.create(produit=produit, image=img)
        return redirect('admin_dashboard')
    return render(request, 'boutique/admin_produit_form.html', {'action': 'Ajouter'})

@login_required(login_url='/mon-admin/login/')
def admin_produit_modifier(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.nom = request.POST['nom']
        produit.description = request.POST['description']
        produit.prix = request.POST['prix']
        produit.categorie = request.POST['categorie']
        produit.sous_categorie = request.POST.get('sous_categorie', '')
        produit.disponible = 'disponible' in request.POST
        if request.FILES.get('image'):
            produit.image = request.FILES['image']
        for img in request.FILES.getlist('images'):
            ProduitImage.objects.create(produit=produit, image=img)
        produit.save()
        return redirect('admin_dashboard')
    return render(request, 'boutique/admin_produit_form.html', {
        'action': 'Modifier',
        'produit': produit
    })

@login_required(login_url='/mon-admin/login/')
def admin_produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('admin_dashboard')
    return render(request, 'boutique/admin_supprimer.html', {'produit': produit})

@login_required(login_url='/mon-admin/login/')
def admin_commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        commande.statut = request.POST['statut']
        commande.save()
        return redirect('admin_commande_detail', pk=pk)
    return render(request, 'boutique/admin_commande_detail.html', {'commande': commande})

@login_required(login_url='/mon-admin/login/')
def admin_stock(request):
    produits = Produit.objects.all().prefetch_related('variants')
    return render(request, 'boutique/admin_stock.html', {'produits': produits})

@login_required(login_url='/mon-admin/login/')
def admin_variant_ajouter(request, produit_pk):
    produit = get_object_or_404(Produit, pk=produit_pk)
    if request.method == 'POST':
        taille = request.POST.get('taille', '').strip()
        stock = int(request.POST.get('stock', 0))
        variant, created = ProduitVariant.objects.get_or_create(
            produit=produit,
            taille=taille,
            defaults={'stock': stock}
        )
        if not created:
            variant.stock = stock
            variant.save()
        return redirect('admin_stock')
    return render(request, 'boutique/admin_variant_form.html', {'produit': produit})

@login_required(login_url='/mon-admin/login/')
def admin_variant_supprimer(request, pk):
    variant = get_object_or_404(ProduitVariant, pk=pk)
    if request.method == 'POST':
        variant.delete()
    return redirect('admin_stock')

@login_required(login_url='/mon-admin/login/')
def admin_stock_update(request, pk):
    variant = get_object_or_404(ProduitVariant, pk=pk)
    if request.method == 'POST':
        variant.stock = int(request.POST.get('stock', 0))
        variant.save()
    return redirect('admin_stock')

@login_required(login_url='/mon-admin/login/')
def admin_image_supprimer(request, pk):
    image = get_object_or_404(ProduitImage, pk=pk)
    produit_pk = image.produit.pk
    image.delete()
    return redirect('admin_produit_modifier', pk=produit_pk)