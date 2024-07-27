from DrissionPage import ChromiumOptions, ChromiumPage
import os
import socket

# 设置基础路径
base_path = r"D:\Browser"


# 获取空闲端口
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def parse_input(input_string):
    # 移除所有空白字符
    input_string = ''.join(input_string.split())

    # 解析输入
    numbers = set()
    for part in input_string.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            numbers.update(range(start, end + 1))
        else:
            numbers.add(int(part))

    return sorted(list(numbers))


if __name__ == "__main__":
    # 询问用户输入
    user_input = input("请输入要执行的浏览器编号，若编号不存在则自动创建。（支持格式：1, 1-3, 1,2,3）: ")

    # 解析用户输入
    browser_numbers = parse_input(user_input)

    print(f"将要执行的浏览器编号: {browser_numbers}")

    # 为每个浏览器配置参数
    for number in browser_numbers:
        debug_port = get_free_port()
        user_data_path = rf'D:\Browser\{number}'
        co = ChromiumOptions()
        co.set_paths(local_port=debug_port, user_data_path=user_data_path)
        page = ChromiumPage(addr_or_opts=co)
        page.get('https://x.com/lumaoyangmao')
