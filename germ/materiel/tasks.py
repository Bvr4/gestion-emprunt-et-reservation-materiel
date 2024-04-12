import datetime as dt
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from materiel.models import Emprunt, Utilisateur

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
