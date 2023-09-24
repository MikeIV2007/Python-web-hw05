from aiofile import async_open
import aiohttp
import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError
import names
import datetime

logging.basicConfig(level=logging.INFO)


async def get_exchange(date):

    async with aiohttp.ClientSession() as session:

        async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') as resp:
            if resp.status == 200:
                r = await resp.json()
                exchangeRate_list = r["exchangeRate"]
                excUSD, = list(filter(lambda el: el["currency"] == "USD", exchangeRate_list))
                excEUR, = list(filter(lambda el: el["currency"] == "EUR", exchangeRate_list))
            return f"{date} USD: buy: {excUSD['purchaseRate']:5}, sale: {excUSD['saleRate']:5} | EUR: buy: {excEUR['purchaseRate']:5}, sale: {excEUR['saleRate']:5}"


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            for client in self.clients:
                await client.send(message)

    async def log(self, message: str):
        async with async_open("exchange_log.txt", "a") as log_file:
            await log_file.write(message + '\n')

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws) 
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):        
        async for message in ws:
                
            message_list = message.strip().lower().split()
        
            if message_list[0] == 'exchange':
                try:
                    quantity = int(message_list[1])
                    if 0 < quantity <= 10:
                        quantity = quantity
                    else:
                        quantity = 10
                except (ValueError, IndexError):
                    quantity = 10
                dates = []
                current_date = datetime.date.today()
                for _ in range(quantity):
                    date = current_date.strftime("%d.%m.%Y")
                    dates.append(date)
                    current_date -= datetime.timedelta(days=1)
                await self.send_to_clients(f'Currencies rates for the last {quantity} days:\n')
                message_list = []
                for date in dates:
                    m = await get_exchange(date)
                    message_list.append(m)
                message = " || ".join(message_list)

                await self.log(f'{message}')
                logging.info("Message sent to log file")
                await self.send_to_clients(message)
                logging.info('Message sent to the clients')

            else:
                await self.send_to_clients(f"{ws.name}: {message}")
                
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())

# first start server-ws.py
# startr html server with LiveServer ( it will open google chrome)
# srart Microsoft Age and copy local host Url to it.
# chat between the browsers