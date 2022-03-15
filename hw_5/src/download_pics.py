import os
from typing import Tuple
import aiohttp
import aiofiles
import asyncio
import sys

PICS_SIZE = (300, 200)


async def download_pics(pics_cnt: int, output_dir: str, pics_size: Tuple[int, int] = PICS_SIZE):
    width, height = pics_size
    async with aiohttp.ClientSession() as session:
        url = f"https://picsum.photos/{width}/{height}?random="
        pics_ids = set()
        while len(pics_ids) != pics_cnt:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Bad response status: {response.status}")
                    continue
                pic_id = response.headers["picsum-id"]
                if pic_id in pics_ids:
                    print(f"Repeating pic: {pic_id}")
                    continue
                f = await aiofiles.open(f"{output_dir}/pic{len(pics_ids)}.jpg", mode="wb")
                await f.write(await response.read())
                await f.close()
                print(f"New pic #{len(pics_ids)} downloaded: {pic_id}")
                pics_ids.add(pic_id)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print("Required arguments: pics_cnt: int, output_dir: str")
        exit(1)

    pics_cnt = None
    try:
        pics_cnt = int(args[0])
    except ValueError:
        print("First argument pics_cnt must be int")
        exit(2)
    output_dir = args[1]
    try:
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    except FileNotFoundError:
        print("Second argument output_dir must be directory")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_pics(pics_cnt, output_dir))


if __name__ == '__main__':
    main()
