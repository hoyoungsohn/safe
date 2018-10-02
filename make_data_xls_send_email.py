# -*- coding: utf-8 -*-
import datetime, openpyxl, smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def getXls(dataListDict, yourName):
    monthDate = datetime.datetime.today().strftime('%m%d')
    yearMonthDate = datetime.datetime.today().strftime('%Y-%m-%d')
    filename = './output_xlsx/'+monthDate+'_'+yourName+'_자살유해정보_신고('+str(len(dataListDict))+'건).xlsx' # 엑셀 파일명: "1120(해당일)_홍길동(성함)_자살유해정보_신고(00건)"
    workbook = openpyxl.load_workbook('./output_xlsx/template.xlsx') # 엑셀파일 열기
    worksheet = workbook.active # 현재 Active Sheet 얻기
    # worksheet = workbook.get_sheet_by_name("Sheet1")

    for i, key in enumerate(dataListDict):
        number = i+1 # 개수 세기용. 1부터 시작함.
        row_index = i + 3  # Row는 3열부터 시작함

        worksheet.cell(row=row_index, column=1).value = number
        worksheet.cell(row=row_index, column=3).value = yourName
        worksheet.cell(row=row_index, column=5).value = yearMonthDate
        worksheet.cell(row=row_index, column=6).value = dataListDict[key][0]
        worksheet.cell(row=row_index, column=7).value = key
        worksheet.cell(row=row_index, column=9).value = '인스타그램'
        if dataListDict[key][1] == 'image': # 텍스트 1, 이미지 2, 동영상 3. 혼합형일 경우 높은 숫자로 기록.
            worksheet.cell(row=row_index, column=11).value = 2
        elif dataListDict[key][1] == 'video':
            worksheet.cell(row=row_index, column=11).value = 3
        elif dataListDict[key][1] == 'video+image':
            worksheet.cell(row=row_index, column=11).value = 3
        worksheet.cell(row=row_index, column=17).value = '자살실행 사진/동영상'
        worksheet.cell(row=row_index, column=18).value = 0
        worksheet.cell(row=row_index, column=19).value = 0
        worksheet.cell(row=row_index, column=20).value = 0
        worksheet.cell(row=row_index, column=21).value = 1
        worksheet.cell(row=row_index, column=22).value = 0
        worksheet.cell(row=row_index, column=23).value = 0
        worksheet.cell(row=row_index, column=24).value = 0
        worksheet.cell(row=row_index, column=25).value = 0
        if dataListDict[key][1] == 'image' or dataListDict[key][1] == 'video+image':
            worksheet.cell(row=row_index, column=26).value = 1
        else:
            worksheet.cell(row=row_index, column=26).value = 0
        if dataListDict[key][1] == 'video' or dataListDict[key][1] == 'video+image':
            worksheet.cell(row=row_index, column=27).value = 1
        else:
            worksheet.cell(row=row_index, column=27).value = 0
        worksheet.cell(row=row_index, column=29).value = 0
        worksheet.cell(row=row_index, column=30).value = 0
        worksheet.cell(row=row_index, column=31).value = 0
        worksheet.cell(row=row_index, column=32).value = 0
        worksheet.cell(row=row_index, column=33).value = 0
        worksheet.cell(row=row_index, column=34).value = 0
        worksheet.cell(row=row_index, column=35).value = 0
        worksheet.cell(row=row_index, column=36).value = 0
        worksheet.cell(row=row_index, column=37).value = 0
        worksheet.cell(row=row_index, column=38).value = 1

    workbook.save(filename) # 엑셀 파일 저장
    workbook.close()
    return filename


def sendEmail(id, pwd, name, to, bcc, subject, content, attachedFilename):
   msg = MIMEMultipart()
   msg['From'] = name
   msg['To'] = ", ".join(to)
   msg['Subject'] = subject
   msg.attach(MIMEText(content))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attachedFilename, 'rb').read())
   encoders.encode_base64(part)
   part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachedFilename))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(id, pwd)
   mailServer.sendmail(id, to+bcc, msg.as_string())

   mailServer.close()
