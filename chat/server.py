# https://youtu.be/8Juj_G_kDaE
# 6:00 01_aiohttp_client
# 18:00 01_2aiohttp_client_custom
# 20:30 01.3 2aiohttp_gether
# 26:30 01.4 request_privat
# 34:00 task_runner_asyncawait
# 52:20 file_sort_asincawait
# 1:00:00 sync_async
# 1:06:20 for await
# 1:12:20 asinc for
# 1:17:00 websocket / see folder chat


# code server form conspect Web socket witj permanent connection

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
    clients = set() # data base of clients / claients prermonently  connected to the cocket

    async def register(self, ws: WebSocketServerProtocol): # registration of clients (adding to database set())
        ws.name = names.get_full_name() # ws - web socket / getting random names of users to create a new web socket 
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol): # removes clients from database set()
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str): # sends message to all clients from database
        print (54, message)
        if self.clients:
            #[await client.send(message) for client in self.clients]
            for client in self.clients:
                await client.send(message) 

    async def ws_handler(self, ws: WebSocketServerProtocol): # processing of connection
        await self.register(ws)
        print (59, ws)
        try:
            await self.distrubute(ws) 
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol): # sends message to clients         
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
                print(83, quantity)
                dates = []
                current_date = datetime.date.today()
                for _ in range(quantity):
                    date = current_date.strftime("%d.%m.%Y")
                    dates.append(date)
                    current_date -= datetime.timedelta(days=1)
                await self.send_to_clients(f'Currencies rates for the last {quantity} days:\n')
                for date in dates:
                    m = await get_exchange(date)
                    await self.send_to_clients(m)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")
                
async def main(): # starts server
    server = Server()  
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())

# first start server-ws.py
# startr html server with LiveServer ( it will open google chrome)
# srart Microsoft Age and copy local host Url to it.
# chat between the browsers