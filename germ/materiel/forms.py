from django import forms
from materiel.models import Materiel, Categorie, Utilisateur, Emprunt, Commentaire
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
    class Meta:
        model = Materiel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EditerMateriel, self).__init__(*args, **kwargs)
        self.fields['identifiant'].widget.attrs['readonly'] = True
        

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
    date_debut_resa = forms.DateField(label="Date de début de réservation", widget=forms.widgets.DateInput(attrs={"type": "date"}))
    date_fin_resa = forms.DateField(label="Date de fin de réservation", widget=forms.widgets.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Emprunt
        fields = ["date_debut_resa", "date_fin_resa", "materiel"]

    def __init__(self, *args, **kwargs):
        super(ReserverMateriel, self).__init__(*args, **kwargs)
        if "initial" in kwargs and "materiel" in kwargs["initial"]:
            self.fields["materiel"].initial = kwargs["initial"]["materiel"]
            self.fields["materiel"].widget = forms.HiddenInput()


class CreerCommentaire(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ["titre", "texte"]