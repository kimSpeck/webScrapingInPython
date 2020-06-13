#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import libraries 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import base64
import imageio
import glob
import os.path

# create instance of Firefox webdriver
driver = webdriver.Firefox()
#driver.maximize_window()

# navigate to page
driver.get("http://www.skymaponline.net/skymap.aspx")
time.sleep(3)

# find element of page to set location for star map
link2location = driver.find_element_by_link_text('Location')
link2location.click()
time.sleep(1)

# location can be selected by option in drop down menu; select Berlin as location
location = driver.find_element_by_xpath("//select[@name='DropDownListLocation']/option[text()='Berlin, Germany']")
location.click()
# update map after selecting location
driver.find_element_by_name('ButtonUpdateMap').click() 
time.sleep(1)

# access time selection menu
driver.find_element_by_link_text('Time').click()
time.sleep(1)

# text input hour and minutes; set time to 00:00 am 
inputHour = driver.find_element_by_id('TextBoxHour')
inputHour.clear()
inputHour.send_keys('00')
inputMinutes = driver.find_element_by_id('TextBoxMinute')
inputMinutes.clear()
inputMinutes.send_keys('00')
time.sleep(1)

# text input of year 
inputYear = driver.find_element_by_id('TextBoxYear')
inputYear.clear()
inputYear.send_keys('2020')

# list all available months to select in drop down menu 
monthsMenu = driver.find_element_by_name("DropDownListMonth")
months = [iMon for iMon in monthsMenu.find_elements_by_tag_name("option")]

monthList = [];
for iMonth in months:
    monthList.append(iMonth.get_attribute("value"))
time.sleep(1)

# generate new folder for star map png-files (if not already exist)
newFolder = r'starMapFiles' 
if not os.path.exists(newFolder):
    os.makedirs(newFolder)

# get more pictures for gif by downloading star map for 5 days per month 
dayList = range(1,26,6)

# iterate through all months in chosen year
for iMonth in monthList:
    # select month in drop down menu
    oneMonth = driver.find_element_by_xpath("//select[@name='DropDownListMonth']/option[@value = '%s']" % iMonth)    
    oneMonth.click()
    time.sleep(2)
    
    # iterate through all 5 days
    for iDay in dayList:
        
        # text input for day 
        inputDay = driver.find_element_by_id('TextBoxDay')
        inputDay.clear()
        inputDay.send_keys(str(iDay))
        
        # update map to selected month and day 
        driver.find_element_by_name('ButtonGoTimezone').click()
        time.sleep(3)
        
        # find slider to control size of map         
        slidebar = driver.find_element_by_xpath("//div[@id='slider']")
        locationSB = slidebar.location
        sizeSB = slidebar.size
        #xOffset = locationSB['x'] + (sizeSB['width']/2)
        #yOffset = locationSB['y'] + sizeSB['height'] - 4
        time.sleep(2)
        
        # start action chain 
        move = ActionChains(driver)  
        # move slider to shrink map as far as possible 
        move.move_to_element(slidebar).move_by_offset(0, sizeSB['height']/2 - 4).click().perform()
        time.sleep(2)
        
        # find button for moving map in canvas element
        navigationButton = driver.find_element_by_id('navigation')
        locationNB = navigationButton.location
        sizeNB = navigationButton.size
        #xOffsetLeft = locationNB['x'] + (sizeNB['width']/4)
        #yOffsetLeft = locationNB['y'] + (sizeNB['height']/2)
        #xOffsetTop = locationNB['x'] + (sizeNB['width']/2)
        #yOffsetTop = locationNB['y'] + (sizeNB['height']/4)
        time.sleep(2)    
        
        # move map to cut as little as possible from map 
        move.move_to_element(navigationButton).move_by_offset(-sizeNB['width']/4, 0).click().perform()
        time.sleep(4)
        
        move.move_to_element(navigationButton).move_by_offset(0, -sizeNB['height']/4).click().perform()
        time.sleep(4)
        
        move.move_to_element(navigationButton).move_by_offset(0, sizeNB['height']/4).click().perform()
        time.sleep(4)
        
        # find map (canvas element)
        canvas = driver.find_element_by_id("map")

        # get the canvas as a PNG base64 string
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)               
        
        # decode
        canvas_png = base64.b64decode(canvas_base64)   
    
        # save map to png file
        with open(r''+newFolder+"/canvas"+str(iDay)+iMonth+".png", 'wb') as f:
            f.write(canvas_png)

# close browser window
driver.close()

# list all filenames in correct order (1st Jan to 25 Dec)
fileNames = []
fileNames += glob.glob(newFolder+"/*.png")
fileNames.sort(key=os.path.getmtime)

# create gif 
with imageio.get_writer('starMap.gif', mode='I') as writer:
    for iFile in fileNames:
        image = imageio.imread(iFile)
        writer.append_data(image)