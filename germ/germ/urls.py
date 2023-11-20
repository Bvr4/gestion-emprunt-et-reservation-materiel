from django.contrib import admin
from django.urls import include, path
import materiel.views as mviews

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('creer-compte', mviews.creer_compte, name='creer-compte'),
    path('', mviews.index, name='home'),
    path('materiel/<int:materiel_pk>', mviews.materiel, name='materiel'),
    path('creer-materiel/', mviews.creer_materiel, name='creer-materiel'),
    path('editer-materiel/<int:materiel_pk>', mviews.editer_materiel, name='editer-materiel'),
    path('reserver-materiel/<int:materiel_pk>', mviews.reserver_materiel, name='reserver-materiel'),
    path('reserver-materiel-bouton/<int:materiel_pk>', mviews.reserver_materiel_bouton, name='reserver-materiel-bouton'),
    path('admin/', admin.site.urls),
]
