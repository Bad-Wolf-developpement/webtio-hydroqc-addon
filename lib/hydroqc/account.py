"""Hydroquebec Account Module."""
from hydroqc.logger import get_logger
from hydroqc.error import HydroQcError


class Account:
    """Hydroquebec account.

    Represents an account (compte)
    """

    def __init__(
        self,
        webuser_id,
        customer_id,
        account_id,
        contracts,
        hydro_client,
        log_level=None,
    ):
        """Create an Hydroquebec account."""
        self._logger = get_logger(
            f"a-{account_id}", log_level, parent=f"w-{webuser_id}.c-{customer_id}"
        )
        self._no_partenaire_demandeur = webuser_id
        self._no_partenaire_titulaire = customer_id
        self._no_compte_contrat = account_id
        self._hydro_client = hydro_client
        self.contracts = contracts
        self._address = ""
        self._address = ""
        self._balance = ""
        self._balance_unpaid = ""
        self._last_bill = ""
        self._bill_date_create = ""
        self._bill_date_due = ""
        self._bill_date_next = ""

    @property
    def webuser_id(self):
        """Get webuser id."""
        return self._no_partenaire_demandeur

    @property
    def customer_id(self):
        """Get customer id."""
        return self._no_partenaire_titulaire

    @property
    def account_id(self):
        """Get account id."""
        return self._no_compte_contrat

    async def get_info(self):
        """Fetch latest data of this account."""
        self._logger.info("Get account info")
        data = await self._hydro_client.get_account_info(
            self.webuser_id, self.customer_id, self.account_id
        )
        self._address = data["adresse"].strip()
        self._balance = data["solde"]
        self._balance_unpaid = data["solde"]
        self._last_bill = data["montant"]
        self._bill_date_create = data["dateEmission"]
        self._bill_date_due = data["dateEcheance"]
        self._bill_date_next = data["dateProchaineFacture"]
        return data

    @property
    def balance(self):
        """Get current balance."""
        return self._balance

    def get_contract(self, contract_id):
        """Find contract by id."""
        contracts = [c for c in self.contracts if c.contract_id == contract_id]
        if not contracts:
            raise HydroQcError(f"Contract {contract_id} not found")
        return contracts[0]

    def __repr__(self):
        """Represent object."""
        return f"""<Account - {self.webuser_id} - {self.customer_id} - {self.account_id}>"""
