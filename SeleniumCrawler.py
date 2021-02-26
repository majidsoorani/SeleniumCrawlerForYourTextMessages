#!/usr/bin/env python
# coding: utf-8

import csv
import pickle
import time
import smtplib
import pandas as pd
from parsel import Selector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from numpy import asarray
from numpy import savetxt
from urllib.request import urlopen
import re
import webbrowser
# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=chrome-data ")
chrome_options.add_argument("--auto-open-devtools-for-tabs")
driver = webdriver.Chrome('D://chromedriver//chromedriver',options=chrome_options)
driver.get('https://messages.google.com/web/conversations/8')  # Already authenticated
time.sleep(20)
messgaes = driver.find_elements_by_tag_name('mws-message-part-content')
dic = {};
datemax = "1399/11/14";
varizNaghdi = 0
lastTransDesc = 0
##Mellat Transaction
for msg in messgaes:
    str_text = msg.text.replace(",", "", 20)
    if "رمز" in str_text:
        lastTransDesc =  str_text.splitlines()[0]  + " " +str_text.splitlines()[1] 
    if ("واريز به حساب" in str_text) |  ("برداشت از حساب" in str_text): 
        regexTransAccount = r"(حساب)(\D*)(\d+)"
        accountNo = re.search(regexTransAccount, str_text, re.IGNORECASE).groups()[2]
        transType = ""
        if "واريز به حساب" in str_text:
            transType ="واريز به حساب";
        if "برداشت از حساب" in str_text:
            transType ="برداشت از حساب";
        if "خريد با کارت" in str_text:
            transType ="خريد با کارت";
        if "حواله پايا" in str_text:
            transType ="حواله پایا";
        regexTransAmount = r"(مبلغ)(\D*)(\d+)"
        transAmount = re.search(regexTransAmount, str_text, re.IGNORECASE).groups()[2]
        if "برداشت از حساب" in str_text: 
            transAmount = "-"+transAmount;
        regexMostanadNumber = r"(مستند)(\D*)(\d+)"
        matches =  re.search(regexMostanadNumber, str_text, re.IGNORECASE).groups()
        if matches:
             mostanadNumber =matches[2]
        if "چک" in str_text:
            regexMostanadNumber = r"(سري و سريال چک)(\D*)(\d+)"
            lastTransDesc += str(re.search(r"(سري و سريال چک)(\D*)(\d+)( )(\d+)", str_text, re.IGNORECASE).groups())
            mostanadNumber =  re.search(r"(سري و سريال چک)(\D*)(\d+)( )(\d+)", str_text, re.IGNORECASE).groups()[2]
        date = re.search("\d{4}\/\d{2}\/\d{2}", str_text, re.IGNORECASE)[0]
        if(date>datemax):
                datemax =date;
        print("datemax"+datemax)
        prtime = re.search("\d{2}\:\d{1,}", str_text, re.IGNORECASE)[0]
        dic[date+ "--" +mostanadNumber+"--"+transAmount+"--mellat"] = ("&lastTransDesc="+lastTransDesc if (lastTransDesc!=0) else "")+ "&transDesc="+transType+ "&accountNo="+accountNo+"&mostanad=" +mostanadNumber+"&date="+date+"&time="+prtime+"&transAmount="+transAmount;
        lastTransDesc = ""
        regexBalance = r"(موجودي)(\D*)(\d+)"
        matches = re.search(regexBalance, msg.text.replace(",", "", 20), re.IGNORECASE)  
        if matches:
            dic[date+ "--" +"Balance--Mellat--" +accountNo] = matches.groups()[2]
driver.get("https://messages.google.com/web/conversations/7")
time.sleep(20)
##Passargad Balances
messgaes = driver.find_elements_by_tag_name('mws-message-part-content')
for msg in messgaes:
    str_text = msg.text.replace(",", "", 20)

    if "رمز" in str_text:
        if "اشتباه" not in  str_text:
            lastTransDesc = str_text.splitlines()[1]   + " " + str_text.splitlines()[2] ;
    if ("رمز" in str_text) | ("ورود" in str_text) :
        continue;
    if "ديباجي جنوبي" in str_text:
        lastTransDesc += 'حقوق'
    matches =re.search("\d{2}\/\d{2}\/\d{2}", str_text, re.IGNORECASE)
    if matches:
        date = "13"+matches[0]    
    else :
        continue;
    prtime = re.search("\d{1,}\:\d{2}", str_text, re.IGNORECASE)[0]
    regexTransAmount = r"(مبلغ)(\D*)(\d+)"
    transAmount = re.search(regexTransAmount, str_text, re.IGNORECASE).groups()[2]
    if ("برداشت از" in str_text) | ("برداشت چک" in str_text): 
        transAmount = "-"+transAmount;
    regexTransAcount = r"(واريز به)(\D*)(\d+.{1,})"
    matches =  re.search(regexTransAcount, str_text, re.IGNORECASE) 
    if matches:
        transType = "واريز به حساب"
        accountNo =matches.groups()[2]
    regexTransAcount = r"(برداشت از)(\D*)(\d+.{1,})"
    matches =  re.search(regexTransAcount, str_text, re.IGNORECASE) 
    if matches:
        transType = "برداشت از حساب"
        accountNo =matches.groups()[2]
    dic[date+ "--" +mostanadNumber+"--"+transAmount+"--passargad"] = ("&lastTransDesc=پاسارگاد "+lastTransDesc if (lastTransDesc!=0) else "")+ "&transDesc="+transType+ "&accountNo="+accountNo+"&mostanad=" +accountNo+"&date="+date+"&time="+prtime+"&transAmount="+transAmount;
    lastTransDesc = ""
    regexBalance = r"(موجودي)(\D*)(\d+)"
    matches =  re.search(regexBalance, str_text, re.IGNORECASE)
    if matches: 
        if accountNo:
            dic[date+ "--" +"Balance--Passargad--" +accountNo] = matches.groups()[2]

driver.get("https://messages.google.com/web/conversations/2053")
time.sleep(20)
## Mehr
messgaes = driver.find_elements_by_tag_name('mws-message-part-content')
for msg in messgaes:
    str_text = msg.text.replace(",", "", 20)
    if "رمز" in str_text:
        if "اشتباه" not in  str_text:
            lastTransDesc = str_text.splitlines()[0]   + " " + str_text.splitlines()[4] ;
    if ("مبلغ" in str_text)  & ("مانده" in str_text  ):
        mostanadNumber =""
        regexTransAccount = r"(حساب)(\D*)(\d+)"
        accountNo = re.search(regexTransAccount, str_text, re.IGNORECASE).groups()[2]
        regexTransAmount = r"(مبلغ)(\D*)(\d+)(\D*)"
        transAmount = re.search(regexTransAmount, str_text , re.IGNORECASE).groups()[2]
        if "-" in re.search(regexTransAmount, str_text , re.IGNORECASE).groups()[3]:
            transAmount = "-"+transAmount;
        regexMostanadNumber = r"(EMPTY)(\D*)(\d+)"
        matches = re.search(regexMostanadNumber, str_text , re.IGNORECASE)
        if matches:
          mostanadNumber = matches.groups()[2]
        regexMostanadNumber = r"(رهگيري)(\D*)(\d+)"        
        matches = re.search(regexMostanadNumber, str_text , re.IGNORECASE)
        if matches :
          mostanadNumber = matches.groups()[2]
        matches = re.search(regexMostanadNumber, str_text, re.IGNORECASE) 
        if matches :
          mostanadNumber = matches.groups()[2]
        regexMostanadNumber = r"(رهـ)(\D*)(\d+)"
        matches = re.search(regexMostanadNumber, str_text, re.IGNORECASE) 
        if matches :
          mostanadNumber = matches.groups()[2]
        date = re.search("\d{4}\/\d{1,}\/\d{1,}", str_text, re.IGNORECASE)[0]
        date = date.split("/")[0] +"/"+ date.split("/")[1].zfill(2) +"/"+ date.split("/")[2].zfill(2)
        ##dic[datemax+"accountNo"] 
        if(date>datemax):
                datemax =date;
        print("datemax"+datemax)
        prtime = re.search("\d{1,2}\:\d{2}", str_text, re.IGNORECASE)[0]
        dic[date+ "--" +mostanadNumber+"--"+transAmount+"--Mehr"] = ("&lastTransDesc=مهر "+lastTransDesc if (lastTransDesc!=0) else "")+"&mostanad=" +mostanadNumber+"&date="+date+"&time="+prtime+"&transAmount="+transAmount;    
        regexBalance = r"(مانده)(\D*)(\d+)"
        matches = re.search(regexBalance, msg.text.replace(",", "", 20), re.IGNORECASE)  
        if matches:
            dic[date+ "--" +"Balance--Mehr--" +accountNo] = matches.groups()[2]
driver.get("https://messages.google.com/web/conversations/2064")
time.sleep(20)
## Melli
messgaes = driver.find_elements_by_tag_name('mws-message-part-content')
for msg in messgaes:
    str_text = msg.text.replace(",", "", 20)
    if "نقدي" in msg.text:
            varizNaghdi = "1"
            regexTransAmount = r"(نقدي)(\D*)(\d+)"
            transAmount = re.search(regexTransAmount, str_text, re.IGNORECASE).groups()[2]
            date = re.search("\d{4}\-\d{2}\:\d{2}", str_text, re.IGNORECASE)[0].split("-")[0]
            date = "1399/"+ date[0:2] +"/"+date[2:4] 
            prtime =re.search("\d{4}\-\d{2}\:\d{2}", str_text, re.IGNORECASE)[0].split("-")[1]
    regexBalance = r"(مانده)(\D*)(\d+)"
    matches = re.search(regexBalance, str_text, re.IGNORECASE)  
    if matches:
        dic[date+ "--" +"Balance--Melli--" +accountNo] = matches.groups()[2]
balancePassargad = 0;
balanceMellat = 0;
balanceMelli = 0;
balanceMehr = 0;
for key in dic.keys():
    print("key in deic ->"+key)
    if(key.split("--")[0] == datemax):
        if key.split("--")[1] == "Balance":
            if key.split("--")[2]== "Passargad":
                balancePassargad += int(dic[key])
            elif key.split("--")[2]== "Mellat":
                balanceMellat    += int(dic[key])
            elif key.split("--")[2]== "Melli":
                balanceMelli    += int(dic[key])
            elif key.split("--")[2]== "Mehr":
                balanceMehr    += int(dic[key])
        else:
            webbrowser.get(chrome_path).open('https://script.google.com/macros/s/AKfycbxGCnsgAcqnGrfYXA8wOsiQz3_zGRBKQppwgi7h-GKhjy2fiV3_uyW6/exec?varizMellat=1'+dic[key])
            time.sleep(10);
webbrowser.get(chrome_path).open('https://script.google.com/macros/s/AKfycbxGCnsgAcqnGrfYXA8wOsiQz3_zGRBKQppwgi7h-GKhjy2fiV3_uyW6/exec?'+("&varizNaghdi="+varizNaghdi if (varizNaghdi!=0) else "")+('&mostanad='+mostanadNumber+"&date="+date+"&time="+prtime+"&transAmount="+transAmount if (mostanadNumber!=0) else "")+("&balanceMelli="+str(balanceMelli) if (balanceMelli!=0) else "")+("&balanceMellat="+str(balanceMellat) if (balanceMellat!=0) else "")+("&balancePassargad="+str(balancePassargad) if (balancePassargad!=0) else "")+("&balanceMehr="+str(balanceMehr) if (balanceMehr!=0) else ""))
#driver.get("https://ib.qmb.ir/webbank/login/loginPage.action?ibReq=WEB")
#inputs = driver.find_elements_by_tag_name('input')
#for input in inputs:
   
driver.quit()
