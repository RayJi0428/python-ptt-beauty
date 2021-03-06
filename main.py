import os
import requests
import codecs
import json
from bs4 import BeautifulSoup

# -------------------------------------------------------------------------------------------

token = os.environ["BEAUTY"]
line_notify_url = "https://notify-api.line.me/api/notify"
line_header = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/x-www-form-urlencoded"
}

# -------------------------------------------------------------------------------------------
# 發送Line訊息


def NotifyLineMessage(msg):
    print('NotifyLineMessage ' + msg)
    # function docstring
    payload = {'message': msg}
    req_line = requests.post(
        line_notify_url, headers=line_header, params=payload)
    return req_line.status_code

# -------------------------------------------------------------------------------------------
# 發送Line圖片


def NotifyLineImage(imageURL):
    print('NotifyLineImage ' + imageURL)
    # function docstring
    payload = {'message': imageURL, 'imageThumbnail': imageURL,
               'imageFullsize': imageURL}
    req_line = requests.post(
        line_notify_url, headers=line_header, params=payload)
    return req_line.status_code

# -------------------------------------------------------------------------------------------
# 讀取版
def loadPage(url, cookies):
    req = requests.get(url, cookies = cookies)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# -------------------------------------------------------------------------------------------
# 解析PTT格式
def parsePTT(soup):
    # 搜尋新聞格式的tag
    news_tag = soup.select('.r-ent a')

    for i in range(len(news_tag)):
        # 標題
        title = news_tag[i].text.strip()

        # 略過不要的標題
        if '公告' in title or '帥哥' in title or '肉特' in title or '大尺碼' in title:
            continue

        # 略過已處理標題
        if title in ptt_log:
            continue

        # 紀錄標題
        ptt_log.append(title)

        page_url = ptt_domain + news_tag[i].attrs['href']  # 頁面連結
        page_req = requests.get(page_url, cookies={'over18': '1'})  # 標記我已滿18
        page_soup = BeautifulSoup(page_req.text, 'html.parser')
        pic_tag = page_soup.select('a[href]')  # 搜尋所有圖片超連結
        notify_title = False
        for i in range(len(pic_tag)):
            file_name = os.path.basename(pic_tag[i].text)
            # 確定連結是圖片才處理
            if '.jpg' in file_name or '.png' in file_name:
                # 標題只發送一次
                if notify_title == False:
                    notify_title = True
                    print('開始下載......' + title)

                    # 發送line訊息
                    NotifyLineMessage(title + "\n" + page_url)

                # 發送line圖片
                NotifyLineImage(pic_tag[i].text)

                # 儲存本地圖片
                #os.makedirs(title, exist_ok=True)
                #img = requests.get(pic_tag[i].text)
                #save = open(os.path.join(title, file_name), 'wb')
                # for chunk in img.iter_content(100000):
                #    save.write(chunk)
                # save.close()

# -------------------------------------------------------------------------------------------
# 讀取log，用來判斷哪些新聞處理過
url_log_file = 'D:\\git\\py\\python-ptt-beauty\\log.txt'
log_file = codecs.open(
    url_log_file, 'r', encoding='utf-8')
ptt_log = log_file.read().split('|')
log_file.close()

# -------------------------------------------------------------------------------------------

ptt_domain = 'https://www.ptt.cc'
req_session = requests.session()
# 讀取表特版
soup = loadPage(ptt_domain + '/bbs/Beauty/index.html', {'over18': '1'})
parsePTT(soup)

# 讀取AV版
soup = loadPage(ptt_domain + '/bbs/japanavgirls/index.html', {'over18': '1'})
parsePTT(soup)

# -------------------------------------------------------------------------------------------
# 儲存標題紀錄
log_file = codecs.open(url_log_file, 'w', encoding='utf-8')
log_file.truncate()  # 清空
log_file.write("|".join(ptt_log))
log_file.close()

print("done")
