import asyncio
import json
import aiofiles
from aiohttp import ClientSession, ClientTimeout

BUFFER_SIZE = 5  # Define your buffer size here

async def check_url(session: ClientSession, url: str, max_retries=3):
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
    unique_urls = set()  
    buffer = []  

    try:
        with open(success_file, 'r') as existing_file:
            existing_urls = {line.strip() for line in existing_file}
        unique_urls.update(existing_urls)
    except FileNotFoundError:
        pass  

    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    timeout = ClientTimeout(total=10)  # 5 seconds timeout for the requests
    async with ClientSession(timeout=timeout) as session:
        tasks = [check_url(session, url) for url in urls]
        for future in asyncio.as_completed(tasks):
            try:
                url, result = await future
                if url not in unique_urls and result.get('code') == 200 and '世界' in result.get('data', ''):
                    buffer.append(url)
                    unique_urls.add(url)
                    if len(buffer) >= BUFFER_SIZE:
                        async with aiofiles.open(success_file, 'a') as valid_file:
                            await valid_file.write('\n'.join(buffer) + '\n')
                        buffer = []  
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    if buffer:
        async with aiofiles.open(success_file, 'a') as valid_file:
            await valid_file.write('\n'.join(buffer) + '\n')

def list_file(input_file, output_file):
    with open(input_file, 'r') as input_file_content:
        lines = input_file_content.readlines()

    flattened_lines = ','.join(line.strip() for line in lines)

    with open(output_file, 'w') as result_file:
        result_file.write(flattened_lines)

asyncio.run(process_urls('input.txt', 'success.txt'))
list_file('success.txt', 'success_result.txt')

print ("all done")
