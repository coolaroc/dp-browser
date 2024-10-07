import hashlib
import pprint
import random
import string
import time
import requests
from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from time import sleep


# 常量配置
APPID = '1587555449088158'  # 替换自己的
SECRETKEY = 'f1b60ed4819f4bdb9ff69d2f1c7eea70'  # 替换自己的
BASEURL = 'http://127.0.0.1:40000'  # 接口地址无需更改


def generate_random_string(length=6):
    """生成指定长度的随机字符串，由字母和数字组成。"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_nonce_id():
    """生成唯一的 nonceId，包含当前时间戳和随机字符串。"""
    return str(int(time.time() * 1000)) + generate_random_string()


def generate_md5_signature(nonce_id):
    """根据 APPID、nonceId 和 SECRETKEY 生成 MD5 哈希值。"""
    md5 = hashlib.md5()
    md5.update((APPID + nonce_id + SECRETKEY).encode('utf-8'))
    return md5.hexdigest()


def create_request_headers():
    """生成 API 请求的头部，包括身份验证信息。"""
    nonce_id = generate_nonce_id()
    md5_str = generate_md5_signature(nonce_id)
    return {
        'X-Api-Id': APPID,
        'Authorization': md5_str,
        'X-Nonce-Id': nonce_id
    }


def start_environment(env_id):
    """启动指定的 MoreLogin 环境，并返回调试端口。"""
    headers = create_request_headers()
    payload = {
        "envId": env_id,
    }
    try:
        res = requests.post(f"{BASEURL}/api/env/start", json=payload, headers=headers)
        res.raise_for_status()  # 检查请求是否成功
        data = res.json()
        pprint.pprint(data)
        return data['data']['debugPort']
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def open_browser(debug_port, url, evn_id):
    page = None
    if debug_port:
        try:
            co = ChromiumOptions().set_local_port(debug_port)
            page = ChromiumPage(co)
            print(f"环境ID：[ {evn_id} ]：接管成功")
            print('Morelogin注册链接(15天免费50个环境)：https://www.morelogin.com/?from=AA5enIPURMdF')
            print('如果你使用了我的链接注册，我可以提供共享脚本或技术支持，加我微信：lumaoyangmao')
        except Exception as e:
            print(f"无法打开浏览器页面: {e}")
    else:
        print("无效的调试端口，无法启动浏览器。")

    # 可继续续写自动化相关代码
    page.get(url)


def parse_range(range_string):
    """解析用户输入的范围字符串"""
    result = set()
    parts = range_string.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(list(result))

def get_ids_from_excel(filename='morelogin_ids.xlsx', indices=None):
    """从Excel文件中读取指定索引的id和env_id"""
    df = pd.read_excel(filename, names=['id', 'env_id'], dtype={'env_id': str})
    if indices:
        return df['env_id'].iloc[[i-1 for i in indices]].tolist()  # 转换为0-based索引
    return df['env_id'].tolist()

def process_environment(count, total, evn_id, url):
    print(f'[{count}/{total}] 等待打开环境ID：{evn_id}')
    debug_port = start_environment(evn_id)
    open_browser(debug_port, url, evn_id)

if __name__ == '__main__':
    url = 'https://x.com/lumaoyangmao'  # 目标 URL

    # 询问用户要执行的编号范围
    range_input = input("请输入要执行的编号范围（例如：10 或 1-5 或 1,3,5,7）: ")
    indices = parse_range(range_input)

    # 询问用户想要使用的线程数
    thread_count = int(input("请输入要使用的线程数: "))

    ids = get_ids_from_excel(indices=indices)
    total = len(ids)

    print(f"将处理 {total} 个环境，使用 {thread_count} 个线程")

    # 使用线程池执行任务
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        for count, evn_id in enumerate(ids, 1):
            future = executor.submit(process_environment, count, total, evn_id, url)
            futures.append(future)
            sleep(1)  # 在每次启动任务时增加1秒延迟

        # 等待所有任务完成
        for future in futures:
            future.result()

    print("所有任务已完成")
