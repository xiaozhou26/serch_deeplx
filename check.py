import aiohttp
import asyncio
import json

async def check_url(session, url, max_retries=5):
    payload = json.dumps({
        "text": "hello world",
        "source_lang": "EN",
        "target_lang": "ZH"
    })
    headers = {'Content-Type': 'application/json'}

    for attempt in range(1, max_retries + 1):
        try:
            requests_url = url + "/translate"
            async with session.post(requests_url, headers=headers, data=payload) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses
                response_json = await response.json()
                return response_json, url
        except Exception as e:
            print(f"Error for URL {url} (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(1)  # Sleep for 1 second before retrying

    return {'code': None, 'data': None}, url  # Default values in case of failure

async def process_urls(input_file, success_file):
    unique_urls = set()
    success_results = []

    try:
        with open(success_file, 'r') as existing_file:
            existing_urls = {line.strip() for line in existing_file}
        unique_urls.update(existing_urls)
    except FileNotFoundError:
        pass

    with open(input_file, 'r') as file:
        urls = [url.strip() for url in file.readlines()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for url in urls]
        for future in asyncio.as_completed(tasks):
            result, url = await future
            if url not in unique_urls and result.get('code') == 200 and '世界' in result.get('data', ''):
                unique_urls.add(url)
                success_results.append(url)

    with open(success_file, 'w') as valid_file:
        for url in success_results:
            valid_file.write(url + '\n')

def list_file(input_file, output_file):
    with open(input_file, 'r') as input_file_content:
        lines = input_file_content.readlines()

    flattened_lines = ','.join(line.strip() for line in lines)

    with open(output_file, 'w') as result_file:
        result_file.write(flattened_lines)

async def main():
    await process_urls('input.txt', 'success.txt')
    list_file('success.txt', 'success_result.txt')

asyncio.run(main())
