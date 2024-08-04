import os
import csv
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyperclip
from DrissionPage import ChromiumPage, ChromiumOptions

# 初始化全局锁
lock = threading.Lock()


def save_to_csv(address, seed_phrase_list):
    filename = 'xverse.csv'
    file_exists = os.path.isfile(filename)

    with lock:  # 使用锁来防止多个线程同时写入文件时发生冲突
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                writer.writerow(['Address', 'Seed Phrase'])  # 写入表头

            # 将助记词列表转换为单个字符串
            seed_phrase = ' '.join(seed_phrase_list)

            writer.writerow([address, seed_phrase])

    print(f"地址与助记词数据已保存到 {filename}")


def create_wallet():
    chrome_options = ChromiumOptions().auto_port().set_argument('--lang=en').add_extension(r'D:\llq\detail\Xverse-Wallet')
    page = ChromiumPage(addr_or_opts=chrome_options)
    page.set.timeouts(0.1)

    page.get('https://wallet.xverse.app/whitelist')
    sleep(2)
    tab = page.get_tab(title='Xverse Wallet')

    while True:
        try:
            tab('text=Create a new wallet').click()
            sleep(1)
        except Exception:
            pass
        try:
            tab('text=Accept').click()
            sleep(1)
        except Exception:
            pass
        try:
            tab('text=Backup now').click()
            sleep(1)
        except Exception:
            pass
        try:
            tab('text=Reveal').click()
            sleep(2)
            unique_elements = tab.eles('t:p@translate=no')
            seed_phrase_list = [element.text for element in unique_elements]
            if seed_phrase_list:
                print(seed_phrase_list)
        except Exception:
            pass

        try:
            tab('text=Continue').click()
            sleep(0.5)
        except Exception:
            pass

        mnemonic_index_element = tab('t:span@text():th') or tab('t:span@text():st') or tab('t:span@text():rd') or tab('t:span@text():nd')
        if mnemonic_index_element:
            mnemonic_index_text = mnemonic_index_element.text[-2:]
            mnemonic_index = int(mnemonic_index_element.text.split(mnemonic_index_text)[0])
            mnemonic_word = seed_phrase_list[mnemonic_index - 1]
            try:
                tab(f'@value={mnemonic_word}').click()
                sleep(1)
            except Exception:
                pass

        try:
            tab('@@type=password@@value=').input('Lumaoyangmao\n')  # 钱包密码
            sleep(0.5)
        except Exception:
            pass

        try:
            tab('text=Close this tab').click()
            sleep(1)
            break
        except Exception:
            pass
        sleep(1)

    while True:
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

    page.get('chrome-extension://hmocdlaipfjakhcngkfcpfkmgapbogfo/options.html#/')
    while True:
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

    save_to_csv(wallet_address, seed_phrase_list)
    page.quit()  # 关闭浏览器
    return wallet_address, seed_phrase_list


def main(iterations, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(create_wallet) for _ in range(iterations)]

        for i, future in enumerate(as_completed(futures)):
            try:
                address, seed_phrase_list = future.result()
                print(f"第 {i + 1} 个任务创建成功。钱包地址: {address}")
            except Exception as e:
                print(f"执行第 {i + 1} 个任务时出错: {e}")
            sleep(2)


if __name__ == "__main__":
    # 获取用户输入的线程数和执行次数
    try:
        print('钱包密码在85行，默认Lumaoyangmao，浏览器用完即销毁，密码不重要，保存好助记词文件即可。')
        iterations = int(input("要执行多少次？(输入数字并回车): "))
        max_workers = int(input("要开几个线程？(输入数字并回车): "))
        main(iterations, max_workers)
        print("所有线程执行完毕。")
    except ValueError:
        print("请输入有效的数字")
