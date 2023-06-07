import sharepy
from getpass import getpass
from re import match

class Sharepoint:
    def __init__(self, site_url):
        """
        Classe représentant une connexion à un site SharePoint.

        Args:
            site_url (str): L'URL du site SharePoint.

        Attributes:
            site_url (str): L'URL du site SharePoint.
            connection: La connexion établie avec SharePoint.
        """
        self.site_url = site_url
        self.connection = None

    def authenticate(self):
        """
        Authentifie l'utilisateur sur le site SharePoint.

        Cette méthode demande à l'utilisateur de saisir son nom d'utilisateur et son mot de passe,
        puis tente de se connecter au site SharePoint avec les informations fournies.

        Returns:
            object: L'objet de connexion établi avec SharePoint.

        Raises:
            Exception: Si l'email ou le mot de passe est invalide.

        Notes:
            Cette méthode effectue plusieurs tentatives de connexion en cas d'erreur d'authentification,
            et finit par quitter si le nombre maximal de tentatives est atteint.
        """
        timer = 0
        while True:
            timer += 1
            try:
                sharepoint_user = self._get_valid_username()
                sharepoint_password = getpass('Entrez votre mot de passe : \n')
                print('Connexion au SharePoint sharepoint.com en cours')
                # Connexion au SharePoint
                with sharepy.connect(self.site_url, username=sharepoint_user, password=sharepoint_password) as s:
                    self.connection = s
                print('Connexion réussie')
                return s
            except Exception as e:
                print(f"Email ou mot de passe invalide. ({e}) Ressayez...")
            if timer == 5 : quit()
        
    def _get_valid_username(self,a):
        """
        Demande à l'utilisateur son nom d'utilisateur et le valide avec une expression régulière.

        Returns:
            str: Le nom d'utilisateur valide.

        Notes:
            L'expression régulière utilisée vérifie si le nom d'utilisateur est au format attendu
            avec le domaine .
        """
        while True:
            username = input('\nSaisissez votre identifiant valide : \nExemple : IDENTIFIANT@COMMUN.FR\n')
            if match('^.+@.*\.?outlook\.fr$', username.lower()):
                return username
            else:
                print("Nom d'utilisateur invalide. Veuillez réessayer.") 