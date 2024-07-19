# DrissionPage 指纹浏览器接管工具

![GitHub stars](https://img.shields.io/github/stars/your-username/your-repo-name?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/your-repo-name?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/your-repo-name)
![GitHub license](https://img.shields.io/github/license/your-username/your-repo-name)

## 项目简介

本项目提供了使用 DrissionPage 库接管各种指纹浏览器的简单示例。目前已实现对 AdsPower 的支持，其他指纹浏览器的支持将陆续添加。


### 安装依赖

```bash
pip install drissionpage requests

adspower示例：

serial_number = 1  # 环境编号
open_url = f"http://localhost:50325/api/v1/browser/start?serial_number={serial_number}"
resp = requests.get(open_url, timeout=10).json()
if resp.get("code") == 0:
    debug_port = int(resp["data"]["debug_port"])
    page = ChromiumPage(debug_port)
    print(f"环境 {serial_number} 已成功启动或接管")
    page.new_tab(url='https://x.com/lumaoyangmao')
    # 在这里继续使用 page 对象进行后续操作
