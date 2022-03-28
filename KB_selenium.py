import urllib.request as ureq
from bs4 import BeautifulSoup as bs
import re
from multiprocessing import Pool
import requests
from selenium import webdriver
import numpy as np


class EHHelper:
    @staticmethod
    def EmitTagAndSpecialCh(str):
        str = EHHelper.RemoveTag(str)
        str = EHHelper.RemoveHtmlSpecialCh(str)
        str = EHHelper.RemoveSymbol(str)
        return str
    @staticmethod
    def RemoveTag(src):
        try:
            while True:
                s,e = EHHelper.FindTag(src)
                if s<e:
                    src = src[:s]+src[e+1:]
                else:
                    src = src[:e]+src[e+1:]
        except:
            return src
    @staticmethod
    def FindTag(src):
        s = src.index('<')
        e = src.index('>')
        return s,e
    @staticmethod
    def RemoveSymbol(src):
        dest = ""
        for elem in src:
            if str.isalpha(elem) or str.isspace(elem):
                dest+=elem
        return dest
    @staticmethod
    def RemoveHtmlSpecialCh(src):
        try:
            while True:
                s,e = EHHelper.FindHtmlSpecialCh(src)
                if s<e:
                    src = src[:s]+src[e+1:]
                else:
                    src = src[:e]+src[e+1:]
        except:
            return src
    @staticmethod
    def FindHtmlSpecialCh(src):
        s = src.index('&')
        e = src.index(';')
        return s,e
    @staticmethod
    def MssqlstrToStrKor(src):
        try:
            src = src.encode('ISO-8859-1')
            src = src.decode('euc-kr')
        except:
            return ""
        else:
            return src

'''
def cleantext(text):
    cleaned_text = re.sub('[a-zA-z]', '', text)  # 영어삭제
    cleaned_text = " ".join(cleaned_text.split())  # 필요없는 공백 삭제
    return cleaned_text
'''

# ELS -> 이엘스
# DLS -> 디엘스
# IRP -> 아이알피
# RP -> 알픠
# ISA -> 아이에세
# CMA -> 크마
# ELW -> 엘렙
# PRIME -> 픠라임
# WM -> 덥엠
# WRAP -> 덥렙
# Choice&Care -> 초케
# Choice Back -> 초백
# More Care -> 모케
# PLAZA -> 쁠라자
# DB -> 뎁베
# DC -> 뒤씨
# BEST -> 쵀고
# e-book -> 리북
# HTS -> 홈트레이딩서비스
# KB Prestige -> 프레스트지
# Premier -> 푸릐미얼
def cleantext(text):    # kb 증권 전용 cleaner
    cleaned_text = re.sub('ELS', '이엘스', text)
    cleaned_text = re.sub('DLS', '디엘스', cleaned_text)
    cleaned_text = re.sub('IRP', '아이알피', cleaned_text)
    cleaned_text = re.sub('ISA', '아이에세', cleaned_text)
    cleaned_text = re.sub('CMA', '크마', cleaned_text)
    cleaned_text = re.sub('ELW', '엘렙', cleaned_text)
    cleaned_text = re.sub('PRIME', '픠라임', cleaned_text)
    cleaned_text = re.sub('WM', '덥엠', cleaned_text)
    cleaned_text = re.sub('WRAP', '덥렙', cleaned_text)
    cleaned_text = re.sub('Choice&Care', '초케', cleaned_text)
    cleaned_text = re.sub('More Care', '모케', cleaned_text)
    cleaned_text = re.sub('PLAZA', '쁠라자', cleaned_text)
    cleaned_text = re.sub('DB', '뎁베', cleaned_text)
    cleaned_text = re.sub('DC', '뒤씨', cleaned_text)
    cleaned_text = re.sub('BEST', '쵀고', cleaned_text)
    cleaned_text = re.sub('e-book', '리북', cleaned_text)
    cleaned_text = re.sub('HTS', '홈트레이딩서비스', cleaned_text)
    cleaned_text = re.sub('Prestige', '프레스트지', cleaned_text)
    cleaned_text = re.sub('Premier', '푸릐미얼', cleaned_text)
    cleaned_text = re.sub('ETF', '이퉵', cleaned_text)
    cleaned_text = re.sub('ETN', '이퉨', cleaned_text)
    cleaned_text = re.sub('CFD', '차액거래', cleaned_text)
    cleaned_text = re.sub('[a-zA-Z]', '', cleaned_text)  # 영어삭제
    cleaned_text = " ".join(cleaned_text.split())  # 필요없는 공백 삭제
    return cleaned_text

def Collect(url):  # 내용 수집
    request = ureq.Request(url)
    response = ureq.urlopen(request)
    if response.getcode() != 200:
        return None
    else:
        return response

# selenium
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
# link list 생성
link_list = []
# link-title 딕셔너리 생성
link_title = {}
def get_link_list():    # 링크 받는 함수
    main_url = 'https://www.kbsec.com/go.able'
    driver.get(main_url)

    html = driver.page_source
    soup = bs(html, 'html.parser')
    # navi > ul > li:nth-child(1) > div > div.colgroup
    # navi > ul > li:nth-child(7) > div > div.colgroup
    # 제대로 가져왔는지 확인
    # 메뉴창의 링크 가져오기
    for i in range(1, 8):
        url_set = "https://www.kbsec.com%s"  # url form 만들어주기
        tags = soup.select('#navi > ul > li:nth-child(%d) > div > div.colgroup'%i)[0].find_all('a')
        for tag in tags:
            link_list.append(tag['href'])
            url_link = url_set % tag['href']  # url 변환
            link_title[url_link] = tag.text   # 링크-타이틀 매칭
    driver.close()
    return(link_list)

get_link_list()

link_set = list(set(link_list))

result_dic = {}

filter = EHHelper() # 필터
n = 1
for sub_link in link_set:      # 서브링크들 반복
    url_set = "https://www.kbsec.com%s" # url form 만들어주기
    url_link = url_set%sub_link  # url 변환
    url_collect = Collect(url_link) # url collect
    html = bs(url_collect,'html.parser')     # parser 가져오기

    removing_special = filter.RemoveHtmlSpecialCh(str(html))
    removing_tag = filter.RemoveTag(removing_special)
    removing_symbol = filter.RemoveSymbol(removing_tag)
    result = cleantext(removing_symbol)
    result_dic[url_link] = result

while True:
    searching_keyword = input("검색 : ")
    keyword_list=[]
    # 변환된 키워드 변환해주기
    if ('ELS' or 'els' or 'DLS' or 'dls' or 'IRP' or 'irp' or 'ISA' or 'isa' or 'CMA' or 'cma' or 'ELW' or 'elw' or
            'PRIME' or 'prime' or 'WM' or 'wm' or 'WRAP' or 'wrap' or 'Choice&Care' or '펀드관리' or 'choicecare' or
            'MoreCare' or 'morecare' or 'PLAZA' or 'plaza' or 'DB' or 'db' or 'DC' or 'dc' or 'best' or 'BEST' or
            'e-book' or 'ebook' or 'EBOOK' or 'Ebook' or 'HTS' or 'hts' or 'Prestige' or 'PRESTIGE' or 'prestige' or
            '프레스티지' or 'Premier' or 'premier' or 'PREMIER' or '프리미얼' or '프리미엄' or '프리미어' or 'ETF' or 'etf' or
            'ETN' or 'etn' or '이티엔' or '이티앤' or 'CFD' or 'cfd') in searching_keyword:
        for index, value in enumerate(searching_keyword):
            if value == 'ELS' or 'els':
                searching_keyword[index] = '이엘스'
            elif value == 'DLS' or 'dls':
                searching_keyword[index] = '디엘스'
            elif value == 'IRP' or 'irp':
                searching_keyword[index] = '아이알피'
            elif value == 'ISA' or 'isa':
                searching_keyword[index] = '아이에세'
            elif value == 'CMA' or 'cma':
                searching_keyword[index] = '크마'
            elif value == 'ELW' or 'elw':
                searching_keyword[index] = '엘렙'
            elif value == 'PRIME' or 'prime':
                searching_keyword[index] = '픠라임'
            elif value == 'WM' or 'wm':
                searching_keyword[index] = '덥엠'
            elif value == 'WRAP' or 'wrap':
                searching_keyword[index] = '덥렙'
            elif value == 'Choice&Care' or 'choicecare' or '펀드관리':
                searching_keyword[index] = '초케'
            elif value == 'MoreCare' or 'morecare':
                searching_keyword[index] = '모케'
            elif value == 'PLAZA' or 'plaza':
                searching_keyword[index] = '쁠라자'
            elif value == 'DB' or 'db':
                searching_keyword[index] = '뎁베'
            elif value == 'DC' or 'dc':
                searching_keyword[index] = '뒤씨'
            elif value == 'BEST' or 'best':
                searching_keyword[index] = '쵀고'
            elif value == 'e-book' or 'ebook' or 'EBOOK' or 'Ebook':
                searching_keyword[index] = '리북'
            elif value == 'HTS' or 'hts':
                searching_keyword[index] = '홈트레이딩서비스'
            elif value == 'Prestige' or 'prestige' or 'PRESTIGE' or '프레스티지':
                searching_keyword[index] = '프레스티지'
            elif value == 'Premier' or 'premier' or 'PREMIER' or '프리미얼' or '프리미엄' or '프리미어':
                searching_keyword[index] = '푸릐미얼'
            elif value == 'ETF' or 'etf':
                searching_keyword[index] = '이퉵'
            elif value == 'ETN' or 'etn' or '이티엔' or '이티앤':
                searching_keyword[index] = '이퉨'
            elif value == 'CFD' or 'cfd':
                searching_keyword[index] = '차익거래'

    if ' ' in searching_keyword:
        keyword_list = searching_keyword.split()
    else:
        keyword_list.append(searching_keyword)

    filtered_link = []  # 필터된 링크 리스트 생성
    ranking_dict = {}   # 랭킹 딕셔너리 생성


    # 키워드가 포함된 링크 뽑아오기
    for searching_keyword in keyword_list:
        for key, value in result_dic.items():
            if searching_keyword in value:
                filtered_link.append(key)

    # 만약 띄어쓰기가 안 되어 있을 때 -> 단어 분리 (지금은 임시방편으로 만듦)
    if len(keyword_list) == 1 and len(filtered_link) == 0:
        expect_word = ''
        expect_word_list = []
        for spell in keyword_list[0]:
            expect_word+=spell
            expect_word_list.append(expect_word)
            for key, value in result_dic.items():
                if expect_word in value:
                    filtered_link.append(key)
        keyword_list = expect_word_list

    filtered_link = list(set(filtered_link))
    # TF-IDF
    # 적중되는 키워드 수만큼 추가 점수
    hit_list = [0 for _ in range(len(filtered_link))]
    for searching_keyword in keyword_list:
        index = 0        # 추가 점수 계산
        for link in filtered_link:  # filter된 링크 하나씩 받아와서
            TF = float(result_dic[link].count(searching_keyword))   # keyword에 따른 TF 계산
            if TF != float(0): #만약 TF가 0이 아니면
                hit_list[index] += 1   # 추가 점수 계산 수 +1
            IDF = abs(float(np.log(len(result_dic)/len(filtered_link)))) # keyword에 따른 IDF 계산
            TF_IDF = TF*IDF #TF-IDF 계산
            if link in ranking_dict.keys(): # 만약 link가 ranking_dict key 안에 들어있으면
                ranking_dict[link] += TF_IDF    # 더해주라
            else:  # 아니면
                ranking_dict[link] = TF_IDF # 채워넣고
            index += 1

    hit_list_indexing=0
#    print(hit_list)
    for link in filtered_link:
        ranking_dict[link] += 100000000*hit_list[hit_list_indexing]
        hit_list_indexing += 1

    # 딕셔너리 중복값 삭제   # 링크는 같지 않아도 내용이 같으면 TF-IDF 값이 같음을 이용
    seen = []
    res_dict = dict()
    for key, value in ranking_dict.items():
        if value not in seen:
            seen.append(value)
            res_dict[key] = value

    #print(res_dict)
    sort_rank_dict = sorted(res_dict.items(), key = lambda x:x[1], reverse=True)  # 내림차순 정렬
    #print(sort_rank_dict)
    for i in sort_rank_dict:
        print(link_title[i[0]]) # 링크 이름 출력하기
        print(i[0])             # 링크 주소 출력하기