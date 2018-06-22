import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
from selenium import webdriver as wd
import time

start_time = time.time()

from dbmgr import DBHelper as Db
db = Db()
main_url = 'http://tour.interpark.com/'
keyword = '로마'


from tour import TourInfo
# 상품 정보를 담는 리스트
tour_list = []

driver = wd.Chrome(executable_path="chromedriver.exe")

driver.get(main_url)
driver.find_element_by_id('SearchGNBText').send_keys(keyword)
driver.find_element_by_css_selector('button.search-btn').click()
# wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'oTravelBox'))
    )
except Exception as e:
    print('', e)

# wait?!
driver.implicitly_wait(5)

driver.find_element_by_css_selector('body > div.container > div > div > div.panelZone > div.oTravelBox > ul > li.moreBtnWrap > button').click()

#div.oTravelBox > ul.boxList > li.moreBtnWrap > button.moreBtn
# searchModule.SetCategoryList(1, '')
import time
for page in range(1, 2): # (1, 16)
    try:
        # 자바스크립트 수행
        driver.execute_script("searchModule.SetCategoryList(%s, '')" % page)
        print(str(page) + ' number')
        time.sleep(10)
        #
        boxItems = driver.find_elements_by_css_selector('body > div.container > div > div > div.panelZone > div.oTravelBox > ul > li')
        print(len(boxItems))
        #
        for li in boxItems:
            # 이미지를 링크값을 사용할것인가?
            # 직접 다운로드해서 우리 서버에 업로드(ftp) 할것인가?
            print('썸네일', li.find_element_by_css_selector('img').get_attribute('src'))
            print('링크', li.find_element_by_css_selector('a').get_attribute('onclick'))
            print('상품명', li.find_element_by_css_selector('h5.proTit').text)
            print('코멘트', li.find_element_by_css_selector('p.proSub').text)
            print('가격', li.find_element_by_css_selector('strong.proPrice').text)
            #print('평점', li.find_elements_by_css_selector('p.proInfo')[2].text)
            infos = li.find_elements_by_css_selector('.info-row .proInfo')
            for info in infos:
                print(info.text)
            print('='*100)

            # 데이터 모음
            # 데이터가 부족하거나 없을수도 있으므로 직접 인덱스로 표현은 위험성이 있음
            obj = TourInfo(
                li.find_element_by_css_selector('h5.proTit').text, \
                li.find_element_by_css_selector('strong.proPrice').text, \
                li.find_elements_by_css_selector('p.proInfo')[1].text, \
                li.find_element_by_css_selector('a').get_attribute('onclick'), \
                li.find_element_by_css_selector('img').get_attribute('src')
            )
            tour_list.append(obj)


    except Exception as e1:
        print('error',e1)

print(len(tour_list))

for tour in tour_list:
    print(type(tour))
    # 링크 데이터에서 실데이터 획득
    # 링크 ,를 기준으로 분리
    arr = tour.link.split(',')

    if arr:
        # 대체
        link = arr[0].replace('searchModule.OnClickDetail(', '')
        # 슬라이싱
        detail_url = link[1:-1]
        # 상세 페이지 이동 : url이 완성된 형태인지 확인, http://~
        driver.get(detail_url)
        time.sleep(3)

        # 현재 selenium의 페이지를 BeautifulSoup의 DOM으로 구성
        soup = bs(driver.page_source, 'html.parser')
        # 현재 상세 정보 페이지에서 스케줄 정보 획득
        data = soup.select('.tip-cover')
        print(type(data), len(data), type(data[0].contents))

        # 디비 입력!! => pymysql
        # 컨텐츠 내용에 따라 전처리 => data[0].contents
        db.db_insertCrawlingData(tour.title, tour.price, tour.area, data[0].contents, keyword)

end_time = time.time()
entire_time = end_time - start_time
print(entire_time)
# 종료


# 창닫기
#driver.close()
#driver.quit()

# 프로세스 종료
#import sys
#sys.exit()

# 수집한 정보 갯수를 루프 => 페이지 방문 => 콘텐츠 획득(상품상세정보) => DB
