import re
from materiel.models import Utilisateur, Categorie, Materiel

# Utilisation de la relation reverse pour accéder aux informations Utilisateur depuis User
def get_utilisateur_data(user):
    try:
        utilisateur_data = user.utilisateur
    except Utilisateur.DoesNotExist:
        utilisateur_data = None
    return utilisateur_data


# Fonction qui retourne le prochain identifiant, en fonction de l'identifiant donné en entrée (incrémentation de la partie numérique uniquement)
def incrementer_identifiant(identifiant):
    # Expression régulière pour extraire le préfixe et l'identifiant numérique
    match = re.match(r'([A-Za-z]+)(\d+)', identifiant)
    
    if match:
        # Extraire le préfixe et le nombre
        prefixe, nombre_str = match.groups()
        
        # Convertir le nombre en entier, l'incrémenter, puis reformater l'identifiant avec le même nombre de zéros
        nombre_incremente = int(nombre_str) + 1
        identifiant_incremente = f"{prefixe}{str(nombre_incremente).zfill(len(nombre_str))}"
        
        return identifiant_incremente
    else:
        return None


# Fonction qui retourne le prochain identifiant matériel pour une catégorie donnée, incrémenté depuis le plus haut identifiant existant
def prochain_id_materiel(categorie_id):
    dernier_id = Materiel.objects.filter(categorie_id=categorie_id).order_by('-identifiant').first()
    # S'il n'y a pas de matériel pour cette catégorie, et si la catégorie existe, on retourne un premier identifiant valide
    if not dernier_id:
        if Categorie.objects.filter(id=categorie_id).exists():
            return Categorie.objects.filter(id=categorie_id).first().prefixe_identifiant + '01'
        else:
            return None
    
    return incrementer_identifiant(dernier_id.identifiant)
