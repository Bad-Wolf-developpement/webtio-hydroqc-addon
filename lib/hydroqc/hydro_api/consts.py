"""Hydroqc API Consts."""
# Always get the time using HydroQuebec Local Time
REQUESTS_TIMEOUT = 30
REQUESTS_TTL = 1

HOST_LOGIN = "https://connexion.hydroquebec.com"
HOST_SESSION = "https://session.hydroquebec.com"
HOST_SERVICES = "https://cl-services.idp.hydroquebec.com"
HOST_SPRING = "https://cl-ec-spring.hydroquebec.com"

# OAUTH PATHS
LOGIN_URL_1 = f"{HOST_LOGIN}/hqam/XUI/"  # not used
LOGIN_URL_2 = f"{HOST_LOGIN}/hqam/json/serverinfo/*"  # not used
AUTH_URL = f"{HOST_LOGIN}/hqam/json/realms/root/realms/clients/authenticate"
SECURITY_URL = f"{HOST_SESSION}/config/security.json"
TOKEN_URL = f"{HOST_LOGIN}/hqam/oauth2/access_token"
SESSION_REFRESH_URL = f"{HOST_SESSION}/oauth2/callback/silent-refresh"
AUTHORIZE_URL = f"{HOST_LOGIN}/hqam/oauth2/authorize"
LOGIN_URL_6 = f"{HOST_SERVICES}/cl/prive/api/v3_0/conversion/codeAcces"
CHECK_SESSION_URL = f"{HOST_LOGIN}/hqam/oauth2/connect/checkSession"
# Initialization uri
RELATION_URL = f"{HOST_SERVICES}/cl/prive/api/v1_0/relations"
INFOBASE_URL = f"{HOST_SERVICES}/cl/prive/api/v3_0/partenaires/infoBase"
# TODO avoid all the /portail/ URLs
SESSION_URL = f"{HOST_SPRING}/portail/prive/maj-session/"
# TODO avoid all the /portail/ URLs
CONTRACT_URL_3 = (
    f"{HOST_SPRING}/portail/fr/group/clientele/gerer-mon-compte/"  # not used
)
CONTRACT_URL = (
    f"{HOST_SERVICES}/cl/prive/api/v3_0/partenaires/"
    "calculerSommaireContractuel?indMAJNombres=true"
)
# CONTRACT_URL_4 = (f"{HOST_SERVICES}/cl/prive/api/v3_0/partenaires/"
#                  "calculerSommaireContractuel")

CUSTOMER_INFO_URL = f"{HOST_SERVICES}/cl/prive/api/v3_0/partenaires/infoCompte"

# TODO avoid all the /portail/ URLs
PORTRAIT_URL = f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation"
# TODO avoid all the /portail/ URLs
PERIOD_DATA_URL = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesPeriodesConsommation"
)

# TODO avoid all the /portail/ URLs
ANNUAL_DATA_URL = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesConsommationAnnuelles"
)

# TODO avoid all the /portail/ URLs
MONTHLY_DATA_URL = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesConsommationMensuelles"
)

# TODO avoid all the /portail/ URLs
DAILY_CONSUMPTION_API_URL = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesQuotidiennesConsommation"
)

# TODO avoid all the /portail/ URLs
HOURLY_CONSUMPTION_API_URL = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesConsommationHoraires"
)
# TODO avoid all the /portail/ URLs
HOURLY_DATA_URL_2 = (
    f"{HOST_SPRING}/portail/fr/group/clientele/portrait-de-consommation/"
    "resourceObtenirDonneesMeteoHoraires"  # not used
)

GET_WINTER_CREDIT_API_URL = (
    f"{HOST_SERVICES}/cl/prive/api/v3_0/tarificationDynamique/creditPointeCritique"
)
