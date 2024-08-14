import hashlib
import random
import string
import time
import requests
from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions

# 常量配置
APPID = '123456'  # 替换自己的
SECRETKEY = 'abcdef'  # 替换自己的
BASEURL = 'http://127.0.0.1:40000'  # 接口地址无需更改
DEFAULT_ENV_ID = '18228'  # 替换自己的环境ID


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


def start_environment(env_id=DEFAULT_ENV_ID):
    """启动指定的 MoreLogin 环境，并返回调试端口。"""
    headers = create_request_headers()
    payload = {
        "envId": env_id,
    }
    try:
        res = requests.post(f"{BASEURL}/api/env/start", json=payload, headers=headers)
        res.raise_for_status()  # 检查请求是否成功
        data = res.json()
        # pprint.pprint(data)
        return data['data']['debugPort']
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def open_browser(debug_port, url):
    page = None
    if debug_port:
        try:
            co = ChromiumOptions().set_local_port(debug_port)
            page = ChromiumPage(co)
            print(f"浏览器[ {DEFAULT_ENV_ID} ]：接管成功")
            print('Morelogin注册链接(15天免费50个环境)：https://www.morelogin.com/?from=AA5enIPURMdF')
            print('如果你使用了我的链接注册，我可以提供共享脚本或技术支持，加我微信：lumaoyangmao')
        except Exception as e:
            print(f"无法打开浏览器页面: {e}")
    else:
        print("无效的调试端口，无法启动浏览器。")

    # 可继续续写自动化相关代码
    page.get(url)


if __name__ == '__main__':
    url = 'https://x.com/lumaoyangmao'  # 目标 URL

    # 启动环境并获取调试端口
    debug_port = start_environment(DEFAULT_ENV_ID)

    # 打开浏览器
    open_browser(debug_port, url)
