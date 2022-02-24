"""Hydroquebec contract module."""
from datetime import date, timedelta

from hydroqc.winter_credit.handler import WinterCreditHandler
from hydroqc.logger import get_logger


class Contract:
    """Hydroquebec contract.

    Represents a contract (contrat)
    """

    def __init__(
        self,
        webuser_id,
        customer_id,
        account_id,
        contract_id,
        hydro_client,
        log_level=None,
    ):
        """Create a new Hydroquebec contract."""
        self._logger = get_logger(
            f"c-{contract_id}",
            log_level=log_level,
            parent=f"w-{webuser_id}.c-{customer_id}.a-{account_id}",
        )
        self._no_partenaire_demandeur = webuser_id
        self._no_partenaire_titulaire = customer_id
        self._no_compte_contrat = account_id
        self._no_contrat = contract_id
        self._hydro_client = hydro_client
        wch_logger = self._logger.getChild("wch")
        self._wch = WinterCreditHandler(
            self.webuser_id,
            self.customer_id,
            self.contract_id,
            hydro_client,
            wch_logger,
        )
        self._address = ""
        self._mve_activated = None
        self._all_period_data = {}

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

    @property
    def contract_id(self):
        """Get contract id."""
        return self._no_contrat

    @property
    def winter_credit(self):
        """Get winter credit helper object."""
        return self._wch

    async def get_today_hourly_consumption(self):
        """Fetch hourly consumption for today."""
        return await self._hydro_client.get_today_hourly_consumption(
            self.webuser_id, self.customer_id, self.contract_id
        )

    async def get_hourly_consumption(self, date_wanted):
        """Fetch hourly consumption for a date."""
        return await self._hydro_client.get_hourly_consumption(
            self.webuser_id, self.customer_id, self.contract_id, date_wanted
        )

    async def get_daily_consumption(self, start_date, end_date):
        """Fetch daily consumption."""
        return await self._hydro_client.get_daily_consumption(
            self.webuser_id, self.customer_id, self.contract_id, start_date, end_date
        )

    async def get_today_daily_consumption(self):
        """TODO ????."""
        yesterday = date.today() - timedelta(days=1)
        today = date.today()
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        return await self.get_daily_consumption(start_date, end_date)

    async def get_monthly_consumption(self):
        """Fetch monthly consumption."""
        return await self._hydro_client.get_monthly_consumption(
            self.webuser_id, self.customer_id, self.contract_id
        )

    async def get_annual_consumption(self):
        """Fetch annual consumption."""
        return await self._hydro_client.get_annual_consumption(
            self.webuser_id, self.customer_id, self.contract_id
        )

    async def get_info(self):
        """Fetch info about this contract."""
        self._logger.info("Get contract info")
        data = await self._hydro_client.get_contract_info(
            self.webuser_id, self.customer_id, self.contract_id
        )
        self._address = data["adresseConsommation"].strip()
        self._meter_id = data["noCompteur"]
        self._mve_activated = data["indicateurMVE"]
        return data

    async def get_periods_info(self):
        """Fetch periods info."""
        self._all_period_data = await self._hydro_client.get_periods_info(
            self.webuser_id, self.customer_id, self.contract_id
        )
        return self._all_period_data

    async def get_latest_period_info(self):
        """Fetch latest period info."""
        if len(self._all_period_data):
            return self._all_period_data[0]
        return []

    # Current period properties
    # CP == Current period
    @property
    def cp_current_day(self):
        """Get number of days since the current period started."""
        return self._all_period_data[0]["nbJourLecturePeriode"]

    @property
    def cp_duration(self):
        """Get current period duration in days."""
        return self._all_period_data[0]["nbJourPrevuPeriode"]

    @property
    def cp_current_bill(self):
        """Get current bill since the current period started."""
        return self._all_period_data[0]["montantFacturePeriode"]

    @property
    def cp_projected_bill(self):
        """Projected bill of the current period."""
        return self._all_period_data[0]["montantProjetePeriode"]

    @property
    def cp_daily_bill_mean(self):
        """Daily bill mean since the current period started."""
        return self._all_period_data[0]["moyenneDollarsJourPeriode"]

    @property
    def cp_daily_consumption_mean(self):
        """Daily consumption mean since the current period started."""
        return self._all_period_data[0]["moyenneKwhJourPeriode"]

    @property
    def cp_total_consumption(self):
        """Total consumption since the current period started."""
        return self._all_period_data[0]["consoTotalPeriode"]

    @property
    def cp_projected_total_consumption(self):
        """Projected consumption of the current period started."""
        return self._all_period_data[0]["consoTotalProjetePeriode"]

    @property
    def cp_lower_price_consumption(self):
        """Total lower priced consumption since the current period started."""
        return self._all_period_data[0]["consoRegPeriode"]

    @property
    def cp_higher_price_consumption(self):
        """Total higher priced consumption since the current period started."""
        return self._all_period_data[0]["consoHautPeriode"]

    @property
    def cp_average_temperature(self):
        """Average temperature since the current period started."""
        return self._all_period_data[0]["tempMoyennePeriode"]

    @property
    def cp_kwh_cost_mean(self):
        """Mean cost of a kWh since the current period started."""
        if self._all_period_data[0]["coutCentkWh"] is not None:
            return self._all_period_data[0]["coutCentkWh"] / 100
        return None

    @property
    def cp_rate(self):
        """Get current period rate name."""
        return self._all_period_data[0]["dernierTarif"]

    @property
    def cp_epp_enabled(self):
        """Is EPP enabled for the current period.

        See: https://www.hydroquebec.com/residential/customer-space/
             account-and-billing/equalized-payments-plan.html
        """
        return self._all_period_data[0]["indMVEPeriode"]

    def __repr__(self):
        """Represent object."""
        return (
            f"""<Contract - {self.webuser_id} - {self.customer_id} - """
            """{self.account_id} - {self.contract_id}>"""
        )
