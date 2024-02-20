import datetime as dt
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

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
    
    # Permet de savoir si le matériel est actuellement réservé
    def est_reserve(self):
        date_du_jour = dt.date.today()
        if Emprunt.objects.filter(materiel=self, cloture=False,
            date_debut_resa__lte=date_du_jour).exists():
            return True
        return False
        
    # Permet de savoir si le matériel est actuellement emprunté
    def est_emprunte(self):
        date_du_jour = dt.date.today()
        if Emprunt.objects.filter(materiel=self, cloture=False,            
            date_debut_resa__lte=date_du_jour,
            date_debut_emprunt__lte=date_du_jour).exists():
            return True
        return False
    

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
    
    # On surcharge la methode save pour pouvoir gérer les groupes de permissions en fonction des booléens
    def save(self, *args, **kwargs):
        super(Utilisateur, self).save(*args, **kwargs)

        groupe_usagers = Group.objects.get(name='usagers')
        groupe_emprunteurs= Group.objects.get(name='emprunteurs')
        groupe_moderateurs = Group.objects.get(name='moderateurs')

        self.user.groups.add(groupe_usagers)

        if self.peut_emprunter:
            self.user.groups.add(groupe_emprunteurs)
        else:
            self.user.groups.remove(groupe_emprunteurs)

        if self.est_moderateur:
            self.user.groups.add(groupe_moderateurs)
        else:
            self.user.groups.remove(groupe_moderateurs)

    # Permet de tester si un utilisateur a des emprunts en cours
    def has_emprunts_en_cours(self):
        if Emprunt.objects.filter(utilisateur=self, cloture=False,
            date_debut_emprunt__isnull=False,
            date_fin_emprunt__isnull=True).exists():
            return True
        return False

    # Teste si l'utilisateur à des réservation en cours ou dans le futur
    def has_resa_en_cours(self):
        date_du_jour = dt.date.today()
        if Emprunt.objects.filter(utilisateur=self, cloture=False,
            date_debut_resa__lte=date_du_jour).exists():
            return True
        return False

# Emprunt et réservation d'un matériel par un usager
class Emprunt(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    date_debut_resa = models.DateField()
    date_fin_resa = models.DateField()
    date_debut_emprunt = models.DateField(null=True)
    date_fin_emprunt = models.DateField(null=True)
    cloture = models.BooleanField(default=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    def clean(self):
        date_du_jour = dt.date.today()

        if self.date_fin_resa < date_du_jour:
            raise ValidationError({"date_fin_resa": "La date de fin de réservation ne peut être antérieure à la date du jour"})
        
        if self.date_fin_resa < self.date_debut_resa: 
            raise ValidationError("La date de fin de reservation doit être ultérieure à la date de début de réservation")
        
        # Vérifier s'il existe des réservations qui chevauchent la période d'emprunt demandée
        resa_chevauche_debut = Emprunt.objects.filter(
            materiel=self.materiel,
            cloture=False,
            date_debut_resa__lte=self.date_debut_resa,
            date_fin_resa__gte=self.date_debut_resa
        ).exclude(pk=self.pk)
        resa_chevauche_fin = Emprunt.objects.filter(
            materiel=self.materiel,
            cloture=False,
            date_debut_resa__lte=self.date_fin_resa,
            date_fin_resa__gte=self.date_fin_resa
        ).exclude(pk=self.pk)

        if resa_chevauche_debut.exists():
            raise ValidationError({"date_debut_resa": "Une réservation existe déjà à la date demandée."})
        
        if resa_chevauche_fin.exists():
            raise ValidationError({"date_fin_resa": "Une réservation existe déjà à la date demandée."})


# Commentaires, liés à un matériel 
class Commentaire(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.RESTRICT)
    titre = models.CharField(max_length=80)
    texte = models.TextField()
    date = models.DateTimeField()
