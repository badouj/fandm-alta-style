from django.db import models

class Produit(models.Model):
    CATEGORIES = [
        ('femme', 'Femme'),
        ('homme', 'Homme'),
        ('enfants', 'Enfants'),
    ]

    SOUS_CATEGORIES = [
        ('jebba_f', 'Jebba Femme'),
        ('dengri_f', 'Dengri Femme'),
        ('kachabiya_f', 'Kachabiya Femme'),
        ('cape', 'Cape'),
        ('kamis_f', 'Kamis Femme'),
        ('herga_h', 'Herga Homme'),
        ('dengri_h', 'Dengri Homme'),
        ('burnous', 'Burnous'),
        ('jebba_e', 'Jebba Enfant'),
        ('dengri_e', 'Dengri Enfant'),
        ('kachabiya_e', 'Kachabiya Enfant'),
        ('herga_e', 'Herga Enfant'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=3)
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    sous_categorie = models.CharField(max_length=50, choices=SOUS_CATEGORIES, blank=True, default='')
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    def stock_total(self):
        return sum(v.stock for v in self.variants.all())


class ProduitVariant(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='variants')
    couleur = models.CharField(max_length=100)
    taille = models.CharField(max_length=20)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.produit.nom} - {self.couleur} - {self.taille}"

    class Meta:
        unique_together = ['produit', 'couleur', 'taille']


class Commande(models.Model):
    STATUTS = [
        ('nouveau', 'Nouveau'),
        ('confirme', 'Confirmé'),
        ('livre', 'Livré'),
        ('annule', 'Annulé'),
    ]

    nom_client = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    notes = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='nouveau')
    total = models.DecimalField(max_digits=10, decimal_places=3)
    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.nom_client}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProduitVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)
    couleur = models.CharField(max_length=100, blank=True, default='')
    taille = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"