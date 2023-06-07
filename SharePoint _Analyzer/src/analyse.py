from statistics import median
from tqdm import tqdm
from json import loads
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import clear_output
import pandas as pd
import os


class Analyse:
    def __init__(self, df):
        """
        Initialise une instance de la classe Analyse.

        Args:
            df (DataFrame): Le DataFrame à analyser.
        """
        self.df = df

    def execute(self):
        """
        Cette fonction effectue l'analyse en elle-meme.
        
        Elle calcule le nombre de donnée de chaque colonne, les valeures nulles,
        les tailles des champs, les types, Top 10, Flop 10...
        
        Returns:
            DataFrame: avec l'analyse d'un CSV.
        """
        
        
        # Initialiser une liste pour stocker les résultats
        result_list = []
        # Boucler sur toutes les colonnes du dataframe
        
        df_count = len(self.df)
        for col in tqdm(self.df.columns):
            # Obtenir le type de données de la colonne
            col_type = self.df[col].dtype
            # print(col_type)
            # Obtenir le nombre total de données dans la colonne
            col_count = self.df[col].count()
            # Obtenir le nombre de valeurs nulles dans la colonne
            col_null_count = self.df[col].isnull().sum()
            # Obtenir le nombre de valeurs nulles dans la colonne
            percent_null = col_null_count * 100 / len(self.df)
            # Obtenir le nombre de valeurs uniques dans la colonne
            col_unique_count = self.df[col].nunique()
            # Obtenir la repartition de longueur de chaque champ dans la colonne
            col_len_count = self.df[col].astype(str).apply(len).value_counts().to_dict()
            # Obtenir le nombre de longueurs différentes dans la colonne
            col_diff_lengths = len(col_len_count)
            # Calculer le maximum, le minimum et la médiane des longueurs de champs
            col_max_length = max(col_len_count.keys())
            col_min_length = min(col_len_count.keys())
            col_median_length = median(col_len_count.keys())

            #Correction des class float en null quand elle sont null
            if(col_count == 0):
                col_type_list = ["<class 'null'>"]
                col_type_counts = {"<class 'null'>": col_null_count}
                col_type = "null"
            else : 
                # Obtenir la liste de tous les types de données présents dans la colonne
                col_type_list = [str(x) for x in self.df[col].apply(type).unique().tolist()]
                # Obtenir la répartition des types de données dans la colonne
                col_type_counts = self.df[col].apply(type).value_counts().to_dict()
                col_type_counts = {str(k): v for k, v in col_type_counts.items()}
                if col_null_count != 0 and "<class 'float'>" in col_type_list:
                    col_type_list.append("<class 'null'>")
                    col_type_counts["<class 'null'>"] = col_null_count
                    if col_null_count == col_type_counts["<class 'float'>"] :
                        col_type_counts.pop("<class 'float'>")
                        for e,i in enumerate(col_type_list) : 
                            if str(i) == "<class 'float'>": del col_type_list[e]
                    else : 
                        col_type_counts["<class 'float'>"] -= col_null_count                    
            # Obtenir le top 10 des valeurs dans la colonne
            col_top_10 = self.df[col].value_counts().head(10).to_dict()
            # Obtenir le flop 10 des valeurs dans la colonne
            col_flop_10 = self.df[col].value_counts().tail(10).to_dict()
            result_list.append({
                "Colonne": col,
                "Type de donnees": col_type,
                "Liste types de donnees": col_type_list,
                "Repartition des types de donnees": col_type_counts,
                "Repartition des longueurs" : col_len_count, 
                "Nombre de longueur differente" : col_diff_lengths,
                "Lougueur Max" : col_max_length, 
                "Longueur Min" : col_min_length,
                "Longueur Median" : col_median_length,
                "Nombre de ligne" :df_count,
                "Nombre de donnees": col_count,
                "Nombre de valeurs nulles": col_null_count,
                "Pourcentage de valeurs nulles" : round(percent_null,3),
                "Nombre de valeurs uniques": col_unique_count,
                # "Pourcentage de valeurs unique" : pourcent_unique,
                "Top 10 des valeurs": col_top_10,
                "Flop 10 des valeurs": col_flop_10})
            # clear_output()
        result_df = pd.DataFrame(result_list)
        return result_df
    
    def create_directory(self,file_input):
        
        """
        Cette fonction crée une hiérarchie de dossier s'ils n'existent pas.

        Args:
            file_imput (str): Le chemin à créer

        """
        
        directory = '.'
        for dire in file_input.split('/')[:-1]:
            directory = directory+"/"+dire
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def check_column_patterns(self,df, pattern_df):
        
        """
        Cette fonction évalue la qualité de la donnée en fonction de pattern.

        Args:
            df (DataFrame): Le DataFrame de la donnée 
            pattern_df (DataFrame): Le DataFrame avec les pattern

        Returns:
            DataFrame: Les analyses, les valeurs en erreurs.
        """
        
        mismatched_rows = []
        result = {}
        mismatch = {}
        for column in tqdm(self.df.columns):
            # print(column)
            count_null =  self.df[column].isnull().sum()
            length = self.df[column].count()

            pattern_list = pattern_df.loc[pattern_df["Colonne"].str.lower() == column.lower(), "Pattern"].item()
            # print(column)
            if pd.isna(pattern_list):
                continue        
            pattern_list = pattern_list.replace(' ', '').lower().split(',')
            matches = self.df[column].astype(str).str.lower().str.replace(' ', '').str.replace('\xa0','').str.replace(',','.').str.match('|'.join(pattern_list))

            if matches.all():
                result[column] = {
                    'match': 100.0,
                    'number_unmatch': 0,
                    'len': length,
                    'null': count_null
                }
            else:
                mismatched_data = self.df.loc[~matches, column]
                result[column] = {
                    'match': round((1 - len(mismatched_data) / len(self.df)) * 100, 2),
                    'number_unmatch': len(mismatched_data),
                    'len': length,
                    'null': count_null
                }
                mismatch[column] = json.loads(mismatched_data.to_json())
        result = pd.DataFrame(result).transpose()
        mismatch = pd.DataFrame(mismatch)
        return result,mismatch
    
    def plot(self,result,name):
        
        """
        Cette fonction crée un diagramme en histogramme à partir de résultats de l'évaluation de qualité.

        Args:
            result (DataFrame): Le DataFrame de la donnée 
            name (str): chemin et nom du graphique

        Returns:
            plt: crée un image dans le repertoire name
        """
        
        sns.set(style="whitegrid")

        # Tracer le graphique à barres horizontales avec Seaborn
        plt.figure(figsize=(15, 7))
        ax = sns.barplot(data=result, y=result.index, x='match', color="pink")
        plt.xlabel('Pourcentage')
        plt.ylabel('Colonnes')
        plt.title('Donnée correspondant au pattern du Data Dictionnaire',fontweight="bold")
        for p in ax.patches:
            width = p.get_width()
            height = p.get_height()
            x, y = p.get_xy()    
            ax.text(x + width + 2, y + height/2, f'{width:.1f}%', ha='center', va='center')

        ax.spines['left'].set_color('black')
        ax.spines['bottom'].set_color('black')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(axis='x', colors='red')
        ax.tick_params(axis='y', colors='black')
        ax.yaxis.label.set_color('blue')
        ax.xaxis.label.set_color('blue')
        ax.title.set_color('green')
        plt.savefig(f"{name}_matching_pattern.png")
        # Afficher le graphique
        plt.show()
        
        return plt