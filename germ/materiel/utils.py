import re
from odf.opendocument import OpenDocumentSpreadsheet
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
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


# Fonction qui permet d'exporter la liste des matériels au format ods
def export_materiels():
    materiels = Materiel.objects.all().order_by('identifiant')

    # Création du document
    doc = OpenDocumentSpreadsheet()
    table = Table(name='Materiels')

    # Création de l'en-tête
    row = TableRow()
    cell = TableCell()
    cell.addElement(P(text=str('Catégorie')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Préfixe catégorie')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Emplacement')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Référence')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Nom')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Description')))  
    row.addElement(cell)

    cell = TableCell()
    cell.addElement(P(text=str('Empruntable')))  
    row.addElement(cell)

    table.addElement(row)


    # Ajout des données au tableau
    for materiel in materiels:
        row = TableRow()
        cell = TableCell()
        cell.addElement(P(text=str(materiel.categorie.nom)))  
        row.addElement(cell)

        cell = TableCell()
        cell.addElement(P(text=str(materiel.categorie.prefixe_identifiant)))  
        row.addElement(cell)

        cell = TableCell()
        cell.addElement(P(text=str(materiel.emplacement)))  
        row.addElement(cell)

        cell = TableCell()
        cell.addElement(P(text=str(materiel.identifiant)))  
        row.addElement(cell)

        cell = TableCell()
        cell.addElement(P(text=str(materiel.nom)))  
        row.addElement(cell)

        cell = TableCell()
        cell.addElement(P(text=str(materiel.description)))  
        row.addElement(cell)

        if materiel.empruntable:
            empruntable = 'oui'
        else:
            empruntable = 'non'
        cell = TableCell()
        cell.addElement(P(text=str(empruntable)))  
        row.addElement(cell)

        table.addElement(row)

    doc.spreadsheet.addElement(table)

    return doc


# Fonction qui permet d'importer la liste des matériels au format ods
def import_materiels(fichier):
    print(fichier.name)
    print(fichier.name[-4:])
    try:
        if fichier.name[-4:] != '.ods':
            raise TypeError
    except:
        raise ValueError
    
    doc = load(fichier)
    d = doc.spreadsheet

    premiere_ligne = True

    for row in d.getElementsByType(TableRow):
        # On vérifie que les en-têtes sont correctes sur la première ligne
        if premiere_ligne:
            if not verifier_entetes(row):
                raise ValueError
            premiere_ligne = False
        
        # Si la catégorie est renseignée, on traite la ligne
        if row.getElementsByType(TableCell)[0] is not None and str(row.getElementsByType(TableCell)[0]) != '':

            print (row)
            print(row.getElementsByType(TableCell))
            print(f"Catégorie : {row.getElementsByType(TableCell)[0]}")
            print(f"Préfixe : {row.getElementsByType(TableCell)[1]}")
            print(f"Emplacement : {row.getElementsByType(TableCell)[2]}")
            print(f"Référence : {row.getElementsByType(TableCell)[3]}")
            print(f"Nom : {row.getElementsByType(TableCell)[4]}")
            print(f"Description : {row.getElementsByType(TableCell)[5]}")
            print(f"Empruntable : {row.getElementsByType(TableCell)[6]}")

            # for cell in row.getElementsByType(TableCell):
            #     cell_text = ""
            #     for paragraph in cell.getElementsByType(P):
            #         print(paragraph)
            #         cell_text += str(paragraph)

            #     print (cell_text)
        print("---")


# Fonction qui permet de vérifier que les en-têtes sont ben au format attendu pour la fonction import_materiel
def verifier_entetes(ligne):
    en_tete = []
    
    try:
        for element in ligne.getElementsByType(TableCell):
            en_tete.append(str(element))

        if (en_tete[0] == 'Catégorie' and en_tete[1] == 'Préfixe catégorie' and en_tete[2] == 'Emplacement' and 
            en_tete[3] == 'Référence' and en_tete[4] == 'Nom' and en_tete[5] == 'Description' and en_tete[6] == 'Empruntable'):
            return True
            
    except:
        return False
    return False