import asyncio
class MainClass():
    def __init__(self, client):
        self.client = client
        self.events=['on_message']

    async def on_message(self, message):
        print(message.content)
