import aiohttp
from utils.env import env
from requests import post


async def lock_thread(thread_ts: str, channel_name: str):
    print("locking thread")

    async with aiohttp.ClientSession() as session:
        res = await session.post(
            f"{env.threadlocker_api_url}/lock?id={thread_ts}&key={env.threadlocker_api_key}&reason=resolved thread&user=dillonb07dev&channel={channel_name}&time=May 1 2025"
        )

    print(await res.text())
