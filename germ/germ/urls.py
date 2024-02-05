from django.contrib import admin
from django.urls import include, path
import materiel.views as mviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('creer-compte', mviews.creer_compte, name='creer-compte'),
    path('', mviews.index, name='home'),
    path('materiel/<int:materiel_pk>', mviews.materiel, name='materiel'),
    path('creer-materiel/', mviews.creer_materiel, name='creer-materiel'),
    path('editer-materiel/<int:materiel_pk>', mviews.editer_materiel, name='editer-materiel'),
    path('supprimer-materiel/<int:materiel_pk>', mviews.supprimer_materiel, name='supprimer-materiel'),
    path('reserver-materiel/<int:materiel_pk>', mviews.reserver_materiel, name='reserver-materiel'),
    path('reserver-materiel-bouton/<int:materiel_pk>', mviews.reserver_materiel_bouton, name='reserver-materiel-bouton'),
    path('emprunter-materiel-bouton/<int:emprunt_pk>', mviews.emprunter_materiel_bouton, name='emprunter-materiel-bouton'),
    path('utilisateur/<int:utilisateur_pk>', mviews.utilisateur, name='utilisateur'),
    path('utilisateur-peut-emprunter/<int:utilisateur_pk>', mviews.utilisateur_peut_emprunter, name='utilisateur-peut-emprunter'),
    path('creer-commentaire/<int:materiel_pk>', mviews.creer_commentaire, name='creer-commentaire'),
    path('creer-commentaire-bouton/<int:materiel_pk>', mviews.creer_commentaire_bouton, name='creer-commentaire-bouton'),
    path('get-prochain-identifiant/', mviews.get_prochain_identifiant, name='get-prochain-identifiant'),
    path('categories', mviews.categories, name='categories'),
    path('categorie/<int:categorie_pk>', mviews.categorie, name='categorie'),
    path('creer-categorie/', mviews.creer_categorie, name='creer-categorie'),
    path('editer-categorie/<int:categorie_pk>', mviews.editer_categorie, name='editer-categorie'),
    path('supprimer-categorie/<int:categorie_pk>', mviews.supprimer_categorie, name='supprimer-categorie'),
    path('emplacements', mviews.emplacements, name='emplacements'),
    path('emplacement/<int:emplacement_pk>', mviews.emplacement, name='emplacement'),
    path('creer-emplacement/', mviews.creer_emplacement, name='creer-emplacement'),
    path('editer-emplacement/<int:emplacement_pk>', mviews.editer_emplacement, name='editer-emplacement'),
    path('supprimer-emplacement/<int:emplacement_pk>', mviews.supprimer_emplacement, name='supprimer-emplacement'),
]
