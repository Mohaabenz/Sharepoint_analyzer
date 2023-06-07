from sharepoint import Sharepoint
from files import File
from analyse import Analyse
import pandas as pd

"""
Ce script permet d'effectuer des opérations sur un site SharePoint à l'aide des classes Sharepoint, File et Analyse.

Usage:
    - Crée une instance de la classe Sharepoint en spécifiant l'URL du site SharePoint.
    - Authentifie l'utilisateur en appelant la méthode authenticate de l'instance Sharepoint.
    - Récupère la connexion établie avec SharePoint à partir de l'attribut connection de l'instance Sharepoint.
    - Demande à l'utilisateur de saisir le nom du sharepoint.
    - Commence une boucle while pour afficher un menu à l'utilisateur.
    - Si l'utilisateur choisit "1", le programme effectue des opérations sur des dossiers :
        - Initialise une liste files_error pour stocker les fichiers en erreur.
        - Définit le chemin racine root_path pour les dossiers.
        - Crée une instance de la classe File en utilisant la connexion à SharePoint et l'URL du sharepoint.
        - Récupère les dossiers racines à partir de root_path.
        - Demande à l'utilisateur d'entrer un nom de dossier ou un chemin cible.
        - Sélectionne les dossiers correspondants à partir de root_items en utilisant la méthode select_folders de la classe File.
        - Itère sur chaque fichier dans la liste folder_list.
        - Charge le fichier en utilisant la méthode upload de la classe File.
        - Crée une liste de DataFrame df_list et une liste de noms de feuilles sheet_name en utilisant la méthode create_df de la classe File.
        - Itère sur chaque DataFrame et son nom de feuille correspondant.
        - Crée une instance de la classe Analyse en utilisant le DataFrame.
        - Exécute l'analyse en utilisant la méthode execute de la classe Analyse.
        - Crée un répertoire pour le fichier d'entrée en utilisant la méthode create_directory de la classe Analyse.
        - Enregistre le résultat de l'analyse dans un fichier CSV.
        - Efface la sortie de la console.
        - Gère les exceptions et ajoute les fichiers en erreur à la liste files_error.
        - Si des fichiers en erreur existent, les enregistre dans un fichier CSV.
    - Si l'utilisateur choisit "2", le programme effectue des opérations sur des fichiers :
        - Crée une instance de la classe File en utilisant la connexion à SharePoint et l'URL du sharepoint.
        - Commence une boucle while pour demander à l'utilisateur d'uploader des fichiers.
        - Charge le fichier en utilisant la méthode upload de la classe File.
        - Crée une liste de DataFrame df_list et une liste de noms de feuilles sheet_name en utilisant la méthode create_df de la classe File.
        - Demande à l'utilisateur s'il souhaite évaluer la qualité des données en utilisant un dictionnaire de données.
        - Itère sur chaque DataFrame et son nom de feuille correspondant.
        - Crée une instance de la classe Analyse en utilisant le DataFrame.
        - Exécute l'analyse en utilisant la méthode execute de la classe Analyse.
        - Crée un répertoire pour le fichier d'entrée en utilisant la méthode create_directory de la classe Analyse.
        - Enregistre le résultat de l'analyse dans un fichier CSV.
        - Si l'évaluation de la qualité des données est demandée, effectue cette évaluation en utilisant la méthode check_column_patterns de la classe Analyse.
        - Enregistre les résultats de l'évaluation et les incohérences dans des fichiers CSV.
        - Affiche un graphique basé sur les résultats de l'évaluation.
    - Si l'utilisateur n'entre ni "1" ni "2", affiche un message d'erreur.
    - La boucle while continue jusqu'à ce que l'utilisateur choisisse une option valide.
"""


if __name__ == '__main__':
    site_url = 'https://sharepoint.com' 
    sharepoint = Sharepoint(site_url)
    sharepoint.authenticate()
    s = sharepoint.connection
    share_point = "/sites/" + input("Veuillez entrer le nom du sharepoint\n") 
    while True:
        menu = input("Voulez-vous faire un dossier (1) ou des fichiers (2) ? \n")
        if menu == "1": 
            files_error = []
            root_path = "Documents partages"
            files = File(s,site_url+share_point)
            print(site_url+share_point)
            root_items = files.get_folders(root_path)
            directory_target = input("Entrez un nom de Dossier ou chemin cible :").replace("%20"," ")
            folder_list = files.select_folders(root_items,directory_target)
            for file_input in tqdm(folder_list):
                try :
                    file_name,file = files.upload(file_input)
                    df_list,sheet_name = files.create_df(file_name,file)
                    for (sheet,df) in zip(sheet_name,df_list):
                        analyse = Analyse(df)
                        result_df = analyse.execute()
                        analyse.create_directory(file_input)
                        result_df.to_csv(f".{(file_input.replace('.xlsx','')).replace('.csv','')}_{sheet}_Describe.csv")
                        clear_output()
                except:
                    files_error.append([file_input])
            if len(files_error)>0:
                print(f"Nombre de fichier en erreur:{len(files_error)}")
                pd.DataFrame(files_error).to_csv(f".{share_point}files_error.csv")                    
            break
        elif menu == "2":
            files = File(s,site_url+share_point)
            while files.rework():
                file_name,file = files.upload()
                df_list,sheet_name = files.create_df(file_name,file)
                menu2 = input('Voulez-vous evaluler la qualité de donnée à partir du data dictionnary ?\n1 pour Oui et 0 pour Non\n')
                for sheet,df in zip(sheet_name,df_list):
                    analyse = Analyse(df)
                    name = f"{file_name.split('.')[0]}_{sheet}"
                    result_df = analyse.execute()
                    print(f"{name}.csv")
                    analyse.create_directory(f"{file_name.split('.')[0]}/result/X")
                    result_df.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Describe.csv")
                    if(menu2 == "1"):
                        pattern_df = pd.read_excel("Mobilite Dictionnary [11-05-2023].xlsx","Dictionnary")
                        result,mismatch = analyse.check_column_patterns(df, pattern_df) 
                        result.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Quality.csv")
                        mismatch.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Mismatch.csv")
                        analyse.plot(result,f"./{file_name.split('.')[0]}/result/{name}")                   
            break
        else:
            print("Saisie incorrecte. Veuillez entrer 1 ou 2.")