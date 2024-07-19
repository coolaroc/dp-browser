import requests
from time import sleep
from DrissionPage import ChromiumPage


def start_browser(serial_number):
    open_url = f"http://localhost:50325/api/v1/browser/start?serial_number={serial_number}"

    for attempt in range(5):
        try:
            resp = requests.get(open_url, timeout=10).json()
            if resp.get("code") == 0:
                debug_port = int(resp["data"]["debug_port"])
                return ChromiumPage(debug_port)
            else:
                print(f"\033[0;31m浏览器[{serial_number}]打开出错,正在重试...错误信息:[{resp}]\033[0m")
        except requests.RequestException as e:
            print(f"\033[0;31m请求失败: {e}\033[0m")

        sleep(1)

    raise Exception(f"无法启动浏览器 {serial_number}，已达到最大重试次数")


# 使用方法
serial_number = 1  # 环境编号

try:
    page = start_browser(serial_number)
    print(f"环境 {serial_number} 已成功启动或接管")
    # 在这里继续使用 page 对象进行后续操作
    page.new_tab(url='https://x.com/lumaoyangmao')
except Exception as e:
    print(f"错误: {e}")
