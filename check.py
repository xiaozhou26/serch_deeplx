import asyncio
import json
import aiofiles
from aiohttp import ClientSession, ClientTimeout

# 定义缓冲区大小
BUFFER_SIZE = 5

async def check_url(session: ClientSession, url: str, max_retries=3):
    """
    检查 URL 并翻译文本
    :param session: aiohttp 会话
    :param url: 目标 URL
    :param max_retries: 最大重试次数
    :return: 元组 (URL, 响应 JSON)
    """
    payload = json.dumps({
        "text": "hello world",
        "source_lang": "EN",
        "target_lang": "ZH"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    for attempt in range(1, max_retries + 1):
        try:
            requests_url = url + "/translate"
            async with session.post(requests_url, headers=headers, data=payload) as response:
                response.raise_for_status()  
                response_json = await response.json()
                print(url, response_json)
                return url, response_json
        except Exception as e:
            print(f"Error for URL {url} (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(1)  

    print(f"All {max_retries} attempts failed. Defaulting to failure.")
    return url, {'code': None, 'data': None}  

async def process_urls(input_file, success_file):
    """
    处理输入 URL 列表，翻译文本并写入成功文件
    :param input_file: 输入文件
    :param success_file: 成功文件
    """
    unique_urls = set()  
    buffer = []  

    try:
        # 从成功文件中读取已处理过的 URL
        with open(success_file, 'r') as existing_file:
            existing_urls = {line.strip() for line in existing_file}
        unique_urls.update(existing_urls)
    except FileNotFoundError:
        pass  

    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    timeout = ClientTimeout(total=5)  # 5 秒超时时间
    async with ClientSession(timeout=timeout) as session:
        tasks = [check_url(session, url) for url in urls]
        for future in asyncio.as_completed(tasks):
            try:
                url, result = await future
                if url not in unique_urls and result.get('code') == 200 and '世界' in result.get('data', ''):
                    buffer.append(url)
                    unique_urls.add(url)
                    if len(buffer) >= BUFFER_SIZE:
                        # 写入成功文件
                        async with aiofiles.open(success_file, 'a') as valid_file:
                            await valid_file.write('\n'.join(buffer) + '\n')
                        buffer = []  
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    if buffer:
        # 写入成功文件
        async with aiofiles.open(success_file, 'a') as valid_file:
            await valid_file.write('\n'.join(buffer) + '\n')

def list_file(input_file, output_file):
    """
    将输入文件中的 URL 按行写入输出文件
    :param input_file: 输入文件
    :param output_file: 输出文件
    """
    with open(input_file, 'r') as input_file_content:
        lines = input_file_content.readlines()

    flattened_lines = ','.join(line.strip() for line in lines)

    with open(output_file, 'w') as result_file:
        result_file.write(flattened_lines)

asyncio.run(process_urls('input.txt', 'success.txt'))
list_file('success.txt', 'success_result.txt')

print ("all done")
