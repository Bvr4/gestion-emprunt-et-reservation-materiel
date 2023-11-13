from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from materiel.models import Emplacement, Categorie, Materiel, Emprunt
from materiel.forms import CreerMateriel, EditerMateriel

def index(request):
    context={}
    context['materiels'] = Materiel.objects.order_by('identifiant')
    return render(request, 'materiel/index.html', context=context)

def materiel(request, materiel_pk):
    context={}
    context['materiel'] = get_object_or_404(Materiel, pk=materiel_pk)
    return render(request, 'materiel/materiel.html', context=context)

def creer_materiel(request):
    if request.method == "POST":
        form = CreerMateriel(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CreerMateriel()
    return render(request, 'materiel/creer-materiel.html', {'form':form})

#  >>>> à modifier (ne fonctionne pas en l'état)
def editer_materiel(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    if request.method == "POST":
        form = EditerMateriel(request.POST)
        if form.is_valid():
            materiel = form.save(commit=False)
            materiel.pk = materiel_pk
            materiel.save()
            return redirect('/')
    else:
        form = EditerMateriel(instance=materiel)
    return render(request, 'materiel/editer-materiel.html', {'form':form, 'materiel':materiel})

