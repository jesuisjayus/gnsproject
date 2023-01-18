import os
import shutil

préCheminCréé = os.getcwd() #a éxécuter là où on crée nos fichiers config/on exécute le load.py
préCheminRempl = "/mnt/c/users/aurel/GNS3/projects/Projet GNS3 auto/project-files" #path project files du projet gns3
a=int(input("Combien de routeurs ? "))

def find_file(préChemin, fichier):
    for root, dirs, files in os.walk(préChemin):
        if fichier in files:
            return os.path.join(root, fichier)
    return None

for i in range (1,a+1):

    fichierCréé = 'i'+str(i)+'_startup-config.cfg'
    fichierRempl = 'i'+str(i)+'_startup-config.cfg'

   
    cheminCréés = find_file(préCheminCréé, fichierCréé) #fichier créés
    cheminRemplacer = find_file(préCheminRempl, fichierRempl) #fichier créés

    if cheminCréés and cheminRemplacer:
        print(cheminCréés,cheminRemplacer)
        shutil.move(cheminCréés, cheminRemplacer)
    
    else:
        print("Fichier introuvable\nFin")
    