import random
import asyncio
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
import requests
import aiofiles
from tqdm import tqdm
from time import sleep
from codetiming import Timer
from aiohttp_socks import ProxyConnector

# active async proxy checker -------------------------------------------------------------------------------------------
# aiohttp_proxy = 'http://194.87.188.114:8000'
# requests_proxy = {'http': 'http://194.87.188.114:8000', 'https': 'http://194.87.188.114:8000'}
"""план:
1) прочитать файл, получить список прокси
2) реализовать функцию для дробления списка на n подсписков
3) реализовать асинхронную функцию, для проверки списка прокси на доступ и возврата рабочих прокси 
4) реализовать асинхронную функцию main() для сбора тасков и добавления их в цикл событий
5) запустить цикл событий """


def read_proxies_file(file_name: str) -> list:
    with open(file=file_name, mode='r') as file:
        result = set([line.strip() for line in file.readlines()])
    return list(result)


def chunk_list(data: list, chunks: int) -> list[list]:
    result = list()
    chunk_size = len(data) // chunks
    for i in range(chunks):
        temp = list()
        for j in range(chunk_size):
            temp.append(data.pop(0))
        result.append(temp)

    return result


async def check_http_https_proxies_list(data: list, url: str, proxy_type: str, result: list) -> None:
    for socket in data:
        proxy = f'{proxy_type}://{socket}'

        async with aiohttp.ClientSession() as session:
            retry_options = ExponentialRetry(attempts=2, start_timeout=0.5, max_timeout=2)
            retry_client = RetryClient(client_session=session, retry_options=retry_options)
            try:
                async with retry_client.get(url=url, proxy=proxy) as response:
                    if response.status == 200:
                        print(socket)
                        result.append(socket)
            except Exception as ex_:
                print(ex_)
                await asyncio.sleep(random.random())
                continue


async def main():
    url = 'https://stepik.org/'
    proxy_type = 'http'
    proxies_chunks = chunk_list(read_proxies_file(file_name=f'{proxy_type}.txt'), 10)
    result = list()
    tasks = list()

    for proxies in proxies_chunks:
        task = check_http_https_proxies_list(data=proxies, url=url, proxy_type=proxy_type, result=result)
        tasks.append(asyncio.create_task(task))

    await asyncio.wait(tasks)
    print(result)


if __name__ == '__main__':
    with Timer():
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(main=main())  # Elapsed time: 630.6373 seconds


########################################################################################################################
""" 100 elements         таймаут = 5            """
# 1 - Elapsed time: 58.3898 seconds
# 2 - Elapsed time: 27.2921 seconds
# 3 - Elapsed time: 20.6833 seconds
# 4 - Elapsed time: 15.0017 seconds
# 5 - Elapsed time: 12.2242 seconds
# 10 - Elapsed time: 7.3287 seconds
# 25 - Elapsed time: 6.2066 - 19.6449 seconds - пропускает
# 50 - Elapsed time: 5.1464 seconds - пропускает
# 100 - Elapsed time: 2.4367 - 22.6860 seconds - пропускает
# ----------------------------------------------------------------------------------------------------------------------
########################################################################################################################
"""active proxies 
['51.158.154.173:3128', '164.70.122.6:3128', '8.219.97.248:80', '45.225.184.18:999', '173.212.224.134:3129', 
'68.183.185.62:80', '173.212.224.134:3128', '103.74.147.26:83', '154.16.180.182:3128', '103.48.68.109:83', 
'166.104.231.44:8888', '34.196.10.189:9090', '8.242.205.41:9991', '103.152.232.194:8080', '85.25.91.156:5566', 
'198.12.122.226:3128', '45.167.253.129:999', '49.212.143.246:6666', '194.87.188.114:8000', '5.9.94.91:3128', 
'51.81.32.81:8888', '95.56.254.139:3128', '178.63.237.147:8080', '82.102.11.74:443', '173.212.200.30:3128', 
'115.144.101.200:10000', '103.131.157.174:8080', '45.119.82.101:3333', '14.140.131.82:3128', '113.133.161.189:9002', 
'201.91.82.155:3128', '115.144.109.179:10000', '103.242.119.88:80', '112.217.162.5:3128', '155.133.26.123:8080', 
'135.125.206.30:3128', '128.199.67.35:80', '191.97.15.19:999', '217.180.218.36:8080', '103.86.187.190:808', 
'45.70.236.194:999', '49.0.2.242:8090', '95.216.194.46:1081', '105.112.191.250:3128']



"""
########################################################################################################################
# async SOCKS proxy checker ---------------------------------------------------------------------------------------


# async def main():
#     async with aiofiles.open('socks4.txt', mode='r') as f:
#         for prx in tqdm(await f.readlines()):
#             # url = 'http://httpbin.org/ip'
#             url = 'https://stepik.org/'
#             connector = ProxyConnector.from_url(f'socks4://{prx}')
#             try:
#                 async with aiohttp.ClientSession(connector=connector, timeout=0.5) as session:
#                     async with session.get(url=url, timeout=2) as response:
#                         if response.status:
#                             print(f'good proxy, status_code -{response.status}-', prx, end='')
#             except Exception as _ex:
#                 continue
#
#
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(main())

"""
109.206.182.50:1080
204.10.182.34:39593

SOCKS4
good proxy, status_code -200- 31.210.134.114:13080-
good proxy, status_code -200- 212.200.118.254:4153
good proxy, status_code -200- 204.10.182.34:39593
good proxy, status_code -200- 212.31.100.138:4153
good proxy, status_code -200- 189.36.201.230:5678
good proxy, status_code -200- 95.140.126.82:1080
good proxy, status_code -200- 195.64.243.176:5678
good proxy, status_code -200- 212.5.132.74:5678
good proxy, status_code -200- 149.3.27.4:5678
good proxy, status_code -200- 178.48.68.61:4145
good proxy, status_code -200- 69.70.195.210:4145
good proxy, status_code -200- 109.68.189.22:54643
good proxy, status_code -200- 178.48.68.61:4145
good proxy, status_code -200- 187.216.144.170:5678
"""




