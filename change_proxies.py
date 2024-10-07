import requests
import random
import logging
import configparser

# 创建日志记录器
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 设置代理服务器的配置信息
port = '端口'
secret = '密钥'
selector = '机场名字'

headers_secret = {
    'Authorization': 'Bearer {}'.format(secret)
}

# 代理的URL信息
url_all_proxies_info = 'http://127.0.0.1:{}/proxies'.format(port)
url_all_proxies = 'http://127.0.0.1:{}/proxies/{}'.format(port, selector)

def change_proxy(url_all_proxies):
    try:
        # 获取当前的代理信息
        res_proxies = requests.get(url_all_proxies, headers=headers_secret).json()
        now_proxy = res_proxies['now']
        logger.info(f'现在的代理是 {now_proxy}')

        # 获取代理名称列表
        proxy_name_list = res_proxies['all']
        if len(proxy_name_list) > 6:
            proxy_name_list = proxy_name_list[3:-3]

        # 如果当前代理不在特殊代理列表中，且在代理列表里，则移除它
        if now_proxy not in ['DIRECT', 'REJECT', '账号邮箱看最新的地址', 'NETV2', '自动选择', '故障转移']:
            if now_proxy in proxy_name_list:
                proxy_name_list.remove(now_proxy)

        # 无限循环，直到找到延迟不为零的代理（有最大尝试次数限制）
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts:
            random_proxy = random.choice(proxy_name_list)
            proxies_info = requests.get(url_all_proxies_info, headers=headers_secret).json()
            delay = proxies_info['proxies'][random_proxy]['history'][-1]['delay']
            if delay != 0:
                break
            attempts += 1

        if attempts >= max_attempts:
            logger.error("未能找到合适的代理，尝试次数过多")
            return

        logger.info(f'随机选择的代理为 {random_proxy}')

        # 设置要更换的代理
        data = {
            "name": random_proxy
        }

        # 请求头，包含内容类型和授权信息
        headers = {
            "content-type": "application/json",
            'Authorization': f'Bearer {secret}'
        }

        # 发送 PUT 请求到代理服务器以更新当前使用的代理
        res = requests.put(url=url_all_proxies, json=data, headers=headers)

        # logger.info(f'切换代理请求的状态码为 {res.status_code}')

        if res.status_code == 204:
            logger.info(f'切换代理成功！现在的代理为 {random_proxy}')
        else:
            logger.error(f'切换代理失败，状态码：{res.status_code}')

    except Exception as e:
        logger.error(f"切换代理时出错: {e}")

if __name__ == "__main__":
    change_proxy(url_all_proxies=url_all_proxies)