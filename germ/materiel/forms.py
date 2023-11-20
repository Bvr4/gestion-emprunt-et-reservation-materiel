from django import forms
from materiel.models import Materiel, Categorie, Utilisateur, Emprunt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreerMateriel(forms.ModelForm):
    class Meta:
        model = Materiel
        fields = ["nom", "identifiant", "description", "categorie", "emplacement"]
    
    def clean_identifiant(self):
        identifiant = self.cleaned_data.get("identifiant")

        if Materiel.objects.filter(identifiant=identifiant).first():
            raise forms.ValidationError("Identifiant déjà utilisé. Veuillez en définir un nouveau")

        return identifiant

    def clean(self):
        identifiant = self.cleaned_data.get("identifiant")
        categorie = self.cleaned_data.get("categorie")
        
        if not identifiant.startswith(categorie.prefixe_identifiant):
            raise forms.ValidationError({"identifiant": "L'identifiant doit commencer par le préfixe de la catégorie à laquelle il appartient"})


class EditerMateriel(forms.ModelForm):
    identifiant = forms.CharField(disabled=True)

    class Meta:
        model = Materiel
        fields = "__all__"
        

class CreationUtilisateur(forms.ModelForm):
    numero_telephone = forms.CharField(label="Numéro de téléphone", max_length=17)
    commune_residence = forms.CharField(label="Commune de résidence", max_length=50)

    class Meta:
        model = Utilisateur
        fields = "numero_telephone", "commune_residence"


class CreationUser(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]


class ReserverMateriel(forms.ModelForm):
    date_debut_resa = forms.DateField(label="Date de début de réservation", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    date_fin_resa = forms.DateField(label="Date de fin de réservation", widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Emprunt
        fields = ["date_debut_resa", "date_fin_resa"]

    def clean(self):
        date_debut_resa = self.cleaned_data.get("date_debut_resa")
        date_fin_resa = self.cleaned_data.get("date_fin_resa")

        if date_fin_resa < date_debut_resa: 
            raise forms.ValidationError({"date_fin_resa": "La date de fin de reservation doit être ultérieure à la date de début de réservation"})
        
        # Vérifier s'il existe des réservations qui chevauchent la période d'emprunt demandée
        resa_chevauche_debut = Emprunt.objects.filter(
            date_debut_resa__lte=date_debut_resa,
            date_fin_resa__gte=date_debut_resa
        )
        resa_chevauche_fin = Emprunt.objects.filter(
            date_debut_resa__lte=date_fin_resa,
            date_fin_resa__gte=date_fin_resa
        )

        if resa_chevauche_debut.exists():
            raise forms.ValidationError({"date_debut_resa": "Une réservation existe déjà à la date demandée."})
        
        if resa_chevauche_fin.exists():
            raise forms.ValidationError({"date_fin_resa": "Une réservation existe déjà à la date demandée."})

