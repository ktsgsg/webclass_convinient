
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import os.path
import sys
import glob
import urllib.parse
import requests
import pickle
from pathlib import Path
import shutil
import getwebclass


ID = input("ユーザーID>")
password = input("パスワード>")
os.makedirs("CLASS",exist_ok=True)

# Chromeドライバのパスとオプションを設定
chrome_options = Options()
#chrome_options.add_argument('--headless')  # ヘッドレスモードで起動
dldir_path = Path("CLASS")
dldir_path.mkdir(exist_ok=True)  # 存在していてもOKとする（エラーで止めない）
download_dir = str(dldir_path.resolve())  # 絶対パス
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True
})

# Chromeドライバを起動
driver = webdriver.Chrome(options=chrome_options)

# 指定したURLのページを開く
url ="https://rpwebcls.meijo-u.ac.jp/webclass/login.php?auth_mode=SAML"
driver.get(url)
LoadingPage = "Loading..."

while (LoadingPage in driver.page_source):
    time.sleep(0.1)
    ##print("ページを読み込み中")
time.sleep(1)  # ページが完全に読み込まれるまで待機
##print("ページに移動中")

driver.find_element(By.ID,"idToken1").send_keys(ID)  # IDを入力
driver.find_element(By.ID,"idToken2").send_keys(password)  # IDを入力
##print("IDとパスワードを入力中")
time.sleep(2) # ページが完全に読み込まれるまで待機

driver.find_element(By.ID,"loginButton_0").click()  # ログインボタンをクリック

while(( "https://rpwebcls.meijo-u.ac.jp/webclass/" in driver.current_url) != True):
    ##print(driver.current_url)
    time.sleep(0.1)
    
##print("ログイン成功")

soup = BeautifulSoup(driver.page_source, "html.parser")
wbclass = []

##print("ページのHTMLを取得中")

schedule_element = soup.find(id = "schedule-table")
hrefs = schedule_element.find_all("a", href=True)
for href in hrefs:
    divs = href.find_all("div")  # divタグを持つ要素を取得
    for n in divs:
        n.extract()
    name = href.get_text()
    calssname = name[9:]  # "授業名"の部分を取得
    #print(f"NAME{name}")  # 各リンクのURLを表示
    os.makedirs(calssname, exist_ok=True)  # ディレクトリを作成
    #そのURLを開く
    driver.get("https://rpwebcls.meijo-u.ac.jp"+href['href'])
    time.sleep(1)  # ページが完全に読み込まれるまで待機
    sections = getwebclass.getclass(driver,calssname)  # 授業内容を取得
    wbclass.append(getwebclass.wbClass(name[9:],sections))
    time.sleep(1)  # ページが完全に読み込まれるまで待機
    
#print(f"時間の数: {len(hrefs)}")  # リンクの数を表示



##print(schedule_element)  # ページのHTMLを表示
# ドライバを終了

driver.quit()