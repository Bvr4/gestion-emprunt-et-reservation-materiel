from django.contrib import admin
from materiel.models import Emplacement, Categorie, Materiel, Emprunt

# Définition des affichages dans l'interface admin
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'commune')

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prefixe_identifiant')

class MaterielAdmin(admin.ModelAdmin):
    list_display = ('nom', 'identifiant', 'categorie', 'emplacement', 'empruntable')

admin.site.register(Emplacement, EmplacementAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Materiel, MaterielAdmin)
admin.site.register(Emprunt)