from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, random, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MultipleLite:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        ${Fore.GREEN + Style.BRIGHT}{"*" * 40}
{"*":<1}{" " * 38}{"*":>1}
{"*":<1}{" " * 9}${Fore.YELLOW + Style.BRIGHT}𝐅 𝐎 𝐑 𝐄 𝐒 𝐓 𝐀 𝐑 𝐌 𝐘{" " * 10}${Fore.GREEN + Style.BRIGHT}{"*":>1}
{"*":<1}{" " * 38}{"*":>1}
{"*":<1}${Fore.CYAN + Style.BRIGHT}        https://t.me/forestarmy{" " * 7}${Fore.GREEN + Style.BRIGHT}{"*":>1}
{"*":<1}{" " * 38}{"*":>1}
{"*" * 40}{Style.RESET_ALL}
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxyshare.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
        
    def hide_account(self, account):
        hide_account = account[:3] + '*' * 3 + account[-3:]
        return hide_account
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def generate_message(self, address: str):
        timestamp = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        nonce = int(timestamp.timestamp() * 1000)
        message = f"www.multiple.cc wants you to sign in with your Ethereum account: {address}\n\t     \nmessage:\nwebsite: www.multiple.cc\nwalletaddress: {address}\ntimestamp: {timestamp}\nNonce: {nonce}"
        return message

    def generate_signature(self, account: str, message: str):
        try:
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = signed_message.signature.hex()
            
            return signature
        except Exception as e:
            return None
    
    async def user_dashboard_login(self, address: str, message: str, signature: str, proxy=None, retries=3):
        url = "https://api.app.multiple.cc/WalletLogin"
        data = json.dumps({"walletAddr":address, "message":message, "signature":signature})
        headers = {
            **self.headers,
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "https://www.app.multiple.cc",
            "Referer": "https://www.app.multiple.cc/",
            "Sec-Fetch-Site": "same-site",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                else:
                    return None

    async def user_extension_login(self, dashboard_token: str, proxy=None, retries=3):
        url = "https://api.app.multiple.cc/ChromePlugin/Login"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {dashboard_token}",
            "Content-Length": '2',
            "Content-Type": "application/json",
            "Origin": "chrome-extension://ciljbjmmdhnhgbihlcohoadafmhikgib",
            "Sec-Fetch-Site": "none",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                else:
                    return None
                
    async def user_information(self, extension_token: str, proxy=None, retries=3):
        url = "https://api.app.multiple.cc/ChromePlugin/GetInformation"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {extension_token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                else:
                    return None
                
    async def send_keepalive(self, extension_token: str, proxy=None, retries=3):
        url = "https://api.app.multiple.cc/ChromePlugin/KeepAlive"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {extension_token}",
            "Content-Length": '0',
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "chrome-extension://ciljbjmmdhnhgbihlcohoadafmhikgib",
            "Sec-Fetch-Site": "none",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                else:
                    return None
    
    async def proxy_questions(self):
        while True:
            try:
                print(f"{Fore.WHITE+Style.BRIGHT}1. Run With Auto Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE+Style.BRIGHT}2. Run With Manual Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE+Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.WHITE+Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto Proxy" if choose == 1 else 
                        "With Manual Proxy" if choose == 2 else 
                        "Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run With {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def user_log(self, address: str, extension_token: str, proxy=None):
        while True:
            user = await self.user_information(extension_token, proxy)
            if user:
                runing_time = user['totalRunningTime']
                is_online = user['isOnline']
                status = "Node Connected" if is_online else "Node Disconnected"
                color = Fore.GREEN if is_online else Fore.RED

                formatted_time = self.format_seconds(runing_time)

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                    f"{color + Style.BRIGHT}{status}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Run Time:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}GET User Node Information Failed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
            await asyncio.sleep(random.randint(600, 610))
        
    async def process_accounts(self, account: str, use_proxy: bool):
        ping_count = 1
        proxy = None
        if use_proxy:
            proxy = self.get_next_proxy()

        address = self.generate_address(account)
        if not address:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Generate Address Failed.{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Check Ur Private Key First {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        message = self.generate_message(address)
        if not message:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Generate Message Failed.{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Check Ur Private Key First {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        signature = self.generate_signature(account, message)
        if not signature:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Generate Signature Failed.{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Check Ur Private Key First {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        dashboard_token = None
        while dashboard_token is None:
            dashboard_token = await self.user_dashboard_login(address, message, signature, proxy)
            if not dashboard_token:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET Dashboard Token Failed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )

                if not use_proxy:
                    return
                
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try With Next Proxy...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                await asyncio.sleep(1)
                
                proxy = self.get_next_proxy()
                continue

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} GET Dashboard Token Success {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            
            extension_token = await self.user_extension_login(dashboard_token, proxy)
            if not extension_token:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET Extension Token Failed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                return
            
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} GET Extension Token Success {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            
            await asyncio.create_task(self.user_log(address, extension_token, proxy))

            while True:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try To Send PING...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                send_ping = await self.send_keepalive(extension_token, proxy)
                if send_ping and send_ping['success']:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} PING {ping_count} Success {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(address)} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} PING {ping_count} Success {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    if use_proxy:
                        proxy = self.get_next_proxy()

                ping_count += 1

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Wait For 10 Minutes For Next PING...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                await asyncio.sleep(random.randint(600, 610))

    async def main(self):
        try:
            with open('privateKeys.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.proxy_questions()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

                if use_proxy and use_proxy_choice == 1:
                    await self.load_auto_proxies()
                elif use_proxy and use_proxy_choice == 2:
                    await self.load_manual_proxy()
                
                tasks = []
                for account in accounts:
                    account = account.strip()
                    if account:
                        tasks.append(self.process_accounts(account, use_proxy))
                        
                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = MultipleLite()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Multiple Lite Node - BOT{Style.RESET_ALL}                                       "                              
        )
