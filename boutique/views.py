# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Produit, ProduitVariant, ProduitImage, Commande, LigneCommande
import json
import requests as http_requests

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
            'couleur': v.couleur if v.couleur else produit.couleur,
            'stock': v.stock
        })
    variants_json = json.dumps(variants_data)
    couleurs = list(set(v.couleur if v.couleur else produit.couleur for v in variants if (v.couleur or produit.couleur)))
    couleurs.sort()
    return render(request, 'boutique/produit_detail.html', {
        'produit': produit,
        'variants': variants,
        'variants_json': variants_json,
        'images': images,
        'couleurs': couleurs,
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
                taille=item.get('taille', ''),
                couleur=item.get('couleur', '')
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
            couleur=request.POST.get('couleur', ''),
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
        produit.couleur = request.POST.get('couleur', '')
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
        couleur = request.POST.get('couleur', '').strip()
        stock = int(request.POST.get('stock', 0))
        variant, created = ProduitVariant.objects.get_or_create(
            produit=produit,
            taille=taille,
            couleur=couleur,
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


def inscription(request):
    error = None
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        if not nom or not email or not telephone or not password:
            error = "Veuillez remplir tous les champs."
        elif password != password2:
            error = "Les mots de passe ne correspondent pas."
        elif len(password) < 6:
            error = "Le mot de passe doit contenir au moins 6 caractères."
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=email).exists():
                error = "Un compte avec cet email existe déjà."
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=nom)
                login(request, user)
                return redirect('accueil')
    return render(request, 'boutique/inscription.html', {'error': error, 'success': False})


def connexion(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('accueil')
        else:
            error = "Email ou mot de passe incorrect."
    return render(request, 'boutique/connexion.html', {'error': error})


def deconnexion(request):
    logout(request)
    return redirect('accueil')


def favoris(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    return render(request, 'boutique/favoris.html')


@login_required(login_url='/mon-admin/login/')
def admin_commandes(request):
    commandes = Commande.objects.all().order_by('-date_commande')
    return render(request, 'boutique/admin_commandes.html', {'commandes': commandes})


@login_required(login_url='/mon-admin/login/')
def envoyer_first_delivery(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        token = '088a94c7-6b7a-4c98-911a-8bd3b6cca55d'

        designation = ', '.join([
            f"{l.produit.nom}{' - ' + l.couleur if l.couleur else ''}{' - ' + l.taille if l.taille else ''}"
            for l in commande.lignes.all()
        ])
        nombre_articles = sum(l.quantite for l in commande.lignes.all())

        adresse_parts = commande.adresse.split(' | ')
        gouvernerat = adresse_parts[0] if len(adresse_parts) > 0 else commande.adresse
        ville = adresse_parts[1] if len(adresse_parts) > 1 else commande.adresse
        adresse_comp = adresse_parts[2] if len(adresse_parts) > 2 else commande.adresse

        data = {
            "Client": {
                "nom": commande.nom_client,
                "gouvernerat": gouvernerat,
                "ville": ville,
                "adresse": adresse_comp,
                "telephone": commande.telephone,
                "telephone2": ""
            },
            "Produit": {
                "prix": float(commande.total),
                "designation": designation,
                "nombreArticle": nombre_articles,
                "commentaire": commande.notes or "",
                "article": designation,
                "nombreEchange": 0
            }
        }

        try:
            response = http_requests.post(
                'https://www.firstdeliverygroup.com/api/v2/create',
                json=data,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            result = response.json()
            if response.status_code == 200 and not result.get('isError'):
                commande.statut = 'confirme'
                commande.save()
                return redirect(f'/mon-admin/commande/{pk}/?success=1')
            else:
                msg = str(result.get('message', str(result)))[:100]
                return redirect(f'/mon-admin/commande/{pk}/?error={msg}')
        except Exception as e:
            return redirect(f'/mon-admin/commande/{pk}/?error={str(e)[:100]}')

    return redirect(f'/mon-admin/commande/{pk}/')