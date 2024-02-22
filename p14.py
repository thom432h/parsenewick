import json
import re
from io import StringIO
import sys
import os

#**********************************************************************************************************#

# Chemin du fichier défini une seule fois
chemin_fichier = r'C:\Users\Vitre\Desktop\python\khv.txt'

#**********************************************************************************************************#

def supprimer_jusqu_a_parenthese_et_end(chemin_fichier):
    """Supprime le contenu d'un fichier depuis le début jusqu'au premier '(' et le 'End;' à la fin."""
    with open(chemin_fichier, 'r') as fichier:
        contenu = fichier.read()
    
    index_parenthese = contenu.find('(')
    if index_parenthese != -1:
        contenu = contenu[index_parenthese:]
    contenu = re.sub(r'End;', '', contenu)

    with open(chemin_fichier, 'w') as fichier:
        fichier.write(contenu)

#**********************************************************************************************************#

def replace_commas(match):
    return match.group(0).replace(',', ' ### ')

#**********************************************************************************************************#

def parseNewickcap(newick):
    result = re.sub(r'\[[^\]]*\]', replace_commas, newick)
    parseNewick(result)

#**********************************************************************************************************#

def filtrer_proprietes(propriete_str):
    proprietes_filtrees = {}

    location1_match = re.search(r'location1=([-\d.]+)', propriete_str)
    location2_match = re.search(r'location2=([-\d.]+)', propriete_str)

    if location1_match:
        proprietes_filtrees['location1'] = float(location1_match.group(1))

    if location2_match:
        proprietes_filtrees['location2'] = float(location2_match.group(1))

    # Debugging: Affiche les propriétés filtrées pour vérification
    #print(f"Propriétés filtrées: {proprietes_filtrees}")

    return proprietes_filtrees

#**********************************************************************************************************#

def parseNewick(newick, parentId=None):
    global nodeid
    nodeid += 1
    node = {"id": nodeid, "parent_id": parentId}

    index_des_2_points = newick.rfind(":")
    lb = newick[index_des_2_points+1:]
    node["longueur"] = float(lb)

    if newick.rfind("(") != -1:
        node["type"] = "noeud interne"
        info = newick[newick.rfind(")")+1:index_des_2_points]
        node["children"] = []
    else:
        node["type"] = "feuille"
        info = newick[newick.rfind("["):newick.rfind("]")+1]

    node["propriete"] = info  # Vous pourriez vouloir convertir cette info en un format plus structuré

    k = 0
    for i, c in enumerate(newick):
        if c == "(":
            k += 1
        if c == ")":
            k -= 1
        if c == "," and k == 1:
            bg = newick[1:i]
            bd = newick[i+1:index_des_2_points]
            child1 = parseNewick(bg, nodeid)
            child2 = parseNewick(bd, nodeid)
            node["children"].extend([child1, child2])
            return node

    # Gère les cas où il n'y a pas de virgule au niveau supérieur, c'est-à-dire un seul enfant direct ou aucune subdivision supplémentaire.
    if "children" not in node:
        inner = newick[newick.find("(")+1:newick.rfind(")")]
        if inner:
            child = parseNewick(inner, nodeid)
            node["children"] = [child]

    return node

#**********************************************************************************************************#

def main(chemin_fichier):
    supprimer_jusqu_a_parenthese_et_end(chemin_fichier)
    
    with open(chemin_fichier, 'r') as fichier:
        newick_string = fichier.read()

    global nodeid
    nodeid = 0

    # Construit l'arbre à partir de la chaîne Newick
    arbre = parseNewick(newick_string)  # Utilisation directe de la structure retournée

    nom_fichier_sortie = os.path.splitext(chemin_fichier)[0] + '_nodes_data.json'
    with open(nom_fichier_sortie, 'w') as file:
        json.dump(arbre, file, indent=4)  # Sauvegarde directe de l'arbre dans un fichier JSON

    print(f"Les données ont été enregistrées dans le fichier {nom_fichier_sortie}")


if __name__ == '__main__':
    main(chemin_fichier)

#**********************************************************************************************************#

