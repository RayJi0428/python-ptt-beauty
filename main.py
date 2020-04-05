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

# 發送Line訊息


def NotifyLineMessage(msg):
    # function docstring
    payload = {'message': msg}
    req_line = requests.post(
        line_notify_url, headers=line_header, params=payload)
    return req_line.status_code

# 發送Line圖片


def NotifyLineImage(imageURL):
    # function docstring
    payload = {'message': imageURL, 'imageThumbnail': imageURL,
               'imageFullsize': imageURL}
    req_line = requests.post(
        line_notify_url, headers=line_header, params=payload)
    return req_line.status_code

# -------------------------------------------------------------------------------------------
# 搜尋頁面


def searchPage(tag):
    title = tag.text.strip()
    page_url = base_url + tag.attrs['href']
    page_req = requests.get(page_url, cookies={'over18': '1'})
    page_soup = BeautifulSoup(page_req.text, 'html.parser')
    pic_tag = page_soup.select('a[href]')
    notify_msg = False
    for i in range(len(pic_tag)):
        file_name = os.path.basename(pic_tag[i].text)
        # 確定有圖片才建立資料夾
        if '.jpg' in file_name or '.png' in file_name:
            if notify_msg == False:
                notify_msg = True
                print('開始下載......' + title)
                NotifyLineMessage(title + "\n" + page_url)
            NotifyLineImage(pic_tag[i].text)
            #os.makedirs(title, exist_ok=True)
            #img = requests.get(pic_tag[i].text)
            #save = open(os.path.join(title, file_name), 'wb')
            # for chunk in img.iter_content(100000):
            #    save.write(chunk)
            # save.close()


# -------------------------------------------------------------------------------------------
url_log_file = 'D:\\git\\py\\python-ptt\\log.txt'
log_file = codecs.open(
    url_log_file, 'r', encoding='utf-8')
ptt_log = log_file.read().split('|')
log_file.close()

base_url = 'https://www.ptt.cc'
req_session = requests.session()
req = requests.get(base_url + '/bbs/Beauty/index.html',
                   cookies={'over18': '1'})
soup = BeautifulSoup(req.text, 'html.parser')
tag = soup.select('.r-ent a')

for i in range(len(tag)):
    # 檢查標題是否已下載過
    title = tag[i].text.strip()
    if '[公告]' in title or '[帥哥]' in title:
        continue
    if title not in ptt_log:
        ptt_log.append(title)
        searchPage(tag[i])

log_file = codecs.open(url_log_file, 'w', encoding='utf-8')
log_file.truncate()  # 清空
log_file.write("|".join(ptt_log))
log_file.close()

print("done")
