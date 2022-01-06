# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 22:12:04 2021

@author: michael
"""

#Install packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from re import sub
from decimal import Decimal
import locale
from bs4 import BeautifulSoup as bs
import datetime 
import concurrent.futures
from time import perf_counter
from lxml import html
import requests
import random
from itertools import cycle
from lxml import etree
import json
from webdriver_manager.chrome import ChromeDriverManager




class getJobURL(object):
    def __init__(self, url, num_page):
        self.url = url
        self.num_page = num_page
        
    def openChromeDriver(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
        self.driver.maximize_window()
        
    def getURL(self):
        self.job_soup = bs(self.driver.page_source, 'lxml')
        urls = []
        i = 0
        for i in range(self.num_page):
            for url in self.job_soup.findAll('article'):
                print('https://www.seek.com.au{}'.format(url.a['href']))
                urls.append('https://www.seek.com.au{}'.format(url.a['href']))
            time.sleep(5)
            nxtBtn = self.driver.find_element_by_class_name('gUkPwHU').click()
            
        self.driver.quit()
        return urls
        
    def closeChromeDriver(self):
        self.driver.quit()

class getJobData(object):
    def __init__(self, url):
        self.url = url
        
    def getData(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
            r = requests.get(self.url, verify = False, headers = headers)
            soup = bs(r.content, 'lxml')
            print(self.url)
            #JOB DESCRIPTION 
            job_desc = []
            for job_data in soup.findAll(attrs={'data-automation': 'jobAdDetails'}):
                job_desc.append(job_data.text)
                print(job_data.text)
                print('-=====')
            job_desc_str = ','.join(job_desc)
            #JOB NAME and Company Name
            company_data = []
            for x in soup.find('div', class_ = 'yvsb870 _1sx92fk0 _1sx92fk6'):
                company_data.append(x.text)
            #Job Name
            job_name = company_data[0]
            print('JOB NAME: ', job_name)
            #Company Name
            try:
                Company_name = company_data[1]
                print('COMPANY NAME: ',  Company_name)
            except:
                Company_name = None
            
            #Job Location
            try:
                job_loc = soup.find('div', class_ = 'yvsb870 _14uh99496').text
            except:
                job_loc = None
            
            #Job Classification
            try:
                tree = etree.HTML(str(soup))
                classification = tree.xpath('//*[@id="app"]/div/div/div[3]/div/div/div/div/div[1]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[3]/div/div[2]/span/div/div[1]/text()')
                job_classification = classification[0]
                type_job = tree.xpath('//*[@id="app"]/div/div/div[3]/div/div/div/div/div[1]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[3]/div/span/div/div/text()')
            except:
                job_classification = None
                type_job = None
                
            #CONTACT EMAIL
            try:
                email = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', job_desc_str)[0]
                print('EMAIL: ', email)
            except:
                email = None
            
            result = [self.url, Company_name, job_loc, job_classification, job_name, job_desc_str, email]
            
            return result
        except:
            pass

def getData(url):
    try:
        data = getJobData(url)
        job_data = getJobData.getData(data)
        return job_data
    except Exception as e:
        print(e)
        pass
    


############################## PROCESS PART #################################



BASE_URL = 'https://www.seek.com.au/jobs?daterange=7'
NUM_PAGE = 50
data = getJobURL(BASE_URL, NUM_PAGE)
try:
    openChrome = getJobURL.openChromeDriver(data)
    urls = getJobURL.getURL(data)
except Exception as e:
    closeDriver =  getJobURL.closeChromeDriver(data)       

    


MAX_WORKER = 5

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
    f = [executor.submit(getData, i)  for i in urls]
    print(f)
    DATA = []
    for future in concurrent.futures.as_completed(f):
        DATA.append(future.result())
        print(future.result())

try:
    df_data = pd.DataFrame(DATA, columns = ['jobsite_url', 'Company_name', 'job_loc', 'job_classification', 'job_name', 'job_desc', 'email'])
    print(df_data)
    df_data.dropna(subset = ['email'], inplace = True)

    df_data = df_data.reset_index()
    df_data = df_data.drop(columns = ['index'])

    #IMPORT INTO JSON
    df_data.to_json('SEEKAU.json' , orient="records")
    df_data.to_excel('SEEKAU.xlsx', index = False)
    print('JOB DONE PLEASE CHECK THE OUTPUT FILE')
except Exception as e:
    print('THERE ARE NO EMAIL THAT ATTACHED ON THE JOB POST!!')
    print(e)


