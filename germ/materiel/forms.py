from django import forms
from materiel.models import Materiel, Categorie

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
    identifiant = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Materiel
        fields = "__all__"
    
