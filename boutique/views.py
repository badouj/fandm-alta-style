from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Produit, Commande, LigneCommande
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
    return render(request, 'boutique/produit_detail.html', {'produit': produit})

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
            LigneCommande.objects.create(
                commande=cmd,
                produit=produit,
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
        Produit.objects.create(
            nom=request.POST['nom'],
            description=request.POST['description'],
            prix=request.POST['prix'],
            categorie=request.POST['categorie'],
            sous_categorie=request.POST.get('sous_categorie', ''),
            tailles=request.POST.get('tailles', ''),
            image=request.FILES.get('image'),
            disponible='disponible' in request.POST
        )
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
        produit.tailles = request.POST.get('tailles', '')
        produit.disponible = 'disponible' in request.POST
        if request.FILES.get('image'):
            produit.image = request.FILES['image']
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