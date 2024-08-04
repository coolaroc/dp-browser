import os
import csv
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyperclip
from DrissionPage import ChromiumPage, ChromiumOptions
from mnemonic import Mnemonic

# 初始化全局锁
lock = threading.Lock()


def save_to_csv(address, seed_phrase_list):
    filename = 'xverse.csv'
    file_exists = os.path.isfile(filename)

    with lock: 
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                writer.writerow(['Address', 'Seed Phrase'])  

            
            seed_phrase = ' '.join(seed_phrase_list)

            writer.writerow([address, seed_phrase])

    print(f"地址与助记词数据已保存到 {filename}")


def create_wallet():
    chrome_options = ChromiumOptions().auto_port().set_argument('--lang=en').add_extension(r'D:\llq\detail\Xverse-Wallet')
    page = ChromiumPage(addr_or_opts=chrome_options)
    page.set.timeouts(0.1)

    try:
        page.get('https://wallet.xverse.app/whitelist')
        sleep(2)


        # 生成助记词
        mnemo = Mnemonic("english")
        seed_phrase_list = mnemo.generate(strength=128).split()

        while True:
            tab = page.get_tab(title='Xverse Wallet')
            if tab:
                try:
                    tab('text=Restore an existing wallet').click()
                    sleep(1)
                except Exception:
                    pass

                try:
                    tab('text=Accept').click()
                    sleep(1)
                except Exception:
                    pass

                if tab('text=Enter your seedphrase to restore your wallet.'):
                    for i in range(12):
                        input_field = tab(f'#input{i}')
                        input_field.input(seed_phrase_list[i])
                        sleep(0.5) 
                    print(f"助记词已输入: {seed_phrase_list}")

                try:
                    tab('text=Continue').click()
                    sleep(0.5)
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
        return wallet_address, seed_phrase_list
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        page.quit()


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
    try:
        print('钱包密码在74行，默认Lumaoyangmao，浏览器用完即销毁，密码不重要，保存好助记词文件即可。')
        iterations = int(input("要执行多少次？(输入数字并回车): "))
        max_workers = int(input("要开几个线程？(输入数字并回车): "))
        main(iterations, max_workers)
        print("所有线程执行完毕。")
    except ValueError:
        print("请输入有效的数字")
