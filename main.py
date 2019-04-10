import asyncio
import aiohttp
import xivapi


async def main(api_key):
    async with aiohttp.ClientSession() as session:
        client = xivapi.Client(session, api_key)

        i_search = await client.index_search(
            name='Curtana',
            indexes=['Item']
        )
        print(i_search)

        item = await i_search.results[0].get()
        print(item)
        # await asyncio.sleep(.1)
        print(item.params)


def run(s):
    asyncio.get_event_loop().run_until_complete(main(s))


if __name__ == '__main__':
    run('')
