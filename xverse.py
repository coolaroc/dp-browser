import os
import csv
import threading
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyperclip
from DrissionPage import ChromiumPage, ChromiumOptions
from mnemonic import Mnemonic
import uuid

# 初始化全局锁
lock = threading.Lock()

def save_to_csv(address, seed_phrase_list):
    """将地址和助记词保存到 CSV 文件中"""
    main_filename = 'xverse.csv'
    temp_filename = f'xverse_temp_{uuid.uuid4().hex}.csv'  # 使用唯一的临时文件名

    with lock:  # 使用锁来防止多个线程同时写入文件时发生冲突
        with open(temp_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # 将助记词列表转换为单个字符串
            seed_phrase = ' '.join(seed_phrase_list)
            writer.writerow([address, seed_phrase])

    # 确保将临时文件内容写入主文件
    with lock:
        if os.path.exists(main_filename):
            with open(main_filename, 'a', newline='', encoding='utf-8') as mainfile:
                with open(temp_filename, 'r', newline='', encoding='utf-8') as tempfile:
                    reader = csv.reader(tempfile)
                    writer = csv.writer(mainfile)
                    for row in reader:
                        writer.writerow(row)
        else:
            os.rename(temp_filename, main_filename)

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    # print(f"地址与助记词数据已保存到 {main_filename}")

def create_wallet():
    """创建钱包并返回钱包地址和助记词列表"""
    chrome_options = ChromiumOptions().auto_port().set_argument('--lang=en').add_extension(r'D:\llq\detail\Xverse-Wallet')
    page = ChromiumPage(addr_or_opts=chrome_options)
    page.set.timeouts(0.1)

    try:
        # 生成助记词
        mnemo = Mnemonic("english")
        seed_phrase_list = mnemo.generate(strength=128).split()
        while True: # 通过标签页数量判断弹出钱包
            if page.tabs_count > 1:
                page.close_tabs(others=True)
                page.get('chrome-extension://hmocdlaipfjakhcngkfcpfkmgapbogfo/options.html#/')
                break
            sleep(1)
        # 处理创建钱包的循环，最多尝试60次
        for _ in range(60):
            try:
                page('text=Restore an existing wallet').click()
                sleep(1)
            except Exception:
                pass

            try:
                page('text=Accept').click()
                sleep(1)
            except Exception:
                pass

            if page('text=Enter your seedphrase to restore your wallet.'):
                for i in range(12):
                    input_field = page(f'#input{i}')
                    input_field.input(seed_phrase_list[i])
                    sleep(0.5)  # 添加一个短暂的延迟，以确保输入顺利
                print(f"助记词已输入: {seed_phrase_list}")

            try:
                page('text=Continue').click()
                sleep(0.5)
            except Exception:
                pass

            try:
                page('@@type=password@@value=').input('Lumaoyangmao\n')  # 钱包密码
                sleep(0.5)
            except Exception:
                pass

            if page('text=Close this tab'):
                sleep(1)
                break
            sleep(1)
        else:
            page.quit()
            return False

        # 处理注册的超时循环
        start_time = time()
        timeout = 60  # 设置超时时间为60秒
        page.get('https://wallet.xverse.app/whitelist')
        while True:
            if time() - start_time > timeout:
                print("注册过程超时")
                page.quit()
                return False

            try:
                page('text=Register').click()
                page.wait(1)
            except Exception:
                pass

            tab = page.get_tab(title='Xverse Wallet')
            if tab:
                try:
                    tab('text=Connect').click()
                    page.wait(1)
                except Exception:
                    pass

            if page('text=Registration successful'):
                sleep(2)
                break
            sleep(1)

        # 获取钱包地址
        page.get('chrome-extension://hmocdlaipfjakhcngkfcpfkmgapbogfo/options.html#/')
        for _ in range(60):
            try:
                page('t:div@text()=Receive').click()
                page.wait(1)
            except Exception:
                pass
            try:
                page('#:copy-address-Ordinals').click()
                page.wait(1)
            except Exception:
                pass
            try:
                page('text=I understand').click()
                page.wait(1)
                wallet_address = pyperclip.paste()
                break
            except Exception:
                pass
            sleep(1)
        else:
            page.quit()
            return False

        save_to_csv(wallet_address, seed_phrase_list)
        return wallet_address, seed_phrase_list
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        page.quit()

def main(iterations, max_workers=4):
    """主函数，管理多线程执行"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(create_wallet) for _ in range(iterations)]

        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                if result:
                    address, seed_phrase_list = result
                    print(f"第 {i + 1} 个任务创建成功。钱包地址: {address}")
                else:
                    print(f"第 {i + 1} 个任务失败。")
            except Exception as e:
                print(f"执行第 {i + 1} 个任务时出错: {e}")
            sleep(2)

if __name__ == "__main__":
    try:
        print('钱包密码在74行，默认Lumaoyangmao，浏览器用完即销毁，密码不重要，保存好助记词文件即可。地址与助记词数据保存在同目录下 xverse.csv 中')
        iterations = int(input("要执行多少次？(输入数字并回车): "))
        max_workers = int(input("要开几个线程？(输入数字并回车): "))
        main(iterations, max_workers)
        print("所有线程执行完毕。")
    except ValueError:
        print("请输入有效的数字")
