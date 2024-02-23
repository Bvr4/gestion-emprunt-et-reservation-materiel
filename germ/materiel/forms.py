from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import django_filters
from materiel.models import Materiel, Categorie, Emplacement, Utilisateur, Emprunt, Commentaire

class CreerMateriel(forms.ModelForm):
    class Meta:
        model = Materiel
        fields = ["nom", "categorie", "emplacement", "identifiant", "description"]

    def __init__(self, *args, **kwargs):
        super(CreerMateriel, self).__init__(*args, **kwargs)
        # On ajoute les balises htmx au champ catégorie, pour mettre à jour l'identifiant quand on selectionne une catégorie
        self.fields["categorie"].widget.attrs["hx-get"] = "/get-prochain-identifiant"
        self.fields["categorie"].widget.attrs["hx-trigger"] = "change"
        self.fields["categorie"].widget.attrs["hx-target"] = "#id_identifiant"
        self.fields["categorie"].widget.attrs["hx-swap"] = "outerHTML"

        if "initial" in kwargs and "identifiant" in kwargs["initial"]:
            self.fields["identifiant"].initial = kwargs["initial"]["identifiant"]

    def clean(self):
        cleaned_data = super().clean() 
        identifiant = cleaned_data.get("identifiant")
        categorie = cleaned_data.get("categorie")

        if Materiel.objects.filter(identifiant=identifiant).exists():
            raise forms.ValidationError({"identifiant": "Identifiant déjà utilisé. Veuillez en définir un nouveau"})
        
        if not identifiant.startswith(categorie.prefixe_identifiant):
            raise forms.ValidationError({"identifiant": "L'identifiant doit commencer par le préfixe de la catégorie à laquelle il appartient"})
        
        len_prefix = len(categorie.prefixe_identifiant)
        if not identifiant[len_prefix:].isdigit():
            raise forms.ValidationError({"identifiant": "L'identifiant doit contenir le préfixe de la catégorie à laquelle il appartient, puis une partie numérique"})

        return cleaned_data


class EditerMateriel(forms.ModelForm):
    class Meta:
        model = Materiel
        fields = ["nom", "categorie", "emplacement", "identifiant", "description", "empruntable"]

    def __init__(self, *args, **kwargs):
        super(EditerMateriel, self).__init__(*args, **kwargs)
        self.fields['identifiant'].widget.attrs['readonly'] = True
        

class CreationUtilisateur(forms.ModelForm):
    numero_telephone = forms.CharField(label="Numéro de téléphone", max_length=17)
    commune_residence = forms.CharField(label="Commune de résidence", max_length=50)

    class Meta:
        model = Utilisateur
        fields = ["numero_telephone", "commune_residence"]


class CreationUser(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]


class EditerUtilisateur(forms.ModelForm):
    numero_telephone = forms.CharField(label="Numéro de téléphone", max_length=17)
    commune_residence = forms.CharField(label="Commune de résidence", max_length=50)

    class Meta:
        model = Utilisateur
        fields = ["numero_telephone", "commune_residence", "peut_emprunter"]


class EditerUser(forms.ModelForm):
    username = forms.CharField(label="Nom d'utilisateur")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom de famille")
    email = forms.EmailField(required=True)
    # utilisateur = EditerUtilisateur()

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


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


class ReserverMaterielModerateur(forms.ModelForm):
    date_debut_resa = forms.DateField(label="Date de début de réservation", widget=forms.widgets.DateInput(attrs={"type": "date"}))
    date_fin_resa = forms.DateField(label="Date de fin de réservation", widget=forms.widgets.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Emprunt
        fields = ["utilisateur", "date_debut_resa", "date_fin_resa", "materiel"]

    def __init__(self, *args, **kwargs):
        super(ReserverMaterielModerateur, self).__init__(*args, **kwargs)
        if "initial" in kwargs and "materiel" in kwargs["initial"]:
            self.fields["materiel"].initial = kwargs["initial"]["materiel"]
            self.fields["materiel"].widget = forms.HiddenInput()


class CreerCommentaire(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ["titre", "texte"]


class CreerCategorie(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean() 
        nom = cleaned_data.get("nom")
        prefixe_identifiant = cleaned_data.get("prefixe_identifiant")

        if Categorie.objects.filter(nom=nom).exists():
            raise forms.ValidationError({"nom": "Cette catégorie existe déjà"})
        
        if Categorie.objects.filter(prefixe_identifiant=prefixe_identifiant).exists():
            raise forms.ValidationError({"prefixe_identifiant": "Une autre catégorie porte déjà ce préfixe"})
        
        return cleaned_data


class EditerCategorie(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean() 
        nom = cleaned_data.get("nom")
        prefixe_identifiant = cleaned_data.get("prefixe_identifiant")

        if Categorie.objects.filter(nom=nom).exists():
            raise forms.ValidationError({"nom": "Cette catégorie existe déjà"})
        
        if Categorie.objects.filter(prefixe_identifiant=prefixe_identifiant).exists():
            raise forms.ValidationError({"prefixe_identifiant": "Une autre catégorie porte déjà ce préfixe"})
        
        return cleaned_data


class CreerEmplacement(forms.ModelForm):
    class Meta:
        model = Emplacement
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean() 
        nom = cleaned_data.get("nom")

        if Emplacement.objects.filter(nom=nom).exists():
            raise forms.ValidationError({"nom": "Cette emplacement existe déjà"})
                
        return cleaned_data


class EditerEmplacement(forms.ModelForm):
    class Meta:
        model = Emplacement
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean() 
        nom = cleaned_data.get("nom")

        if Emplacement.objects.filter(nom=nom).exists():
            raise forms.ValidationError({"nom": "Cette emplacement existe déjà"})
                
        return cleaned_data
    

class FiltreMateriel(django_filters.FilterSet):
    DISPONIBILITE_CHOIX = [
        ('disponible', 'Disponible'),
        ('reserve', 'Réservé'),
        ('emprunte', 'Emprunté'),
    ]

    disponibilite = django_filters.ChoiceFilter(label='Disponibilité', choices=DISPONIBILITE_CHOIX, method='filtre_disponibilite')

    nom = django_filters.CharFilter(lookup_expr='icontains')

    # On filtrer en fonction du champ calculé 'disponibilite'
    def filtre_disponibilite(self, queryset, name, value):
        if value == 'disponible':
            filtered_ids = [materiel.id for materiel in queryset if materiel.disponibilite() == 'disponible']
            return Materiel.objects.filter(pk__in=filtered_ids)
        elif value == 'emprunte':
            filtered_ids = [materiel.id for materiel in queryset if materiel.disponibilite() == 'emprunté']
            return Materiel.objects.filter(pk__in=filtered_ids)
        elif value == 'reserve':
            filtered_ids = [materiel.id for materiel in queryset if materiel.disponibilite() == 'réservé']
            return Materiel.objects.filter(pk__in=filtered_ids)
        else:
            return queryset
    
    class Meta:
        model = Materiel
        fields = ['nom', 'categorie', 'emplacement', 'disponibilite']