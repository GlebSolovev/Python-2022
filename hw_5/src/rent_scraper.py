import json
import os
import re
from typing import List, Dict, NoReturn, Optional, Any
import asyncio
from asyncio import TimeoutError

import aiofiles
from aiohttp import ClientSession, ClientProxyConnectionError, ServerDisconnectedError, ClientHttpProxyError, \
    ClientOSError
from bs4 import BeautifulSoup

from hw_5.src.proxies_pool import ProxiesPool

CIAN_URL = "https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&region=2"
PAGES_CHUNK_SIZE = 10
GET_PAGE_ATTEMPTS = 3

PROXY_CONNECTION_TIMEOUT_SECS = 3
SLEEP_BETWEEN_PARSE_PAGE_ATTEMPTS_SECS = 1
SLEEP_BETWEEN_PAGES_CHUNKS_SECS = 0

FLATS_FILE = "../artifacts/flats.json"

proxies_pool = ProxiesPool()


async def parse_flat_urls_from_page(session: ClientSession, url: str, page: int) \
        -> Optional[List[Any]]:
    global proxies_pool
    while proxies_pool.not_empty():
        proxy_url, proxy_id = proxies_pool.get_proxy()
        try:
            for _ in range(GET_PAGE_ATTEMPTS):
                async with session.get(f"{url}&p={page}", proxy=proxy_url,
                                       timeout=PROXY_CONNECTION_TIMEOUT_SECS) as response:
                    if response.status != 200:
                        print(f"Bad response status for page #{page}: {response.status}")
                        await asyncio.sleep(SLEEP_BETWEEN_PARSE_PAGE_ATTEMPTS_SECS)
                        continue
                    html = await response.text()
                    flat_urls = []
                    soup = BeautifulSoup(html, "html.parser")
                    # print(soup.prettify())
                    for link_area in soup.find_all("div", attrs={"data-name": "LinkArea"}):
                        for link in link_area.find_all(href=re.compile("/sale/flat/")):
                            flat_urls.append(link.get("href"))
                    print(f"Parsed {len(flat_urls)} flat urls from page #{page}")
                    # if len(flat_urls) == 0:
                    #     print(html)
                    return flat_urls
            print(f"Failed {GET_PAGE_ATTEMPTS} attempts to download page #{page}")
            return []
        except (ClientProxyConnectionError, ServerDisconnectedError, ClientHttpProxyError, ClientOSError, TimeoutError):
            print(f"Failed to connect to proxy: {proxy_url}")
            proxies_pool.delete_proxy(proxy_url, proxy_id)
            continue
    print(f"No proxies are left in proxies pool")
    return None


async def get_flat_urls() -> List[str]:
    flat_urls = []
    base_url = CIAN_URL

    global proxies_pool
    pool_is_ready = await proxies_pool.clear_and_update_pool()
    if not pool_is_ready:
        print("Failed to update proxies pool, aborting get_flat_urls")
        return []

    pages_chunk = 0
    while True:
        first_page = pages_chunk * PAGES_CHUNK_SIZE + 1
        print(f"Attempt to download {pages_chunk}-th pages chunk")
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        #     "Accept-Language": "en-US,en;q=0.5",
        #     # "Connection": "keep-alive"
        # }
        async with ClientSession() as session:
            pages_chunk_flat_urls = await asyncio.gather(
                *(parse_flat_urls_from_page(session, base_url, page) for page in
                  range(first_page, first_page + PAGES_CHUNK_SIZE))
            )
        print(f"Downloaded {pages_chunk}-th pages chunk")
        for page_flat_urls in pages_chunk_flat_urls:
            if page_flat_urls is None:
                print("Proxies pool became empty, aborting get_flat_urls")
                return []
            if not page_flat_urls:
                return flat_urls
            flat_urls += page_flat_urls
        pages_chunk += 1
        await asyncio.sleep(SLEEP_BETWEEN_PAGES_CHUNKS_SECS)


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
