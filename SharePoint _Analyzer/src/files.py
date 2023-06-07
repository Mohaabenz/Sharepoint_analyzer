from getpass import getpass
from io import BytesIO
from tqdm import tqdm
import pandas as pd

class File:
    def __init__(self, s,site_url):
        """
        Initialise une instance de la classe File.

        Args:
            s (object): Session d'authentification pour SharePoint.
            site_url (str): URL du site SharePoint.
        """
        self.s = s
        self.site_url = site_url

        
    def get_folders(self, folder):
        """
        Récupère les dossiers et fichiers dans un dossier SharePoint et ses sous-dossiers.

        Args:
            folder (str): Chemin relatif du dossier SharePoint.

        Returns:
            list: Liste des dossiers et fichiers trouvés avec leurs chemins.
        """
        # Récupération des informations du dossier
        r = s.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{folder}')?$expand=Folders,Files")
        data = r.json()
        # Création d'une liste pour stocker les dossiers et fichiers trouvés
        items = []

        # Récupération des sous-dossiers
        if 'd' in data :
            if 'Folders' in data['d']:
                for sub_folder in data['d']['Folders']['results']:
                    # Appel récursif de la fonction pour récupérer les sous-dossiers et fichiers du sous-dossier
                    sub_items = self.get_folders(sub_folder['ServerRelativeUrl'])
                    items.extend(sub_items)
            # Récupération des fichiers
            if 'Files' in data['d']:
                for file in data['d']['Files']['results']:
                    if file['Name'].endswith('.csv') or file['Name'].endswith('.xlsx'):
                        # Ajout du fichier à la liste des items
                        items.append({
                            'name': file['Name'],
                            'path': folder + '/' + file['Name']
                        })
        return items
    
    def select_folders(self,root_items,folder_name):
        """
        Sélectionne les dossiers contenant un nom spécifique dans une liste de dossiers.

        Args:
            root_items (list): Liste des dossiers racines.
            folder_name (str): Nom du dossier recherché.

        Returns:
            list: Liste des chemins des dossiers correspondants.
        """
        folder_list = []
        for item in tqdm(root_items):
            if folder_name in item['path']:
                folder_list.append(item['path'])
        return folder_list
    
    def display_folders(self, root_items, folder_name):
        """
        Affiche les fichiers CSV trouvés dans un dossier SharePoint et ses sous-dossiers.

        Args:
            root_items (list): Liste des dossiers racines.
            folder_name (str): Nom du dossier recherché.
        """
        for item in root_items:
            if folder_name in item['path']:
                print(item['path'])
        
    def upload(self,file_input=""):
        """
        Télécharge un fichier depuis SharePoint.

        Args:
            file_input (str, optional): Chemin relatif du fichier SharePoint. Si vide, l'utilisateur est invité à entrer le lien.

        Returns:
            tuple: Nom du fichier téléchargé, fichier sous forme de BytesIO.
        """
        timer = status_code = 0
        while status_code != 200:
            while True:
                try:
                    if file_input == "":
                        file_url = input('Entrez le lien de votre document : \nExemple : https://sharepoint.com/sites/sitename/path/file.csv\n').split('?')[0].replace(":x:/r/","")
                    else :
                        file_url = "https://sharepoint.com/"+file_input
                    print('Recherche du fichier')
                    r = self.s.get(file_url)
                    r.raise_for_status()  # vérifier si une exception est levée
                    file = BytesIO(r.content)
                    status_code = r.status_code
                    break
                except :
                    print("Le lien du fichier est invalide ou une erreur de connexion s'est produite. Réessayez...")
            if(status_code == 200):
                print('Fichier trouvé !')
            else:
                print("Le lien du fichier est invalide ou une erreur de connexion s'est produite. Réessayez...")
        print("Chargement réussi !")
        file_name = file_url.split('/')[-1].replace("%20","_").replace("%5","_")
        return file_name, file
               
    def create_df(self, file_name, file):
        """
        Crée un DataFrame à partir d'un fichier CSV ou Excel.

        Args:
            file_name (str): Nom du fichier.
            file (BytesIO): Fichier sous forme de BytesIO.

        Returns:
            tuple: Liste de DataFrames et liste des noms de feuilles (si le fichier est Excel).
        """
        df_list =[]
        # Lire le fichier CSV/EXCEL en tant que dataframe
        sheet_name =[]
        if ".csv" in file_name:
            df = pd.read_csv(file, sep=";", encoding='latin', low_memory=False)
            sheet_name.append("_")
            df_list.append(df)
        else:
            if ".xlsx" in file_name:
                xls_type = "openpyxl"
            elif ".xls" in file_name:
                xls_type = "xlrd"
            elif ".ods" in file_name:
                xls_type = "odf"
            else:
                raise ValueError("Le format du fichier n'est pas pris en charge.")
            xls = pd.ExcelFile(file,engine=xls_type)
            sheet_name = xls.sheet_names
            for sheet in sheet_name:
                df = pd.read_excel(xls, sheet_name=sheet)
                df_list.append(df)
        return df_list,sheet_name
    
    def rework(self):
        """
        Demande à l'utilisateur s'il souhaite analyser un autre fichier.

        Returns:
            int: 1 si l'utilisateur souhaite analyser un autre fichier, 0 sinon.
        """
        while True:
            try:
                # demande à l'utilisateur de saisir un nombre
                value = int(input("Voulez-vous analyser un autre fichier ?\n 1: OUI ou 0: NON\nEntrez le numero\n"))
                # vérifie si le nombre est entre les bornes
                if 0 <= value <= 1: 
                    return value
                    break
                else: print(f"Valeur incorrecte")
            except ValueError:
                print("Valeur incorrecte. Saisissez un nombre.")