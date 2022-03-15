import json
import os
import re
from typing import List, Dict, NoReturn
import asyncio

import aiofiles
from aiohttp import ClientSession
from bs4 import BeautifulSoup

CIAN_URL = "https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&region=2"
PAGES_CHUNK_SIZE = 1
GET_PAGE_ATTEMPTS = 3

FLATS_FILE = "../artifacts/flats.json"


async def parse_flat_urls_from_page(session: ClientSession, url: str, page: int) -> List[str]:
    for _ in range(GET_PAGE_ATTEMPTS):
        async with session.get(f"{url}&p={page}") as response:
            if response.status != 200:
                print(f"Bad response status for page #{page}: {response.status}")
                await asyncio.sleep(1)
                continue
            html = await response.text()
            flat_urls = []
            soup = BeautifulSoup(html, "html.parser")
            # print(soup.prettify())
            for link_area in soup.find_all("div", attrs={"data-name": "LinkArea"}):
                for link in link_area.find_all(href=re.compile("/sale/flat/")):
                    flat_urls.append(link.get("href"))
            print(f"Parsed {len(flat_urls)} flat urls from page #{page}")
            return flat_urls
    print(f"Failed to download page #{page}")


async def get_flat_urls() -> List[str]:
    flat_urls = []
    base_url = CIAN_URL
    pages_chunk = 0
    while True:
        first_page = pages_chunk * PAGES_CHUNK_SIZE + 1
        async with ClientSession() as session:
            pages_chunk_flat_urls = await asyncio.gather(
                *(parse_flat_urls_from_page(session, base_url, page) for page in
                  range(first_page, first_page + PAGES_CHUNK_SIZE))
            )
        for page_flat_urls in pages_chunk_flat_urls:
            if not page_flat_urls:
                return flat_urls
            flat_urls += page_flat_urls
        pages_chunk += 1


async def parse_flat_from_url(url: str) -> Dict[str, str]:
    return {"url": url}


async def get_and_save_flats() -> NoReturn:
    flat_urls = await get_flat_urls()
    flats = await asyncio.gather(
        *(parse_flat_from_url(url) for url in flat_urls)
    )
    async with aiofiles.open(FLATS_FILE, mode="w") as file:
        await file.write(json.dumps(flats))


def main():
    os.makedirs(os.path.dirname(FLATS_FILE), exist_ok=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_and_save_flats())


if __name__ == '__main__':
    main()
