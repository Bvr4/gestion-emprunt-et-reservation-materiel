import re
import os
from ezodf import newdoc, opendoc, Sheet
from django.core.files.storage import FileSystemStorage
from materiel.models import Utilisateur, Categorie, Materiel, Emplacement

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


# Fonction qui permet d'exporter la liste des matériels au format ods
def export_materiels():
    materiels = Materiel.objects.all().order_by('identifiant')

    # Création du document
    doc = newdoc(doctype='ods')
    doc.sheets.insert(0, Sheet('Materiels'))
    sheet = doc.sheets[0]

    # Création de l'en-tête
    entetes = ['Catégorie', 'Préfixe catégorie', 'Emplacement', 'Référence', 'Nom', 'Description', 'Empruntable']
    
    for i, entete in enumerate(entetes):
        sheet[0, i].set_value(entete)

    # Ajout des données au tableau
    for i, materiel in enumerate(materiels):
        if materiel.empruntable:
            empruntable = 'oui'
        else:
            empruntable = 'non'

        donnees = [materiel.categorie.nom,
                materiel.categorie.prefixe_identifiant,
                materiel.emplacement,
                materiel.identifiant,
                materiel.nom,
                materiel.description,
                empruntable
        ]

        for j, valeur in enumerate(donnees):
            sheet.append_rows(1)
            sheet[i+1, j].set_value(str(valeur))

    return doc.tobytes()


# Fonction qui permet d'importer la liste des matériels au format ods
def import_materiels(fichier, maj_description, maj_disponibilite):
    try:
        if fichier.name[-4:] != '.ods':
            raise TypeError
    except:
        raise ValueError
    
    # On enregistre le document pour pouvoir le traiter avec ezodf
    fs = FileSystemStorage()
    temp = fs.save('fichier_import_materiel_temp.ods', fichier)
    temp_path = fs.path(temp)

    # Ouverture du fichier avec ezodf
    doc = opendoc(temp_path)
    sheet = doc.sheets[0]

    premiere_ligne = True
    messages = []

    for row in sheet.rows():
        # On vérifie que les en-têtes sont correctes sur la première ligne
        if premiere_ligne:
            if not verifier_entetes(row):
                os.remove(temp_path)    # On supprime le fichier
                raise ValueError
            premiere_ligne = False
        else:
            # On met les valeurs de la ligne dans une liste
            infos_materiel = [cell.value for cell in row]
            # Si la catégorie est renseignée, on traite la ligne
            if infos_materiel[0] is not None and str(infos_materiel[0]) != '':
                nom_categorie = infos_materiel[0]
                prefixe_categorie = infos_materiel[1]
                nom_emplacement = infos_materiel[2]
                identifiant = infos_materiel[3]
                nom = infos_materiel[4]
                description = infos_materiel[5]
                empruntable = infos_materiel[6]

                erreur = False

                # Si la catégorie n'existe pas, on la crée
                if not Categorie.objects.filter(nom=nom_categorie).exists():
                    # Sauf si le préfixe est utilisé pour une catégorie existante
                    if Categorie.objects.filter(prefixe_identifiant=prefixe_categorie).exists():
                        messages.append(f"{identifiant} - {nom} : la catégorie {nom_categorie} n'a pas été trouvée en base, "\
                                        "mais le prefixe {prefixe_categorie} existe déjà pour une catégorie existante. "\
                                        "Cet enregistrement ne pourra être traité.")
                        erreur = True
                    else:
                        categorie = Categorie.objects.create(nom=nom_categorie, prefixe_identifiant=prefixe_categorie)
                        messages.append(f"{identifiant} - {nom} : la catégorie {nom_categorie} ({prefixe_categorie}) a été crée en base")

                # Si l'emplacement n'existe pas, on la crée
                if not Emplacement.objects.filter(nom=nom_emplacement).exists(): 
                    emplacement = Emplacement.objects.create(nom=nom_emplacement, commune=' ')
                    messages.append(f"{identifiant} - {nom} : l'emplacement {nom_emplacement} a été crée en base, "\
                                    "pensez à mettre à jour les informations concernant la commune de cet emplacement")

                # Si nous n'avons pas d'erreur concernant la catégorie, on continue le traitement
                if not erreur:
                    categorie = Categorie.objects.filter(nom=nom_categorie).first()
                    emplacement = Emplacement.objects.filter(nom=nom_emplacement).first()

                    # Si l'identifiant n'est pas renseignée ou qu'il n'existe pas déjà en base
                    if identifiant is None or identifiant == '' or not Materiel.objects.filter(identifiant=identifiant).exists():
                        # Si le nom n'existe pas déjà pour un autre matériel, on crée le matériel
                        if not Materiel.objects.filter(nom=nom).exists():
                            materiel = Materiel()
                            materiel.nom = nom

                            # Si l'identifiant n'est pas renseigné, on cherche le prochain identifiant pour la catégorie
                            if identifiant is None or identifiant == '':
                                materiel.identifiant = prochain_id_materiel(categorie.id) 
                            else:
                                materiel.identifiant = identifiant

                            if description is not None:
                                materiel.description = description
                            else:
                                materiel.description = ""
                            
                            materiel.categorie = categorie
                            materiel.emplacement = emplacement
                            
                            if empruntable.lower() == "non":
                                empruntable = False
                            else:
                                empruntable = True
                            materiel.empruntable = empruntable
                            materiel.save()
                            messages.append(f"{identifiant} - {nom} : le matériel a été créé en base.")
                        else:
                            messages.append(f"{nom} : un matériel existant porte déjà ce nom. Renseignez son identifiant si vous souhaitez mettre à jour ses informations.")
                        

                    # Si la référence existe déjà
                    elif Materiel.objects.filter(identifiant=identifiant).exists():
                        materiel = Materiel.objects.filter(identifiant=identifiant).first()

                        if materiel.nom != nom:
                            messages.append(f"{identifiant} - {nom} : un matériel existe déjà pour cet identifiant, avec un nom différent ({materiel.nom}).")
                        else:
                            # Si les informations sont différentes de celles en base, on met à jour l'enregistrement
                            if materiel.categorie != categorie:
                                materiel.categorie = categorie
                                materiel.save()
                                messages.append(f"{identifiant} - {nom} : la catégorie a été mise à jour.")

                            if materiel.emplacement != emplacement:
                                materiel.emplacement = emplacement
                                materiel.save()
                                messages.append(f"{identifiant} - {nom} : l'emplacement a été mise à jour.")

                            if maj_description and description is not None:
                                materiel.description = description
                                materiel.save()
                                messages.append(f"{identifiant} - {nom} : la description a été mise à jour.")
                        
                            if maj_disponibilite:
                                if empruntable.lower() == "oui":
                                    empruntable_bool = True
                                elif empruntable.lower() == "non":
                                    empruntable_bool = False
                                else:
                                    empruntable_bool = None
                                    messages.append(f'{identifiant} - {nom} : la disponibilité n\'a pas été mise à jour: {empruntable} n\'est pas une valeur valide. '\
                                                    'La valeur attendue est "oui" ou "non". ')

                                if empruntable_bool is not None:
                                    materiel.empruntable = empruntable_bool
                                    materiel.save()
                                    messages.append(f"{identifiant} - {nom} : la disponibilité a été mise à jour")
                       
    # Une fois le traitement terminé, on supprime le fichier
    os.remove(temp_path)
    return messages


# Fonction qui permet de vérifier que les en-têtes sont ben au format attendu pour la fonction import_materiel
def verifier_entetes(ligne):
    en_tete = []
    
    try:
        for cell in ligne:
            en_tete.append(str(cell.value).lower())

        if (en_tete[0] == 'catégorie' and en_tete[1] == 'préfixe catégorie' and en_tete[2] == 'emplacement' and 
            en_tete[3] == 'référence' and en_tete[4] == 'nom' and en_tete[5] == 'description' and en_tete[6] == 'empruntable'):
            return True
            
    except:
        return False
    return False