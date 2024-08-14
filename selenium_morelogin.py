# pip install selenium
from selenium import webdriver

import sys
import asyncio
import traceback
import time
import hashlib
import random
import string
import requests

# count auth info for web-request
def requestHeader(appId, secretKey):
    nonceId = generateNonceId()
    md5Str = md5Encode(nonceId, appId, secretKey)
    return {
        'X-Api-Id': appId,
        'Authorization': md5Str,
        'X-Nonce-Id': nonceId
    }


# generate a random string
def generateRandom(length=6):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


# count globally unique ID
def generateNonceId():
    return str(int(time.time()* 1000)) + generateRandom()


# count signature parameter
def md5Encode(nonceId, appId, secretKey):
    md5 = hashlib.md5()
    md5.update((appId + nonceId + secretKey).encode('utf-8'))
    return md5.hexdigest()


# send web-request with POST
def postRequest(url, data, headers):
    headers['Content-Type'] = 'application/json'
    return requests.post(url, json=data, headers=headers)


# send web-request with GET
def getRequest(url, headers):
    return requests.get(url, headers=headers)


# 将 API ID 和 SECRETKEY 复制到下面。
APPID = ''
SECRETKEY = ''
BASEURL = 'http://127.0.0.1:40000'


async def main():
    try:
        # 环境名称 就是默认P-1那个，
        uniqueId = 1
        # 环境ID 启动按钮后面三个点，选择复制环境ID
        # 环境名称和环境ID可只填写一个，两个都填，优先使用环境ID
        envId = '1823684318728519683'
        debugUrl = await startEnv(envId, uniqueId, APPID, SECRETKEY, BASEURL)
        print(debugUrl)

        driver = createWebDriver(debugUrl)
        operationEnv(driver)
    except:
        errorMessage = traceback.format_exc()
        print('run-error: ' + errorMessage)

# create webdriver with exist browser
def createWebDriver(debugUrl):
    opts = webdriver.ChromeOptions()
    opts.set_capability('browserVersion', '126')
    opts.add_experimental_option('debuggerAddress', debugUrl)
    driver = webdriver.Chrome(options=opts)
    print(driver.current_url)
    return driver


async def startEnv(envId, uniqueId, appId, secretKey, baseUrl):
    requestPath = baseUrl + '/api/env/start'
    data = {
        'envId': envId,
        'uniqueId': uniqueId
    }
    headers = requestHeader(appId, secretKey)
    response = postRequest(requestPath, data, headers).json()

    if response['code'] != 0:
        print(response['msg'])
        print('please check envId')
        sys.exit()

    port = response['data']['debugPort']
    print('env open result:', response['data'])
    return '127.0.0.1:' + port


# open page and operation
def operationEnv(driver):
    driver.switch_to.new_window('tab')
    driver.get('https://x.com/lumaoyangmao')

    # 可续写自动化流程
    print('浏览器启动或接管成功')


if __name__ == '__main__':
    asyncio.run(main())