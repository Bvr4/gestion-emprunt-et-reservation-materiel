from django.contrib import admin
from materiel.models import Emplacement, Categorie, Materiel, Emprunt, Utilisateur, Commentaire

# Définition des affichages dans l'interface admin
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'commune')

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prefixe_identifiant')

class MaterielAdmin(admin.ModelAdmin):
    list_display = ('nom', 'identifiant', 'categorie', 'emplacement', 'empruntable')

class EmpruntAdmin(admin.ModelAdmin):
    list_display = ('materiel', 'utilisateur', 'date_debut_resa', 'date_fin_resa', 'date_debut_emprunt', 'date_fin_emprunt', 'cloture')

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_telephone', 'commune_residence', 'est_moderateur', 'peut_emprunter')

class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('materiel', 'auteur', 'titre', 'texte', 'date')

admin.site.register(Emplacement, EmplacementAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Materiel, MaterielAdmin)
admin.site.register(Emprunt, EmpruntAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Commentaire, CommentaireAdmin)