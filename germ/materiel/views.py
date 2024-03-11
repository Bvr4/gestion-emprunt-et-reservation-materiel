import datetime as dt
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from materiel.models import Emplacement, Categorie, Materiel, Emprunt, Utilisateur, Commentaire
from materiel.forms import CreerMateriel, EditerMateriel, CreationUtilisateur, CreationUser, ReserverMateriel, ReserverMaterielModerateur, CreerCommentaire
from materiel.forms import CreerCategorie, EditerCategorie, CreerEmplacement, EditerEmplacement, EditerUser, EditerUtilisateur
from materiel.forms import FiltreMateriel
from .utils import get_utilisateur_data, prochain_id_materiel


def index(request):
    context={}
    context['materiels'] = Materiel.objects.order_by('identifiant')

    context['filtre_materiel'] = FiltreMateriel(request.GET, queryset=Materiel.objects.order_by('identifiant'))
    
    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)

    return render(request, 'materiel/index.html', context=context)


@login_required(login_url="/login")
@permission_required("materiel.view_materiel", login_url="/login", raise_exception=True)
def materiel(request, materiel_pk):
    context={}
    context['materiel'] = get_object_or_404(Materiel, pk=materiel_pk)

    # On renseigne les informations de réservations pour l'affichage dans le calendrier
    reservations_calendrier = []
    for reservation in context['materiel'].reservations_passees(nombre=0):
        reservations_calendrier.append({
            'title': 'Réservé',
            'start': reservation.date_debut_resa.isoformat(),
            'end': (reservation.date_fin_resa + dt.timedelta(days=1)).isoformat(),
        })
    
    if context['materiel'].reservation_en_cours():
        reservations_calendrier.append({
            'title': 'Réservé',
            'start': context['materiel'].reservation_en_cours().date_debut_resa.isoformat(),
            'end': (context['materiel'].reservation_en_cours().date_fin_resa + dt.timedelta(days=1)).isoformat(),
        })
    
    for reservation in context['materiel'].reservations_futures():
        reservations_calendrier.append({
            'title': 'Réservé',
            'start': reservation.date_debut_resa.isoformat(),
            'end': (reservation.date_fin_resa + dt.timedelta(days=1)).isoformat(),
        })

    context['reservations_calendrier'] = reservations_calendrier

    context['commentaires'] = Commentaire.objects.filter(materiel=context['materiel']).order_by('-date')

    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
    return render(request, 'materiel/fiche_materiel/materiel.html', context=context)


@login_required(login_url="/login")
@permission_required("materiel.add_materiel", login_url="/login", raise_exception=True)
def creer_materiel(request):
    if request.method == 'POST':
        form = CreerMateriel(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CreerMateriel()
    return render(request, 'materiel/creer-materiel.html', {'form':form})


@login_required(login_url="/login")
@permission_required("materiel.add_materiel", login_url="/login", raise_exception=True)
# Permet de récupérer le prochain identifiant lors de la création de matériel, quand l'utilisateur choisi une catégorie
def get_prochain_identifiant(request):
    if request.method == 'GET':
        categorie = request.GET.get('categorie')
        if categorie is not None and categorie != '':
            prochain_identifiant = prochain_id_materiel(categorie)
            # On renvoie le formulaire avec la valeur initiale définie
            form = CreerMateriel(initial={'identifiant': prochain_identifiant})
            return render(request, 'materiel/creer-materiel-prochain-identifiant.html', {'form':form})
    return HttpResponse(400)


@login_required(login_url="/login")
@permission_required("materiel.change_materiel", login_url="/login", raise_exception=True)
def editer_materiel(request, materiel_pk):
    materiel_a_editer = get_object_or_404(Materiel, pk=materiel_pk)
    if request.method == 'POST':
        form = EditerMateriel(request.POST)
        if form.is_valid():
            materiel_a_editer = form.save(commit=False)
            materiel_a_editer.pk = materiel_pk
            materiel_a_editer.save()
            return redirect(materiel, materiel_pk=materiel_pk)
    else:
        form = EditerMateriel(instance=materiel_a_editer)
    return render(request, 'materiel/editer-materiel.html', {'form':form, 'materiel':materiel_a_editer})


@login_required(login_url="/login")
@permission_required("materiel.delete_materiel", login_url="/login", raise_exception=True)
def supprimer_materiel(request, materiel_pk):    
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    nom_materiel = materiel.nom
    materiel.delete()
    messages.success(request, f'Le matériel "{nom_materiel}" a été supprimé.')
    return redirect('/') 
       

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

    return render(request, 'registration/creer-compte.html', {'form_user':form_user, 'form_utilisateur':form_utilisateur})


@login_required(login_url="/login")
@permission_required("materiel.add_emprunt", login_url="/login", raise_exception=True)
def reserver_materiel(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    utilisateur = get_utilisateur_data(request.user)

    # Si l'utilisateur est modérateur, on charge le formulaire permettant de choisir quel utilisateur procède à la reservation
    if utilisateur.est_moderateur:
        form_model_resa = ReserverMaterielModerateur
    else:
        form_model_resa = ReserverMateriel

    if request.method == 'POST':
        # On recharge tout le contexte pour pouvoir render toute la section reservation
        context = {}
        context['materiel'] = materiel
        context['utilisateur'] = utilisateur

        form = form_model_resa(request.POST, initial={'materiel': materiel})

        if form.is_valid():
            reservation = form.save(commit=False)
            if not utilisateur.est_moderateur:
                reservation.utilisateur = get_utilisateur_data(request.user)
            reservation.save()
            return render(request, 'materiel/fiche_materiel/section-reservation.html', context=context)
        else:
            context['formulaire_resa'] = form
            return render(request, 'materiel/fiche_materiel/section-reservation.html', context=context)

    else:
        form = form_model_resa(initial={'materiel':materiel})

    return render(request, 'materiel/fiche_materiel/reserver-materiel.html', {'form':form, 'materiel':materiel})


@login_required(login_url="/login")
@permission_required("materiel.add_emprunt", login_url="/login", raise_exception=True)
def reserver_materiel_bouton(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    return render(request, 'materiel/fiche_materiel/reserver-materiel-bouton.html', {'materiel':materiel})


@login_required(login_url="/login")
@permission_required("materiel.view_utilisateur", login_url="/login", raise_exception=True)
def utilisateur(request, utilisateur_pk):
    context={}
    # utilisateur dont on affiche les informations
    context['utilisateur_fiche'] = get_object_or_404(Utilisateur, pk=utilisateur_pk)
    context['emprunts'] = Emprunt.objects.filter(utilisateur=context['utilisateur_fiche']).order_by('-date_fin_resa').all()
    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
    return render(request, 'utilisateur/utilisateur.html', context)


@login_required(login_url="/login")
@permission_required("materiel.change_emprunt", login_url="/login", raise_exception=True)
def emprunter_materiel_bouton(request, emprunt_pk):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_pk)
    utilisateur = get_object_or_404(Utilisateur, user=request.user)
    if request.method == 'POST':
        action_emprunt = request.POST.get('action_emprunt', None)
        print (action_emprunt)
        if action_emprunt == 'retourner':
            emprunt.date_fin_emprunt = dt.date.today()
            emprunt.cloture = True
            emprunt.save()
        elif action_emprunt == 'emprunter':
            emprunt.date_debut_emprunt = dt.date.today()
            emprunt.save()
        elif action_emprunt == 'annuler':
            emprunt.cloture = True
            emprunt.save()

    return render(request, 'materiel/fiche_materiel/emprunter-materiel-bouton.html', {'emprunt':emprunt, 'utilisateur':utilisateur})


@login_required(login_url="/login")
@permission_required("materiel.add_commentaire", login_url="/login", raise_exception=True)
def creer_commentaire(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    if request.method == 'POST':
        form = CreerCommentaire(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.auteur = get_utilisateur_data(request.user)
            commentaire.materiel = materiel
            commentaire.date = timezone.now()
            commentaire.save()
            return render(request, 'materiel/fiche_materiel/commentaire.html', {'commentaire':commentaire, 'materiel':materiel, 'nouveau_commentaire':True})
    else:
        form = CreerCommentaire()
    return render(request, 'materiel/fiche_materiel/creer-commentaire.html', {'form':form, 'materiel':materiel})


@login_required(login_url="/login")
@permission_required("materiel.add_commentaire", login_url="/login", raise_exception=True)
def creer_commentaire_bouton(request, materiel_pk):
    materiel = get_object_or_404(Materiel, pk=materiel_pk)
    return render(request, 'materiel/fiche_materiel/creer-commentaire-bouton.html', {'materiel':materiel})


def categories(request):
    context = {}
    context['categories'] = Categorie.objects.order_by('nom')

    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)

    return render(request, 'categorie/categories.html', context=context)


def categorie(request, categorie_pk):
    context = {}
    context['categorie'] = get_object_or_404(Categorie, pk=categorie_pk)   
    context['materiels'] = Materiel.objects.filter(categorie=context['categorie']).order_by('identifiant') 

    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
    return render(request, 'categorie/categorie.html', context=context)


@login_required(login_url="/login")
@permission_required("materiel.add_categorie", login_url="/login", raise_exception=True)
def creer_categorie(request):
    if request.method == 'POST':
        form = CreerCategorie(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/categories')
    else:
        form = CreerCategorie()
    return render(request, 'categorie/creer-categorie.html', {'form':form})


@login_required(login_url="/login")
@permission_required("materiel.change_categorie", login_url="/login", raise_exception=True)
def editer_categorie(request, categorie_pk):
    categorie_a_editer = get_object_or_404(Categorie, pk=categorie_pk)
    ancien_prefixe = categorie_a_editer.prefixe_identifiant
    if request.method == 'POST':
        form = EditerCategorie(request.POST)
        if form.is_valid():
            categorie_a_editer = form.save(commit=False)
            categorie_a_editer.pk = categorie_pk
            categorie_a_editer.save()

            if categorie_a_editer.prefixe_identifiant != ancien_prefixe:
                #  Mise à jour des identifiants des matériels de la catégorie, pour que le préfixe corresponde à la nouvelle valeur
                len_ancien_prefixe = len(ancien_prefixe)
                materiels = Materiel.objects.filter(categorie=categorie_a_editer)

                for materiel in materiels:
                    nouvel_identifiant = categorie_a_editer.prefixe_identifiant + materiel.identifiant[len_ancien_prefixe:]
                    Materiel.objects.filter(pk=materiel.pk).update(identifiant=nouvel_identifiant)

            return redirect(categorie, categorie_pk=categorie_pk)
    else:
        form = EditerCategorie(instance=categorie_a_editer)
    return render(request, 'categorie/editer-categorie.html', {'form':form, 'categorie':categorie_a_editer})


@login_required(login_url="/login")
@permission_required("materiel.delete_categorie", login_url="/login", raise_exception=True)
def supprimer_categorie(request, categorie_pk):    
    categorie = get_object_or_404(Categorie, pk=categorie_pk)

    if Materiel.objects.filter(categorie=categorie).exists():
        messages.error(request, 'Vous ne pouvez pas supprimer cette catégorie car des matériels y sont associés.')
        return redirect(reverse(editer_categorie, args=[categorie_pk]))

    nom_categorie = categorie.nom
    categorie.delete()
    messages.success(request, f'La catégorie "{nom_categorie}" a été supprimé.')
    return redirect('/categories') 


@login_required(login_url="/login")
@permission_required("materiel.view_utilisateur", login_url="/login", raise_exception=True)
def utilisateurs(request):
    context = {}
    context['utilisateurs'] = Utilisateur.objects.order_by('user__last_name')

    return render(request, 'utilisateur/utilisateurs.html', context=context)


@login_required(login_url="/login")
@permission_required("materiel.change_utilisateur", login_url="/login", raise_exception=True)
def editer_utilisateur(request, utilisateur_pk):
    utilisateur_a_editer = get_object_or_404(Utilisateur, pk=utilisateur_pk)
    if request.method == 'POST':
        form_user = EditerUser(request.POST, instance=utilisateur_a_editer.user)
        form_utilisateur = EditerUtilisateur(request.POST, instance=utilisateur_a_editer)
        if form_utilisateur.is_valid() and form_user.is_valid():
            user_edite = form_user.save()
            utilisateur_edite = form_utilisateur.save(commit=False)
            utilisateur_edite.user = user_edite
            utilisateur_edite.save()
            return redirect(utilisateur, utilisateur_pk=utilisateur_pk)
    else:
        form_user = EditerUser(instance=utilisateur_a_editer.user)
        form_utilisateur = EditerUtilisateur(instance=utilisateur_a_editer)

    return render(request, 'utilisateur/editer-utilisateur.html', {'form_user':form_user, 'form_utilisateur':form_utilisateur, 'utilisateur_a_editer':utilisateur_a_editer})


@login_required(login_url="/login")
@permission_required("materiel.delete_utilisateur", login_url="/login", raise_exception=True)
def supprimer_utilisateur(request, utilisateur_pk):   
    utilisateur = get_object_or_404(Utilisateur, pk=utilisateur_pk)
    nom_utilisateur = utilisateur.user.username
    # On supprime l'user, comme l'utilisateur est en mode "on_delete=cascade", il sera supprimé lui aussi.
    utilisateur.user.delete()
    messages.success(request, f'L\'utilisateur "{nom_utilisateur}" a été supprimé.')
    return redirect('/utilisateurs') 


def emplacements(request):
    context = {}
    context['emplacements'] = Emplacement.objects.order_by('nom')

    # utilisateur actuellement connecté
    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)

    return render(request, 'emplacement/emplacements.html', context=context)


def emplacement(request, emplacement_pk):
    context = {}
    context['emplacement'] = get_object_or_404(Emplacement, pk=emplacement_pk)   
    context['materiels'] = Materiel.objects.filter(emplacement=context['emplacement']).order_by('identifiant') 

    if request.user.is_authenticated:
        context['utilisateur'] = get_object_or_404(Utilisateur, user=request.user)
    return render(request, 'emplacement/emplacement.html', context=context)


@login_required(login_url="/login")
@permission_required("materiel.add_emplacement", login_url="/login", raise_exception=True)
def creer_emplacement(request):
    if request.method == 'POST':
        form = CreerEmplacement(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/emplacements')
    else:
        form = CreerEmplacement()
    return render(request, 'emplacement/creer-emplacement.html', {'form':form})


@login_required(login_url="/login")
@permission_required("materiel.change_emplacement", login_url="/login", raise_exception=True)
def editer_emplacement(request, emplacement_pk):
    emplacement_a_editer = get_object_or_404(Emplacement, pk=emplacement_pk)
    if request.method == 'POST':
        form = EditerEmplacement(request.POST)
        if form.is_valid():
            emplacement_a_editer = form.save(commit=False)
            emplacement_a_editer.pk = emplacement_pk
            emplacement_a_editer.save()
            return redirect(emplacement, emplacement_pk=emplacement_pk)
    else:
        form = EditerEmplacement(instance=emplacement_a_editer)
    return render(request, 'emplacement/editer-emplacement.html', {'form':form, 'emplacement':emplacement_a_editer})


@login_required(login_url="/login")
@permission_required("materiel.delete_emplacement", login_url="/login", raise_exception=True)
def supprimer_emplacement(request, emplacement_pk):
    emplacement = get_object_or_404(Emplacement, pk=emplacement_pk)

    if Materiel.objects.filter(emplacement=emplacement).exists():
        messages.error(request, 'Vous ne pouvez pas supprimer cette emplacement car des matériels y sont associés.')
        return redirect(reverse(editer_emplacement, args=[emplacement_pk]))

    nom_emplacement = emplacement.nom
    emplacement.delete()
    messages.success(request, f'L\'emplacement "{nom_emplacement}" a été supprimé.')
    return redirect('/emplacements')
