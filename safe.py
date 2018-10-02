# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import turicreate as tc
import datetime, time, re, os, pickle
import make_data_xls_send_email

def getImageClassification(imagePath, turiModel):
    image = tc.image_analysis.load_images(imagePath)
    prediction = turiModel.predict(image)
    return prediction[0]


def isOption(optionsForCrawler):
    loadOptions = Options()
    for i, option in enumerate(optionsForCrawler):
        loadOptions.add_argument(option)
    return loadOptions


def loginInstagram(crawler, instagramAddress, instagramUsername, instagramPassword):
    #Instagram 로그인
    print('### ----- Logging in Instagram... ----- ###')
    crawler.get(instagramAddress+'/accounts/login/')
    crawler.implicitly_wait(3)
    crawler.find_element_by_name("username").send_keys(instagramUsername)
    crawler.find_element_by_name("password").send_keys(instagramPassword)
    crawler.find_element_by_name("password").send_keys(u'\ue007')


def connectInstagramTargetPage(crawler, instagramAddress, hashtag): #Instagram 해시태그로 들어가기
    print('### ----- Getting to the site... ----- ###')
    crawler.get(instagramAddress+'/explore/tags/'+hashtag) # Instagram #hashtag 주소로 들어가기
    crawler.implicitly_wait(3)
    # 자살 관련 게시물 '게시물 보기' 버튼 클릭
    try:
        print('### ----- 게시물 보기 클릭 시도... ----- ###')
        crawler.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div/ul/li[1]/button').click()
    except:
        pass


def getInstagramTargetTotalcount(crawler): # 총 게시물 수를 클래스 이름으로 찾기
    totalcount = crawler.find_element_by_class_name('g47SY').text
    totalcount = ''.join(totalcount.split(','))
    print("### ----- 총 게시물: {} ----- ###".format(totalcount))
    return int(totalcount)


def getInstagramTargetDataInDict(crawler, scrollWaitingTime, scrollNumber):
    element = crawler.find_element_by_tag_name("body") # body 태그를 태그 이름으로 찾기
    targetDataDict = {} # 전체 값을 담을 빈 dictionary 선언
    pagedowns = 0 # 페이지 스크롤을 위해 임시 변수 선언
    startTime = datetime.datetime.now()

    while pagedowns < scrollNumber: # 스크롤을 진행한다.
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(scrollWaitingTime) # 페이지 스크롤 타이밍을 맞추기 위해 sleep
            try:
                posts = crawler.find_elements_by_css_selector('div.v1Nh3.kIKUG._bz0w') # 브라우저에 보이는 모든 img 태그를 css 선택자 문법으로 찾는다.

                for post in posts:
                    postLink = post.find_element_by_tag_name('a').get_attribute('href') # Post 주소 가져오기
                    key = postLink.split('/')[-2] #Post의 Key 생성
                    imageLink = (post.find_element_by_css_selector('img.FFVAD').get_attribute('srcset').split('240w,')[1]).split(' 320w,')[0] # Thumbnail Image link 가져오기 (Total: imageLink ==> 320x320만 골라서 저장)
                    targetDataDict[key] = [postLink, imageLink] # targetDataDict = {'고유번호':['글주소','이미지주소']} 형태로 저장 (중복 방지 위해)
            except:
                pass

            pagedowns += 1
            print('### ----- Scrolling {}/{} done - # of Posts: {} (Lap time: {}) ----- ###'.format(pagedowns, scrollNumber,len(targetDataDict),datetime.datetime.now()-startTime))
            try:
                if pagedowns % (scrollNumber // 10) == 0:
                    print('### ----- Scrolling {}/{} done - # of Posts: {} (Lap time: {}) ----- ###'.format(pagedowns,scrollNumber,len(targetDataDict),datetime.datetime.now()-startTime))
            except:
                pass
    lapTime = datetime.datetime.now()-startTime

    return targetDataDict, lapTime # targetDataDict = {'고유번호':['글주소','이미지주소']}


def getUpdatedDataInDict(databasePath, targetDataDict): # database에 있는 자료는 삭제, 없는 자료만 남김 (updated data만 남음)
    with open(databasePath, 'rb') as databaseFile:
        database = pickle.load(databaseFile)

    delKeys = [] #지울 key 모을 list
    #지울 key 목록 확보
    for key in targetDataDict:
        if key in database:
            delKeys.append(key)
        else:
            pass
    #확보한 key 삭제
    for key in delKeys:
        del targetDataDict[key]

    return targetDataDict #UpdatedData 리턴


def updateDatabase(databasePath, updatedData):
    with open(databasePath, 'rb') as databaseFile:
        database = pickle.load(databaseFile)

    database.update(updatedData) #database update

    with open(databasePath, 'wb') as databaseFile:
        pickle.dump(database,databaseFile)


def gatherData(crawler, dataListDict, imageClassifier, turiModel, selfharmLabel, outputFilename):
    nowPostpix = re.sub('[-:. ]', '', datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
    outputFilenameNow = outputFilename + nowPostpix + '.txt'
    print('### ----- Data_gathering start... ----- ###')
    i = 0 #Count 용 임시 변수 선언
    selfharmDataListDict = {} #반환용 dict 변수 선언
    startTime = datetime.datetime.now()

    with open(outputFilenameNow,'wt',encoding='utf-8', newline='') as outputFile: # Post 주소를 txt 파일에 저장
        for Key in dataListDict:
            try:
                if imageClassifier(dataListDict[Key][1], turiModel) == selfharmLabel:  # 자해(selfharm)일 경우에만 데이터 모으기
                    print('### ----- {} contains selfharm content ----- ###'.format(Key))
                    crawler.get(dataListDict[Key][0]) #글주소로 들어가기
                    idAddress = crawler.find_element_by_css_selector('a.FPmhX.notranslate.nJAzx').get_attribute('href')
                    dateTime = crawler.find_element_by_css_selector('time._1o9PC.Nzb55').get_attribute('datetime')[:10]

                    try: # 동영상인지 이미지인지 구분하기
                        playButton = crawler.find_element_by_css_selector('a.QvAa1')
                        imageOrVideo = 'video'
                    except NoSuchElementException:
                        imageOrVideo = 'image'

                    if idAddress in selfharmDataListDict and selfharmDataListDict[idAddress][1]!=imageOrVideo:
                        imageOrVideo = 'video+image'
                        selfharmDataListDict[idAddress] = [dateTime, imageOrVideo, dataListDict[Key][0]]
                    else:
                        selfharmDataListDict[idAddress] = [dateTime, imageOrVideo, dataListDict[Key][0]]

                    outputFile.write(dataListDict[Key][0]+'\n') #파일에 자해 게시물 주소만 기록하기
            except:
                pass #그림파일 삭제된 것은 list 기록 안함

            i += 1
            try:
                if i % (dataListDict // 10) == 0: # 전체 시도의 10%마다 메시지 출력하기
                    print('### ----- Data gathering {}/{} done  (Lap time: {}) ----- ###'.format(i,len(dataListDict),datetime.datetime.now()-startTime))
            except:
                pass

    lapTime = datetime.datetime.now() - startTime

    return selfharmDataListDict, outputFilenameNow, lapTime # selfharmDataListDict = {'idAddress':['datetime', 'imageOrVideo', 'postAddress']}


def reportPost(crawler, dataList):
    with open(dataList, 'rt', encoding='utf-8') as postAddressList:
        while True:
            postAddress = postAddressList.readline()
            if not postAddress: break
            crawler.get(postAddress)
            # 신고하기
            crawler.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div/article/div[3]/button').click()  # [더보기] 클릭
            crawler.find_element_by_xpath('/html/body/div[3]/div/div/div/div/button[1]').click()  # [부적절한 콘텐츠 신고] 클릭
            crawler.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/ul/li[5]/button').click()  # [기타] 클릭
            crawler.find_element_by_xpath(
                '/html/body/div[3]/div/div/div[2]/div/ul/li[5]/button').click()  # [스스로 신체적 상해를 입히는 행위] 클릭
            crawler.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/ul/li/div/span/button').click()  # [제출] 클릭
            crawler.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div[2]/button').click()  # [닫기] 클릭
            print(postAddress," 신고완료하였습니다")


if __name__=='__main__':
    ### ----- 변수 정의 ----- ###
    CRAWLER_OPTIONS = ['-headless'] #CRAWLER 옵션 list 형태로 구성(추가, 삭제 가능)

    INSTAGRAM_USERNAME = '' #Instagram ID
    INSTAGRAM_PASSWORD = '' #Instagram Password
    INSTAGRAM_ADDRESS = 'https://www.instagram.com'
    HASHTAGS = ['%EC%9E%90%ED%95%B4', '%EC%9E%90%EC%82%B4']

    SCROLL_WAITING_TIME = 1  # Scroll 할 때 기다릴 시간(초)

    OUTPUT_FILENAME_PREFIX = './output_list/updated_lists'
    DATABASE_PATH = './.database/database.pickle' #현재까지 수집한 [게시물 기준] 전체 데이터베이스 (누적)
    DATABASE_SELFHARM_ACCOUNT_PATH = './.database/database_selfharm_account.pickle' #현재까지 수집한 ['계정' 기준] 전체 자해게시물 데이터베이스 (누적)
    TURI_SELFHARM_CLASSIFIER_PATH = 'classifier_safe-selfharm-dataset.model' #TURI로 학습한 자해 판별 신경망 모델 주소
    SELFHARM_LABEL = 'selfharm' #label
    YOUR_NAME = '홍길동' # 본인 이름(파일명, 이메일 내용 등에 포함)
    GMAIL_ID = '# your-gmail-ID@gmail.com' # Gmail ID
    GMAIL_PASSWORD = '# your-gmail-password >>>' # Gmail Password
    EMAIL_NAME = '홍길동' # 보낸사람에 표시될 이름
    EMAIL_TO = [''] # 참고: 중앙자살예방센터 미디어정보팀 'spcmedia@spckorea.or.kr'
    EMAIL_BCC = [''] # 숨은참조
    EMAIL_CONTENT = '안녕하세요.\n\n'+'검색한 자료 보내드립니다.\n\n\n'+YOUR_NAME+' 드림'


    ### ----- 구동부(1): 웹크롤러 준비하여 리스팅 한 hashtag에 대해 접근하여 게시물 주소 확보 ----- ###
    startTime = datetime.datetime.now()
    print('### ----- SAFE started at {} ----- ###'.format(startTime))
    crawlerOptions = isOption(CRAWLER_OPTIONS) # 브라우저 옵션 준비
    crawler = webdriver.Firefox(firefox_options=crawlerOptions) # Firefox 브라우저 준비
    selfharmClassifierTuriModel = tc.load_model(TURI_SELFHARM_CLASSIFIER_PATH) #자해 판별 신경망 준비 (turicreate로 학습된 신경망 loading)
    imageClassifier = getImageClassification # image classifier 준비

    #loginInstagram(crawler, INSTAGRAM_ADDRESS, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD) # 인스타그램 로그인
    updatedData = {} #updated Data 모을 빈 dict 선언
    lapTimeCrawling = [] #lap time 기록용 빈 list 선언
    for i, hashtag in enumerate(HASHTAGS):
        print('### ----- Start searching HASHTAG #{}/{} : {} ----- ###'.format(i+1, len(HASHTAGS),hashtag))
        connectInstagramTargetPage(crawler, INSTAGRAM_ADDRESS, hashtag) # 해당 hashtag 주소로 접근
        totalCount = getInstagramTargetTotalcount(crawler) # 게시물 수(n) 확보
        scrollNumber = totalCount // 50 # Scroll 할 횟수(n) 정하기: 전체 스크롤 하려면 '// 5' 정도로 설정. 스크롤 1회 당 평균 5개 게시물 수집됨.
        targetData, lapTime = getInstagramTargetDataInDict(crawler, SCROLL_WAITING_TIME, scrollNumber) # 해당 hashtag 게시물/이미지 주소 데이터 수집(dict 형태)
        lapTimeCrawling.append(lapTime)
        updatedData.update(getUpdatedDataInDict(DATABASE_PATH, targetData)) # 기존 database에 없는 updated된 자료만 추가(hashtag 별로 반복됨)
    updateDatabase(DATABASE_PATH, updatedData) # 모든 hashtag에 대해 모은 updated Data로 기존 database update 시킴

    ### ----- 구동부(2): 신경망으로 자해 이미지/동영상 포함한 것만 골라내어 리스팅 ----- ###
    selfharmDataListDict, updatedDataFilename, lapTimeDataGathering = gatherData(crawler, updatedData, imageClassifier, selfharmClassifierTuriModel, SELFHARM_LABEL, OUTPUT_FILENAME_PREFIX) #해당 주소 데이터에 있는 image 다운로드 및 해당 게시물 주소 기록
    updateDatabase(DATABASE_SELFHARM_ACCOUNT_PATH, selfharmDataListDict) # selfharm account Database update 시킴

    ### ----- 구동부(3): 추가된 데이터 있을 경우에만 엑셀 파일(.xlsx) 형태로 작성된 자살유해정보를 이메일로 송부 ----- ###
    if len(selfharmDataListDict)>0:
        xlsxFilename = make_data_xls_send_email.getXls(selfharmDataListDict, YOUR_NAME) # XLSX 파일로 자료 기록하기
        print('### ----- Data is saved in {} ----- ###'.format(xlsxFilename))
        monthDate = datetime.datetime.today().strftime('%m%d') # 메일제목용 날짜
        emailSubject = monthDate+' '+YOUR_NAME+' 자살유해정보 신고('+str(len(selfharmDataListDict))+'건)입니다' # 메일 제목: "1120(해당일) 홍길동 자살유해정보 신고(00건)입니다"
        make_data_xls_send_email.sendEmail(GMAIL_ID, GMAIL_PASSWORD, EMAIL_NAME, EMAIL_TO, EMAIL_BCC, emailSubject, EMAIL_CONTENT, xlsxFilename) # 이메일 보내기
        print('### ----- Sending email is complete ----- ###'.format(xlsxFilename))

    runtimeTotal = datetime.datetime.now()-startTime
    print("##### ----- SAFE task is accomplished ----- #####")
    for i, lapTime in enumerate(lapTimeCrawling):
        print('Time for Crawling (#{}/{}): {}'.format(i+1,len(lapTimeCrawling),lapTime))
    print('Time for Data Gathering: {}'.format(lapTimeDataGathering))
    print('Total Runtime: {}'.format(runtimeTotal))