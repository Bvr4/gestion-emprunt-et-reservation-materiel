from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from materiel.models import Emplacement, Categorie, Materiel, Emprunt, Utilisateur
from materiel.forms import CreerMateriel, EditerMateriel, CreationUtilisateur, CreationUser, ReserverMateriel

def index(request):
    context={}
    context['materiels'] = Materiel.objects.order_by('identifiant')
    return render(request, 'materiel/index.html', context=context)


def materiel(request, materiel_pk):
    context={}
    context['materiel'] = get_object_or_404(Materiel, pk=materiel_pk)
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
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


def creer_compte(request):
    if request.method == 'POST':
        form_user = CreationUser(request.POST)
        form_utilisateur = CreationUtilisateur(request.POST)
        if form_utilisateur.is_valid() and form_user.is_valid():
            user = form_user.save()
            utilisateur = form_utilisateur.save(commit=False)
            utilisateur.user = user
            utilisateur.save()
            login(request, user)
            return redirect('/')
    else:
        form_user = CreationUser()
        form_utilisateur = CreationUtilisateur()

    return render(request, 'registration/creer-compte.html', {"form_user":form_user, "form_utilisateur":form_utilisateur})


def get_utilisateur_data(user):
    # Utilisation de la relation reverse pour accéder aux informations Utilisateur depuis User
    try:
        utilisateur_data = user.utilisateur
    except Utilisateur.DoesNotExist:
        utilisateur_data = None

    return utilisateur_data


def reserver_materiel(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    if request.method == 'GET':        
        form = ReserverMateriel()
    elif request.method == 'POST':
        form = ReserverMateriel(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.utilisateur=get_utilisateur_data(request.user)
            reservation.materiel=materiel
            reservation.save()
            return HttpResponse('OK')

    return render(request, 'materiel/reserver-materiel.html', {'form':form, 'materiel':materiel})