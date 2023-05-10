import requests
from bs4 import BeautifulSoup
import telegram
import time
import re
from tqdm import trange

# 设置代理IP
proxies = None
#{
#    'http': 'http://127.0.0.1:1080',
#    'https': 'http://127.0.0.1:1080'
#}
# 如果您需要使用代理网络，请将其设置为代理的IP地址和端口号，否则将其设置为None

# 设置Telegram机器人
bot = telegram.Bot(token='6252585899:AAHePzEGAdM0QCfVICw5tq1rE_y_tRa-0Ko')
chat_id = '@iyangmao' # 修改为您要发送内容的Telegram频道的名称或ID
CHANNEL_ID = 1001865524540

# 设置Telegram通知警告发送机器人
notify_bot = telegram.Bot(token='6132385604:AAEFT6B7caldN3q9EFJTMgSW43-Phkmaf-M')
notify_chat_id = '@jinggaobot' # 修改为您要接收通知和警告的Telegram频道的名称或ID

# 设置京东联盟URL参数
jd_param = ''

# 设置广告内容
ad_content = '关注频道|转发|投稿联系@wafen_bot'

# 设置URL记录文件
url_file = 'url.txt'

# 设置白名单和黑名单
whitelist = [] # 留空不过滤白名单，格式：['红包', '京东']
blacklist = [] # 留空不过滤黑名单，格式：['怎么办', '什么']

# 设置爬取间隔时间
interval = 5

# 读取URL记录文件
def read_url_file():
    if not url_file:
        return []
    urls = []
    with open(url_file, 'r') as f:
        for line in f:
            urls.append(line.strip())
    return urls

# 写入URL记录文件
def write_url_file(urls):
    if not url_file:
        return
    with open(url_file, 'w') as f:
        for url in urls:
            f.write(url + '\n')

# 添加URL到记录文件
def add_url_to_file(url):
    if not url_file:
        return
    urls = read_url_file()
    urls.append(url)
    if len(urls) > 300:
        urls = urls[-300:]
    write_url_file(urls)

# 判断URL是否已经存在
def is_url_exist(url):
    if not url_file:
        return False
    urls = read_url_file()
    return url in urls

# 判断内容是否包含白名单或黑名单关键词
def is_content_valid(content):
    if not whitelist and not blacklist:
        return True
    if whitelist:
        for keyword in whitelist:
            if keyword in content:
                return True
    if blacklist:
        for keyword in blacklist:
            for keyword in blacklist:
                if keyword in content:
                    return False
    return True

# 处理京东联盟短链接
def process_jd_link(url):
    if not jd_param:
        return url
    if 'https://u.jd.com/' in url:
        match = re.search(r'https://u.jd.com/(\w+)', url)
        if match:
            short_url = match.group(0)
            param = match.group(1)
            new_url = url.replace(short_url, '') + jd_param + param
            return new_url
    return url

# 爬取0818tuan
def crawl_0818tuan():
    print('正在爬取0818tuan...')
    url = 'https://www.0818tuan.com/'
    try:
        response = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('.list-item'):
            title = item.select_one('.title a').text.strip()
            link = item.select_one('.title a')['href']
            if not is_url_exist(link) and is_content_valid(title):
                link = process_jd_link(link)
                publish_to_telegram(title, link)
                add_url_to_file(link)
    except Exception as e:
        print('爬取0818tuan出错：', e)
        notify_error('爬取0818tuan出错：' + str(e))

# 爬取zhuanyes
def crawl_zhuanyes():
    print('正在爬取zhuanyes...')
    url = 'https://www.zhuanyes.com/'
    try:
        response = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('.list-item'):
            title = item.select_one('.title a').text.strip()
            link = item.select_one('.title a')['href']
            if not is_url_exist(link) and is_content_valid(title):
                link = process_jd_link(link)
                publish_to_telegram(title, link)
                add_url_to_file(link)
    except Exception as e:
        print('爬取zhuanyes出错：', e)
        notify_error('爬取zhuanyes出错：' + str(e))

# 爬取TG频道
def crawl_telegram():
    print('正在爬取TG频道...')
    try:
        for message in bot.get_updates():
            if message.message and message.message.text:
                content = message.message.text.strip()
                link = ''
                if message.message.entities:
                    for entity in message.message.entities:
                        if entity.type == 'url':
                            link = entity.url
                            break
                if not is_url_exist(link) and is_content_valid(content):
                    link = process_jd_link(link)
                    publish_to_telegram(content, link)
                    add_url_to_file(link)
    except Exception as e:
        print('爬取TG频道出错：', e)
        notify_error('爬取TG频道出错：' + str(e))

# 发送Telegram通知
def send_telegram_notification(message):
    notify_bot.send_message(chat_id=notify_chat_id, text=message)

# 发布内容到Telegram
def publish_to_telegram(content, link):
    message = content + '\n' + link + '\n\n' + ad_content
    bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

# 发送错误通知
def notify_error(message):
    send_telegram_notification('错误通知：' + message)

# 主函数
def main():
    for i in trange(100):
        crawl_0818tuan()
        crawl_zhuanyes()
        crawl_telegram()
        time.sleep(interval)

if __name__ == '__main__':
    main()
