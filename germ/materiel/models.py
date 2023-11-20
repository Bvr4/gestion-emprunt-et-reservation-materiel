from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Emplacement où se trouve le matériel (batiment)
class Emplacement(models.Model):
    nom = models.CharField(max_length=80)
    commune = models.CharField(max_length=80)

    # permet d'avoir le nom visible dans l'interface d'admin django
    def __str__(self) -> str:
        return self.nom


# Catégorie à laquelle appartiens le matériel
class Categorie(models.Model):
    nom = models.CharField(max_length=80)
    prefixe_identifiant = models.CharField(max_length=8)
    
    # permet d'avoir le nom visible dans l'interface d'admin django
    def __str__(self) -> str:
        return self.nom + " [" + self.prefixe_identifiant + "]"


# Matériel empruntable
class Materiel(models.Model):
    nom = models.CharField(max_length=80)
    identifiant = models.CharField(max_length=10)
    description = models.TextField(default=None, blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.RESTRICT)
    emplacement = models.ForeignKey(Emplacement, on_delete=models.RESTRICT)
    empruntable = models.BooleanField(default=True)

    # permet d'avoir le nom visible dans l'interface d'admin django
    def __str__(self) -> str:
        return self.nom


# Utilisateur
class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Le numéro de téléphone doit être au format: '+33612345678'.")
    numero_telephone = models.CharField(validators=[telephone_regex], max_length=17, blank=True)
    commune_residence = models.CharField(max_length=50, blank=True)
    est_moderateur = models.BooleanField(default=False)
    peut_emprunter = models.BooleanField(default=True)

    # permet d'avoir le nom visible dans l'interface d'admin django
    def __str__(self) -> str:
        return self.user.username


# Emprunt et réservation d'un matériel par un usager
class Emprunt(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    date_debut_resa = models.DateField()
    date_fin_resa = models.DateField()
    date_debut_emprunt = models.DateField(null=True)
    date_fin_emprunt = models.DateField(null=True)
    cloture = models.BooleanField(default=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

