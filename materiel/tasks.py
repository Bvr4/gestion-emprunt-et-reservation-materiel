import datetime as dt
import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from materiel.models import Emprunt, Utilisateur
from .utils import generer_mdp

# Fonction qui permet de cloturer les emprunts ayant uniquement des dates de réservation (pas de date de début d'emprunt), une fois la période passée
@shared_task
def cloture_emprunt_non_empruntes():
    date_du_jour = dt.date.today()
    # On récupère tous les enregistrements Emprunts non cloturés aux dates de réservation expirées
    reservations_expirees = Emprunt.objects.filter(
        cloture = False,
        date_fin_resa__lte = date_du_jour,
        date_debut_emprunt = None
        ).all()    

    for reservation in reservations_expirees:
        reservation.cloture = True
        reservation.save()


# Fonction qui envoie un mail de rappel si la date de fin de réservation est dépassée, et que le matériel est signalé comme emprunté
@shared_task
def rappel_fin_de_reservation_depassee():
    date_du_jour = dt.date.today()
    # On récupère tous les enregistrements Emprunts non cloturés aux dates de réservation expirées
    emprunts_expires = Emprunt.objects.filter(
        cloture = False,
        date_fin_resa__lte = date_du_jour,
        date_debut_emprunt__isnull = False, 
        date_fin_emprunt__isnull = True
        ).all()    
        
    for emprunt in emprunts_expires:
        utilisateur = Utilisateur.objects.filter(pk=emprunt.utilisateur.pk).first()
        email_dest = utilisateur.user.email
        sujet = f'Matériel "{emprunt.materiel.nom}" non retourné'
        message = f"""Bonjour {utilisateur.user.username},
        Vous avez réservé le matériel "{emprunt.materiel.nom:}", du {emprunt.date_debut_resa:%d-%m-%Y} au {emprunt.date_fin_resa:%d-%m-%Y}, et procédé à son emprunt le {emprunt.date_debut_emprunt:%d-%m-%Y}.
        Le retour du matériel n'a pas été signalé sur la plateforme de gestion d'emprunt du matériel, alors que la date de fin de réservation est dépassée. Merci de bien vouloir restituer le matériel emprunté et signaler son retour sur la plateforme.
        
        Ceci est un message automatique, veuillez ne pas y répondre.
        """
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email_dest],
        )


# Fonction qui crée des utilisateurs à partir des utilisateurs inscrits dans Dolibarr
@shared_task
def import_utilisateurs_dolibarr():
    date_du_jour = str(dt.date.today())

    headers = {
        'Content-Type': 'application/json',
        'DOLAPIKEY': settings.DOLIBARR_API_KEY 
    }    

    url = settings.DOLIBARR_API_URL + 'members'

    # On demande la liste des utilisateurs dont la date de fin d'adhésion n'est pas dépassée (à jour dans leurs cotisations)
    params = {
        'sortfield': 't.rowid',
        'sortorder': 'ASC',
        'limit': 100,
        'properties': 'lastname,firstname,email,town,type,last_subscription_date_end,phone,phone_pro,phone_perso,phone_mobile',
        'sqlfilters': f"t.datefin:>:'{date_du_jour}'"
    }

    response = requests.get(url, headers = headers, params = params)

    if response.status_code != 200:
        raise Exception(f"Impossible de récupérer les utilisateurs Dolibarr via l'API")
    
    utilisateurs_dolibarr = response.json()

    for utilisateur in utilisateurs_dolibarr:
        # Création du user name en fonction du prénom et nom si ils sont présents
        user_name =  (utilisateur['lastname'] if utilisateur['lastname'] else '') + \
                    ('_' if utilisateur['lastname'] and utilisateur['firstname'] else '') + \
                    (utilisateur['firstname'] if utilisateur['firstname'] else '')

        # Création de l'utilisateur si il n'existe pas déjà, et si on a assez d'information sur l'utilisateur venant de dolibarr
        if (utilisateur['email'] is not None and utilisateur['email'] != '' and user_name != '' and
            not Utilisateur.objects.filter(user__email=utilisateur['email']).exists() and
            not Utilisateur.objects.filter(user__username=user_name).exists()):

            # Création de l'enregistrement User
            nouvel_user = User.objects.create_user(username=user_name,
                                email=utilisateur['email'],
                                password=generer_mdp(12))

            nouvel_user.first_name=utilisateur['firstname']
            nouvel_user.last_name=utilisateur['lastname']
            nouvel_user.save()

            # Création de l'enregistrement Utilisateur, lié au nouvel User.
            nouvel_utilisateur = Utilisateur()
            nouvel_utilisateur.user = nouvel_user

            # On récupère le numéro de téléphone renseigné
            if utilisateur['phone'] is not None:
                telephone = utilisateur['phone']
            elif utilisateur['phone_perso'] is not None:
                telephone = utilisateur['phone_perso']
            elif utilisateur['phone_mobile'] is not None:
                telephone = utilisateur['phone_mobile']
            elif utilisateur['phone_pro'] is not None:
                telephone = utilisateur['phone_pro']

            # Pour le numéro de téléphone, on se débarasse de tous les caractères qui ne sont pas numériques (espaces, points, tirets...)
            nouvel_utilisateur.numero_telephone = "".join(ch for ch in telephone if ch.isnumeric())
            nouvel_utilisateur.commune_residence = utilisateur['town'] if utilisateur['town'] else ''

            try:
                nouvel_utilisateur.save()
            except:
                nouvel_user.delete()
                raise Exception(f"Impossible de créer l'utilisateur {utilisateur['email']}")