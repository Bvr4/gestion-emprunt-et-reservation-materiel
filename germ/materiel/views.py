from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from materiel.models import Emplacement, Categorie, Materiel, Emprunt, Utilisateur
from materiel.forms import CreerMateriel, EditerMateriel, CreationUtilisateur, CreationUser, ReserverMateriel
import datetime as dt

def index(request):
    context={}
    context['materiels'] = Materiel.objects.order_by('identifiant')
    return render(request, 'materiel/index.html', context=context)


def materiel(request, materiel_pk):
    date_du_jour = dt.date.today()
    context={}
    context['materiel'] = get_object_or_404(Materiel, pk=materiel_pk)
    context['reservations'] = Emprunt.objects.filter(materiel=context['materiel'])

    context['reservation_en_cours'] = Emprunt.objects.filter(
        materiel=context['materiel'],
        cloture=False,
        date_debut_resa__lte=date_du_jour,
        date_fin_resa__gte=date_du_jour 
    ).first()

    context['reservation_passees'] = Emprunt.objects.filter(
        materiel=context['materiel'],
        date_fin_resa__lt=date_du_jour 
    ).order_by('-date_fin_resa').all()[:5]

    context['reservation_futures'] = Emprunt.objects.filter(
        materiel=context['materiel'],
        date_debut_resa__gt=date_du_jour 
    ).order_by('date_debut_resa').all()

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
    if request.method == 'POST':
        form = ReserverMateriel(request.POST, initial={'materiel': materiel})
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.utilisateur=get_utilisateur_data(request.user)
            reservation.save()
            # return render(request, 'materiel/reserver-materiel-bouton.html', {'materiel':materiel, 'reservation':reservation})   # !>> à creuser, je ne suis pas fan du résultat en terme d'UX/UI
            return redirect('materiel', materiel_pk=materiel.pk)
    else:
        form = ReserverMateriel(initial={'materiel':materiel})

    return render(request, 'materiel/reserver-materiel.html', {'form':form, 'materiel':materiel})


def reserver_materiel_bouton(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    return render(request, 'materiel/reserver-materiel-bouton.html', {'materiel':materiel})


def utilisateur(request, utilisateur_pk):
    context={}
    # utilisateur dont on affiche les informations
    context['utilisateur_fiche'] = get_object_or_404(Utilisateur, pk=utilisateur_pk)
    context['emprunts'] = Emprunt.objects.filter(utilisateur=context['utilisateur_fiche']).order_by('-date_fin_resa').all()
    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
    return render(request, 'materiel/utilisateur.html', context)


def utilisateur_peut_emprunter(request, utilisateur_pk):
    # utilisateur à modifier
    utilisateur_fiche = get_object_or_404(Utilisateur, pk=utilisateur_pk)
    if request.method == 'POST':
        if utilisateur_fiche.peut_emprunter:
            utilisateur_fiche.peut_emprunter = False
        else:
            utilisateur_fiche.peut_emprunter = True
        utilisateur_fiche.save()

    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur, user=request.user)

    return render(request, 'materiel/utilisateur-peut-emprunter.html', {'utilisateur_fiche':utilisateur_fiche, 'utilisateur':utilisateur})


def emprunter_materiel_bouton(request, emprunt_pk):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_pk)
    if request.method == 'POST':
        action_emprunt = request.POST.get('action_emprunt', None)
        print (action_emprunt)
        if action_emprunt == 'retourner':
        # if emprunt.date_debut_emprunt is not None and emprunt.date_fin_emprunt is None:
            emprunt.date_fin_emprunt = dt.date.today()
            emprunt.cloture = True
            emprunt.save()
        elif action_emprunt == 'emprunter':
        # if emprunt.date_debut_emprunt is None:
            emprunt.date_debut_emprunt = dt.date.today()
            emprunt.save()
        elif action_emprunt == 'annuler':
            emprunt.cloture = True
            emprunt.save()

    return render(request, 'materiel/emprunter-materiel-bouton.html', {'emprunt':emprunt})
