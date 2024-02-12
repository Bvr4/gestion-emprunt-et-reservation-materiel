import datetime as dt
from celery import shared_task
from materiel.models import Emprunt


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