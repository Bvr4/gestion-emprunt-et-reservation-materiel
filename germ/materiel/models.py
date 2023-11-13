from django.db import models

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


# Emprunt et réservation d'un matériel par un usager
class Emprunt(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    date_debut_resa = models.DateField()
    date_fin_resa = models.DateField()
    date_debut_emprunt = models.DateField()
    date_fin_emprunt = models.DateField()
    cloture = models.BooleanField(default=False)
    # utilisateur = models.ForeignKey(.....)  # >>> On verra ça plus tard