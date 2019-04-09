import asyncio
import aiohttp
import xivapi

api_key = ''


async def main():
    async with aiohttp.ClientSession() as session:
        client = xivapi.Client(session, api_key)

        i = await client.index_search(
            name='Infusion of Strength',
            indexes=['Item']
        )

        print(i)

        item = await client.index_by_id(
            index="Item",
            content_id=i['Results'][0]['ID'],
        )

        print(item)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
