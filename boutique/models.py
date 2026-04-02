from django.db import models

class Produit(models.Model):
    CATEGORIES = [
        ('jebba', 'Jebba'),
        ('burnous', 'Burnous'),
        ('kaftan', 'Kaftan'),
        ('accessoire', 'Accessoire'),
    ]
    
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=3)
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


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
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"