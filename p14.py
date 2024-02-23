import json
import re
from io import StringIO
import sys
import os

#**********************************************************************************************************#

# Chemin du fichier à lire
chemin_fichier = r'C:\Users\Vitre\Desktop\python\parsenewick\khv.txt'

#**********************************************************************************************************#

def supprimer_jusqu_a_parenthese_et_end(chemin_fichier):
    """Supprime le contenu d'un fichier depuis le début jusqu'au premier '(' et le 'End;' à la fin. """
    # Lire le contenu du fichier
    with open(chemin_fichier, 'r') as fichier:
        contenu = fichier.read()
    
    # Trouver l'index du premier '('
    index_parenthese = contenu.find('(')
    
    # Si '(' est trouvé, supprimer tout le contenu avant cela
    if index_parenthese != -1:
        contenu = contenu[index_parenthese:]

    contenu = re.sub(r'End;', '', contenu)

    # Réécrire le contenu modifié dans le fichier
    with open(chemin_fichier, 'w') as fichier:
        fichier.write(contenu)

# Exemple d'utilisation

supprimer_jusqu_a_parenthese_et_end(chemin_fichier)

#**********************************************************************************************************#

# Fonction pour nettoyer le contenu entre les crochets
def clean_metadata(text):
    pattern = r'\[.*?\]'  # Utilisation d'une raw string ici
    def replacer(match):
        segment = match.group(0)
        location1_match = re.search(r'location1=([-\d.]+)', segment)  # Raw string utilisée ici aussi
        location2_match = re.search(r'location2=([-\d.]+)', segment)  # Et ici
        
        new_segment = '['
        if location1_match:
            new_segment += location1_match.group(0)
        if location1_match and location2_match:
            new_segment += ', '
        if location2_match:
            new_segment += location2_match.group(0)
        new_segment += ']'
        
        return new_segment
    
    return re.sub(pattern, replacer, text)

#**********************************************************************************************************#

# Fonction pour lire, nettoyer et éventuellement sauvegarder le contenu du fichier
def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        contenu_original = file.read()
    
    contenu_nettoye = clean_metadata(contenu_original)
    
    # Sauvegarde du contenu nettoyé dans un nouveau fichier
    chemin_fichier_nettoye = filepath.replace('.txt', '_nettoye.txt')
    with open(chemin_fichier_nettoye, 'w', encoding='utf-8') as file:
        file.write(contenu_nettoye)
    
    print(f"Contenu nettoyé sauvegardé dans : {chemin_fichier_nettoye}")

# Appel de la fonction avec le chemin du fichier
process_file(chemin_fichier)

#**********************************************************************************************************#

def replace_commas_in_brackets(filepath):
    # Ouvrir et lire le contenu du fichier
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remplacer les virgules entre crochets par ' ### '
    modified_content = re.sub(r'\[(.*?)\]', lambda m: '[' + m.group(1).replace(',', ' ### ') + ']', content)

    # Sauvegarder le contenu modifié dans un nouveau fichier (ou réécrire sur l'original si désiré)
    modified_filepath = filepath.replace('.txt', '_modified.txt')
    with open(modified_filepath, 'w', encoding='utf-8') as file:
        file.write(modified_content)

    print(f"Le fichier modifié a été sauvegardé sous : {modified_filepath}")

# Spécifier le chemin de votre fichier
chemin_fichier = r'C:\Users\Vitre\Desktop\python\parsenewick\khv_nettoye.txt'  # Ajustez le chemin selon votre environnement
replace_commas_in_brackets(chemin_fichier)

#**********************************************************************************************************#

def parseNewick(newick, parentId=None):
    global nodeid
    newickParts = []
    k = 0
    l = len(newick)
    index_des_2_points = newick.rfind(":")
    lb = newick[index_des_2_points+1:l]
    info = ""
    infoStart = -1  # Initialiser infoStart ici
    if newick.rfind("(") != -1:
        nodeType = "noeud interne"
        info = newick[newick.rfind(")")+1:index_des_2_points]
        nodeid += 1  # Increment node ID for internal node
        currentId = nodeid
    else:
        nodeType = "feuille"
        infoStart = newick.rfind("[")
        info = newick[infoStart:newick.rfind("]")+1]
        nodeid += 1  # Increment node ID for leaf
        currentId = nodeid

    # Préparation de la partie Newick pour ce nœud
    if parentId is not None:
        if infoStart != -1:
            newickPart = f"{info[:1]}id:{currentId}{info[1:]}:{lb}"
        else:
            newickPart = f"[id:{currentId}]{info}:{lb}"
    else:
        newickPart = f"[id:{currentId}]{newick[:index_des_2_points]}:{lb}"

    newickParts.append(newickPart)

    for i, c in enumerate(newick):
        if c == "(":
            k += 1
        if c == ")":
            k -= 1
        if c == "," and k == 1:
            bg = newick[1:i]
            bd = newick[i+1:l-1]  # Ajustement pour exclure la dernière parenthèse

            leftPart = parseNewick(bg, currentId)
            rightPart = parseNewick(bd, currentId)
            combined = f"({leftPart},{rightPart})[id:{currentId}]:{lb}"
            return combined

    if len(newickParts) == 1:
        return newickParts[0]  # Si un seul élément, le retourner directement

# Example usage
nodeid = 0
with open(r'C:\Users\Vitre\Desktop\python\parsenewick\khv_nettoye_modified.txt', 'r') as fichier:
    newick_string = fichier.read()

newNewick = parseNewick(newick_string)
print(newNewick)

parseNewick(newick_string)

#**********************************************************************************************************#



