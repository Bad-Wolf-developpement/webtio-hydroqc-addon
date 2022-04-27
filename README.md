
webtio-hydroqc-addon

[![GitHub](https://img.shields.io/github/forks/Bad-Wolf-developpement/webtio-hydroqc-addon.svg?style=social&label=Fork&maxAge=2592000)](https://img.shields.io/github/forks/Bad-Wolf-developpement/webtio-hydroqc-addon.svg?style=social&label=Fork&maxAge=2592000)
![GitHub](https://img.shields.io/github/license/Bad-Wolf-Developpement/webtio-hydroqc-addon?style=social)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Bad-Wolf-developpement/webtio-hydroqc-addon?style=social)

This is addon create a thing for the hydro-quebec winter credit: https://www.hydroquebec.com/residential/customer-space/rates/dynamic-pricing.html.

This program offer dynamic rate that allow you to save money when you reduce your energy usage during peak event.

So this thing will be Active when a peek event is currently active, with optional pre-heat and post-heat event that allow to pre-heat the house, or to re-heat after the peak.

The configuration of the addon will required:

 - Name: Friendly name for the site
 - Username: Username (usually e-mail) for the Hydro-quebec website
 - Password: Password of your account
 - Customer number: as seen on your invoice(must be 10 digits so add 0 before)
 - Account number: as seen on your invoice
 - Contract number: as seen on your invoice(must be 10 digits so add 0 before)

This will allow the addon to fetch data from Hydro Quebec.

The addon provide the following information:
 - Active Event: if a peak event is currently active
 - Pre Heat Event: if a pre-heat event is currently active
 - Post Heat Event: if a post-heat event is currently active
 - Next Event: the next peak event if available
 - Last Sync: last sync with the Hydro Quebec website
 - Credit Earned: the currently total credit amount earned for the winter credit season

This addon is not produce or related to the Hydro Quebec employee.

Credit: Thank you to the hydroqc api developper (a community work still not related to Hydro Quebec) Source: <https://gitlab.com/hydroqc/hydroqc/>
