import asyncio
import platform
import datetime
from pathlib import Path
import sys

import aiohttp


async def request(date, currency):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
        ) as recponse:
            if recponse.status == 200:
                result = await recponse.json()
                exchangeRate_list = result["exchangeRate"]
                exc_dict = {}
                (exc,) = list(
                    filter(lambda el: el["currency"] == currency, exchangeRate_list)
                )
                exc_dict["sale"] = exc["saleRateNB"]
                exc_dict["purchase"] = exc["purchaseRateNB"] 
                return exc_dict
            
def get_dates(quantity):
    dates = []
    current_date = datetime.date.today()
    for _ in range(quantity):
        date = current_date.strftime("%d.%m.%Y")
        dates.append(date)
        current_date -= datetime.timedelta(days=1) 
    return dates  


def get_currensies_list(additional_currency):
    currencies_list = ["USD", "EUR"]
    additional_carrencis_list = [
        "AUD",
        "AZN",
        "BYN",
        "CAD",
        "CHF",
        "CNY",
        "CZK",
        "DKK",
        "GBP",
        "GEL",
        "HUF",
        "ILS",
        "JPY",
        "KZT",
        "MDL",
        "NOK",
        "PLN",
        "SEK",
        "SGD",
        "TMT",
        "TRY",
        "UAH",
        "UZS",
        "XAU",
    ]
    if additional_currency in additional_carrencis_list:
        currencies_list.append(additional_currency)
    return currencies_list


def get_args():
    try:
        message = sys.argv
    except IndexError:
        return print("input is not correct!")
    if len(message) >= 2:
        try:
            quantity = int(message[1].strip())
            if 0 < quantity <= 10:
                quantity = quantity
            else:
                quantity = 10
        except ValueError:
            quantity = 10
    else:
        quantity = 10

    if len(message) == 3:
        additional_currency = message[2].strip().upper()
    else:
        additional_currency = None
    currensies_list = get_currensies_list(additional_currency)
    return quantity, currensies_list


def main():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    quantity, currensies_list = get_args()
    dates = get_dates(quantity)
    
    date_dict = {} 
    for date in dates:
        currency_dict = {}
        for currency in currensies_list:
            exc_dict  = asyncio.run(request(date, currency))
            currency_dict[currency] = exc_dict
        date_dict[date] = currency_dict
    result_list = [date_dict]
    print (f'\nDays quantity: {quantity},  Currenscies: {currensies_list}: \n\n{result_list}\n')
    #print (result_list)


if __name__ == "__main__":
    main()
    # py main.py 2 PLN
    # py main.py 4
    # py main.py
    # py main
    # py main.py 3 gbp
    # py main.py fhds sjl


"""
[
  {'03.11.2022': {'EUR': {'sale': 39.,'purchase': 38.4},'USD': {'sale': 39.9,'purchase': 39.4}}},
  {'02.11.2022': {'EUR': {'sale': 39.4,'purchase': 38.4},'USD': {'sale': 39.9,'purchase': 39.4}}}
]
"""
