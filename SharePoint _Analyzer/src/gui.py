import tkinter as tk
from tkinter import filedialog
from sharepoint import Sharepoint
from files import File
from analyse import Analyse
import pandas as pd

# Fonction pour effectuer l'authentification
def authenticate_sharepoint():
    site_url = entry_sharepoint.get()
    username = entry_username.get()
    password = entry_password.get()
    sharepoint = Sharepoint(site_url)
    sharepoint.authenticate(username, password)
    connection = sharepoint.connection
    label_connection_status.config(text="Connexion réussie")
    button_process_folders.config(state=tk.NORMAL)
    button_process_files.config(state=tk.NORMAL)
    # button_select_sharepoint.config(state=tk.NORMAL)

# # Fonction pour sélectionner le SharePoint
# def select_sharepoint():
#     sharepoint_url = entry_sharepoint.get()
#     sharepoint = Sharepoint(sharepoint_url)
#     sharepoint.authenticate(entry_username.get(), entry_password.get())
#     # sites = sharepoint.get_sites()
#     # site_options = [site["Title"] for site in sites]
#     # selected_sharepoint = tk.StringVar()
#     # selected_sharepoint.set(site_options[0])
#     # sharepoint_dropdown = tk.OptionMenu(window, selected_sharepoint, *site_options)
#     # sharepoint_dropdown.pack()
#     # button_select_sharepoint.config(state=tk.DISABLED)
#     button_process_folders.config(state=tk.NORMAL)
#     button_process_files.config(state=tk.NORMAL)

def process_folders():
    files_error = []
    root_path = entry_root_path.get()
    sharepoint_path = entry_sharepoint_path.get()
    files = File(connection, sharepoint_path)
    root_items = files.get_folders(root_path)
    directory_target = entry_directory_target.get().replace("%20", " ")
    folder_list = files.select_folders(root_items, directory_target)
    for file_input in folder_list:
        try:
            file_name, file = files.upload(file_input)
            df_list, sheet_name = files.create_df(file_name, file)
            for (sheet, df) in zip(sheet_name, df_list):
                analyse = Analyse(df)
                result_df = analyse.execute()
                analyse.create_directory(file_input)
                result_df.to_csv(f".{(file_input.replace('.xlsx', '')).replace('.csv', '')}_{sheet}_Describe.csv")
                clear_output()
        except:
            files_error.append([file_input])
    if len(files_error) > 0:
        print(f"Nombre de fichier en erreur:{len(files_error)}")
        pd.DataFrame(files_error).to_csv(f".{share_point}files_error.csv")

def process_files():
    files = File(connection, sharepoint_path)
    while files.rework():
        file_name, file = files.upload()
        df_list, sheet_name = files.create_df(file_name, file)
        menu2 = entry_menu2.get()
        for sheet, df in zip(sheet_name, df_list):
            analyse = Analyse(df)
            name = f"{file_name.split('.')[0]}_{sheet}"
            result_df = analyse.execute()
            print(f"{name}.csv")
            analyse.create_directory(f"{file_name.split('.')[0]}/result/X")
            result_df.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Describe.csv")
            if menu2 == "1":
                pattern_df = pd.read_excel("Mobilite Dictionnary [11-05-2023].xlsx", "Dictionnary")
                result, mismatch = analyse.check_column_patterns(df, pattern_df)
                result.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Quality.csv")
                mismatch.to_csv(f"./{file_name.split('.')[0]}/result/{name}_Mismatch.csv")
                analyse.plot(result, f"./{file_name.split('.')[0]}/result/{name}")

# Création de la fenêtre principale
window = tk.Tk()
window.title("Programme de traitement SharePoint")
window.geometry("600x400")

# Création des éléments de l'interface
label_sharepoint = tk.Label(window, text="URL SharePoint :")
entry_sharepoint = tk.Entry(window, width=50)

label_username = tk.Label(window, text="Identifiant SharePoint :")
entry_username = tk.Entry(window, width=50)

label_password = tk.Label(window, text="Mot de passe SharePoint :")
entry_password = tk.Entry(window, width=50, show="*")

button_authenticate = tk.Button(window, text="Authentifier", command=authenticate_sharepoint)

label_connection_status = tk.Label(window, text="")

label_sharepoint = tk.Label(window, text="Choisir un Sharepoint")
entry_sharepoint = tk.Entry(window, width=50)


# button_select_sharepoint = tk.Button(window, text="Sélectionner SharePoint", command=select_sharepoint, state=tk.DISABLED)

button_process_folders = tk.Button(window, text="Traiter les dossiers", command=process_folders, state=tk.DISABLED)
button_process_files = tk.Button(window, text="Traiter les fichiers", command=process_files, state=tk.DISABLED)

# Placement des éléments dans la fenêtre
label_sharepoint.pack()
entry_sharepoint.pack()

label_username.pack()
entry_username.pack()

label_password.pack()
entry_password.pack()

button_authenticate.pack()
label_connection_status.pack()

# button_select_sharepoint.pack()
button_process_folders.pack()
button_process_files.pack()

# Lancement de la boucle principale de l'interface
window.mainloop()