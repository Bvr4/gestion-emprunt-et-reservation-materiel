from django.contrib import admin
from django.urls import path
import materiel.views as mviews

urlpatterns = [
    path('', mviews.index, name='home'),
    path('materiel/<int:materiel_pk>', mviews.materiel, name='materiel'),
    path('creer-materiel/', mviews.creer_materiel, name='creer-materiel'),
    path('editer-materiel/<int:materiel_pk>', mviews.editer_materiel, name='editer-materiel'),
    path('admin/', admin.site.urls),
]
