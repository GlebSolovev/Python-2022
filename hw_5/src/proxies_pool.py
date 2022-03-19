import asyncio
from random import shuffle
from typing import Tuple, Dict, NoReturn

from aiohttp import ClientSession
from bs4 import BeautifulSoup


class ProxiesPool:
    SSL_PROXIES_ORG = "https://www.sslproxies.org/"

    def __init__(self, change_proxy_attempts: int = 5, update_pool_attempts: int = 5):
        self.proxies = []
        self.cur_proxy_index = 0
        self.change_proxy_attempts = change_proxy_attempts
        self.get_proxy_attempts = 0
        self.update_pool_attempts = update_pool_attempts

    async def clear_and_update_pool(self) -> bool:
        for attempt in range(1, self.update_pool_attempts + 1):
            async with ClientSession() as session:
                async with session.get(self.SSL_PROXIES_ORG) as response:
                    if response.status != 200:
                        print(f"Bad response from {self.SSL_PROXIES_ORG}: {response.status}, attempt #{attempt}")
                        return False
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    proxies_table = soup.find(class_="table-responsive fpl-list")

                    self.proxies = []
                    self.cur_proxy_index = 0
                    self.get_proxy_attempts = 0
                    for row in proxies_table.tbody.find_all("tr"):
                        self.proxies.append({
                            "ip": row.find_all("td")[0].string,
                            "port": row.find_all("td")[1].string
                        })
                    shuffle(self.proxies)
                    if len(self.proxies) > 0:
                        print(f"Successfully updated proxies pool: {len(self.proxies)} proxies, attempt #{attempt}")
                        return True
                    print(f"Attempt #{attempt} failed: obtained zero proxies")
        print(f"Proxies pool update failed: {self.update_pool_attempts} attempts failed")
        return False

    @staticmethod
    def __convert_proxy_to_url(proxy_dict: Dict[str, str]) -> str:
        return "http://" + proxy_dict["ip"] + ":" + proxy_dict["port"]

    def get_proxy(self) -> Tuple[str, int]:
        self.get_proxy_attempts += 1
        if self.get_proxy_attempts >= self.change_proxy_attempts:
            self.switch_proxy()
        proxy = self.proxies[self.cur_proxy_index]
        return self.__convert_proxy_to_url(proxy), self.cur_proxy_index

    def switch_proxy(self):
        self.cur_proxy_index += 1
        self.cur_proxy_index %= len(self.proxies)
        self.get_proxy_attempts = 0

    def not_empty(self) -> bool:
        return len(self.proxies) > 0

    def delete_proxy(self, proxy_url: str, proxy_id: int) -> NoReturn:
        if proxy_id < len(self.proxies) and self.__convert_proxy_to_url(self.proxies[proxy_id]) == proxy_url:
            del self.proxies[proxy_id]
            self.get_proxy_attempts = 0
            if self.proxies:
                self.cur_proxy_index %= len(self.proxies)
            print(f"Deleted proxy, left: {len(self.proxies)}")


def main():
    loop = asyncio.get_event_loop()
    pool = ProxiesPool()
    loop.run_until_complete(pool.clear_and_update_pool())
    print(pool.proxies)
    print(pool.get_proxy())


if __name__ == '__main__':
    main()
