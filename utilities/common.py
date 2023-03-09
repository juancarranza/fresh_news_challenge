from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from datetime import datetime as dt

from datetime import date
from dateutil.relativedelta import relativedelta

import logging
import os
import time
import shutil
import re

# Define a open_the_website(url) that opens the browser with an specific URL
def open_the_website(url: str, browser:Selenium):
    """ Here we open the main website and 
     we maximize the browser window, also we specify the browser to use.

    Keyword arguments:
    url -- The url that is going to be opened.
    browser -- In order to use the same browser variable so this can continue
    """

    logging.info("*********[common.py][open_the_website] - Method has started.***********")
    # This opens the main browser.
    browser.open_available_browser(url, alias="main_browser")
    browser.maximize_browser_window()
    logging.info("***********[Tasks.py][open_the_website] - Method has ended.************")

def helper_wait_element_and_input_text(selector:str, wait_time: int, value:str,browser:Selenium):
    """ Here wait for the element appear and 
     input text on the element, also we specify the browser to use.

    Keyword arguments:
    url -- The url that is going to be opened.
    browser -- In order to use the same browser variable so this can continue and didn't throw an expception
    wait_time -- integer that represents how many seconds is going to wait for the element to appear on the screen
    value  -- string that represents what we want to type into the text field
    """
    logging.info("*********[common.py][helper_wait_element_and_input_text] - Method has started.***********")
    browser.wait_until_element_is_visible(
        selector,
        wait_time,
        selector+": Input Text not found in the permited timeframe."
    )

    logging.info("Typing into: "+selector+"...")
    # Input Text - value
    browser.input_text_when_element_is_visible(selector,value) 
    logging.info("Typed into: "+selector)

    logging.info("***********[Tasks.py][helper_wait_element_and_input_text] - Method has ended.************")

def helper_wait_element_and_click(selector:str, wait_time: int, browser:Selenium):
    """ Here wait for the element appear and 
     clicked on the element, also we specify the browser to use.

    Keyword arguments:
    url -- The url that is going to be opened.
    browser -- In order to use the same browser variable so this can continue and didn't throw an expception
    wait_time -- integer that represents how many seconds is going to wait for the element to appear on the screen
    """
    logging.info("*********[common.py][helper_wait_element_and_click] - Method has started.***********")
    browser.wait_until_element_is_visible(
        selector,
        wait_time,
        selector+":Unable to click on the element, the element didn't appear."
    )
    logging.info("Clicking on: "+selector+"...")
    browser.click_element(selector)
    logging.info(selector+": Clicked.")
    logging.info("***********[Tasks.py][helper_wait_element_and_click] - Method has ended.************")

def take_screenshot(browser: Selenium, folder_path:str, file_name=None, selector=None):
    """ This function is used to take a screenshot.

    Keyword arguments:
    url -- The url that is going to be opened.
    browser -- In order to use the same browser variable so this can continue
    """
    time.sleep(3)
    if(file_name is None):
        now_sufix=dt.now().strftime("%d%m%Y_%H%M%S%f")
        name_file=now_sufix+".png"
    else:
        name_file=file_name
    #Get screenshot path
    screnshoot_path=os.path.join(folder_path.strip(), name_file)
    #Validate selector
    if(selector is None):
        browser.screenshot(None,screnshoot_path)
    else: 
        browser.screenshot(selector,screnshoot_path)
    return screnshoot_path

def create_or_clean_dir(folder_path: str):
    shutil.rmtree(folder_path, ignore_errors=True)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass

def get_begin_date(number_months:int):
    """ This functions will get the begin the date, based on the months number. 
    Conditions: Example of how this should work: 0 or 1 - only the current month, 2 - current and previous month, 3 - current and two previous months, 

    Keyword arguments:
    number_months -- number of months for which you need to receive news
    
    """
    actual_date=date.today()
    diff_months=number_months-1

    if(number_months>=0 and number_months<2):
        return dt(actual_date.year, actual_date.month, 1 ).strftime("%m/%d/%Y")
    else:
        return (actual_date - relativedelta( months=diff_months)).strftime("%m/%d/%Y")

def count_phrases(input_text:str, phrase:str):
    """ This functions get the count of phrases, in a certain text.

    Keyword arguments:
    input_text -- refers to the text where the phrase is going to be looked up
    phrase -- refers to the word that is going to be search for on the text
    """
    array_phrases=re.findall(str(phrase).lower(), str(input_text).lower())
    return len(array_phrases)

def contains_ammounts(description:str, title:str):
    """ This function is used to validate if is there any ammount on the title or description.
        Examples: Possible formats: $11.1 | $111,111.11 | 11 dollars | 11 USD

    Keyword arguments:
    title -- This refers to the text of the title of the article
    description -- this referst to the text of the description for the article
    """
    if(description==''):
        description_var=False
    else:
        array_ammounts=re.findall("(\$[0-9]+([,][0-9][0-9][0-9])*(\.[0-9])?([0-9])*) | ([0-9]+ dollars) | ([0-9]+ USD)", description)
        description_var=True if len(array_ammounts) else False

    if description_var:
        return True
    array_title=re.findall("(\$[0-9]+([,][0-9][0-9][0-9])*(\.[0-9])?([0-9])*) | ([0-9]+ dollars) | ([0-9]+ USD)", title)
    return True if len(array_title) else False

def get_article_date(browser:Selenium, idx:str):
    """ This function is used to get the date of an article.

    Keyword arguments:
    idx -- this is index of the element that we need to get
    browser -- In order to use the same browser variable so this can continue
    """
    description=''
    try: 
        description=browser.get_text("//li[contains(@data-testid,'search-bodega-result')]["+idx+"]//p[contains(@class,'css-16nhkrn')]")
    except Exception as e:
        pass
    return description