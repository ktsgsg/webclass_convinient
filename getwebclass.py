
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

class Chapter:
    def __init__(self,chaptername,sourceURL,cookies):
        self.chaptername = chaptername
        self.sourceURL = sourceURL
        self.cookies = cookies

class Content:
    def __init__(self,contentsname,chapters):
        self.contentsname = contentsname
        self.chapters = chapters

class Section:
    def __init__(self,sectionname,contents):
        self.sectionname = sectionname
        self.contents = contents

class wbClass:
    def __init__(self,Classname,sections):
        self.Classname = Classname
        self.sections = sections


# 指定フォルダに、ファイルのダウンロードが完了するまで待機する
def wait_file_download(path):
   # 待機タイムアウト時間(秒)設定
   timeout_second = 10

   # 指定時間分待機
   for i in range(timeout_second + 1):
       # ファイル一覧取得
       match_file_path = os.path.join(path,'*.*')
       files = glob.glob(match_file_path)

       # ファイルが存在する場合
       if files:
           # ファイル名の拡張子に、'.crdownload'が含むかを確認
           extensions = [file_name for file_name in files if '.crdownload' in os.path.splitext(file_name)]
           extensions = [file_name for file_name in files if '.tmp' in os.path.splitext(file_name)]
           # '.crdownload'が見つからなかったら抜ける
           if not extensions : break

       # 指定時間待っても .crdownload 以外のファイルが確認できない場合 エラー
       if i >= timeout_second:
           # 終了処理
           raise Exception('file cannnot be finished downloading!')

       # 一秒待つ
       time.sleep(1)
   
   return

def DownloadPDFfromPath(classname,sectionname,contentname,chaptername,f,cookies,driver):
    driver.get(f)
    wait_file_download("CLASS")
    print("DONWLOADING")
    object_url = f
    object_name = object_url[object_url.rfind('/') + 1:]
    filename, optional = os.path.splitext(object_name)
    filename = chaptername
    print(filename+optional)
    print(f"{classname}/{sectionname}/{contentname}/{filename+optional}")
    print(f"CLASS/{object_name}")
    shutil.copyfile(f"CLASS/{object_name}",f"{classname}/{sectionname}/{contentname}/{filename+optional}")

def getPDFfrom_txtbk_frame(driver:webdriver.Chrome,classname,sectionname,contentname):#PDFの取得 txtbk_frameの時pdfを取得する
    
    soup = BeautifulSoup(driver.execute_script("return document.body.childNodes[3].childNodes[1].contentDocument.body.innerHTML"),"html.parser")
    TOC = soup.find("table",{"id":"TOCLayout"})
    Chapters = soup.find_all("span",{"class":"size2 darkslategray"})
    n = driver.execute_script("return document.body.childNodes[3].childNodes[1].contentDocument.app.pageMax")
    chapters = []

    #print(f"+++++>Chapters {n}")
    for i in  range(int(n)):
        driver.execute_script(f"return document.body.childNodes[3].childNodes[1].contentDocument.app.movePageTo({i+1})")

        Chaptername = Chapters[i*2].get_text()+","+Chapters[i*2+1].get_text()

        time.sleep(2)
        try:
            pages = driver.execute_script("return document.body.childNodes[3].childNodes[3].contentDocument.body.childNodes[1].contentDocument.body.childNodes[1].getAttribute('href')")
            f = "https://rpwebcls.meijo-u.ac.jp" + pages
            #print(f"+++++>{f}")
            cookies = driver.get_cookies()
            chapters.append(Chapter(Chaptername,f,cookies))
            DownloadPDFfromPath(classname,sectionname,contentname,Chaptername,f,cookies,driver)
        except :
            print("+++++>パスなし")
        #cookies = driver.get_cookies()
    return chapters

def webclassPathManager(driver,path,classname,sectionname,contentname):
    if path == "/webclass/txtbk_frame.php":
        #print(f"+++++>{path}")
        return getPDFfrom_txtbk_frame(driver,classname,sectionname,contentname)
    
def getclass(driver,classname):#科目の授業内容の取得
    soup = BeautifulSoup(driver.page_source, "html.parser")#クラスのページのHTMLを取得
    works = soup.find_all("section",class_="cl-contentsList_folder")#授業内容の部分を取得
    sections = []
    #print("授業内容の取得中")
    #print(f"授業内容数:{len(works)}")
    for i in range(len(works)):
        titile = works[i].find("h4",class_="panel-title")
        #print("+>"+titile.get_text())#授業内容のタイトルを取得
        groups = works[i].find(class_="list-group").find_all("section",class_="cl-contentsList_listGroupItem")#授業内容のグループを取得
        contents = []
        os.makedirs(f"{calssname}/{titile.get_text()}", exist_ok=True)#ディレクトリの作成
        for j in range(len(groups)):
            try:
                grouptitile = groups[j].find("h4",class_="cm-contentsList_contentName").find("a")#授業内容のグループのタイトルを取得
                groupurl = grouptitile['href']
                #print(f"++>{grouptitile.get_text()},URL:{groupurl}")#授業内容のグループのタイトルを取得
                
                session_qs = urllib.parse.urlparse(groupurl).query#クエリパラメータを取得
                session_qd = urllib.parse.parse_qs(session_qs)#クエリパラメータを辞書型に変換
                #print(f"+++>コンテンツIDを取得するためのID:{session_qd['set_contents_id']}")#クエリパラメータを表示
                
                getacsurl = "https://rpwebcls.meijo-u.ac.jp/webclass/do_contents.php?reset_status=1&"+"set_contents_id="+session_qd["set_contents_id"][0]
                ##print(f"+++>コンテンツを取得するためのURL:{getacsurl}")#クエリパラメータを表示
                driver.get(getacsurl)#acsの値が必要そうなので、まずここを開いて資料を特定のところで開くすることができるようにする
                time.sleep(3)#将来的にURLが変わったら変更にする
                docontentsURL = driver.current_url#現在のURLを取得 内容をクリックした後のURLを取得,ここの内容で次の動きを決める
                doC = urllib.parse.urlparse(docontentsURL)#クエリパラメータを取得
                doCq = doC.query#クエリパラメータを取得
                ContentID = urllib.parse.parse_qs(doCq)['set_contents_id'][0]#クエリパラメータを辞書型に変換
                #print(f"++++>コンテンツのタイプ(URLのパスの部分):{doC.path}")
                #print(f"++++>コンテンツID:{ContentID}")
                os.makedirs(f"{calssname}/{i+1}回{titile.get_text()}/{grouptitile.get_text()}", exist_ok=True)
                chapters = webclassPathManager(driver,doC.path,classname,f"{i+1}回{titile.get_text()}",grouptitile.get_text())
                contents.append(Content(grouptitile.get_text(),chapters))
            except:
                print("++>この授業内容は閉鎖しています")
        sections.append(Section(f"{i+1}回{titile.get_text()}",contents))
    return sections