from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.Robocorp.Vault import Vault
from RPA.Robocorp.WorkItems import WorkItems


from utilities.common import open_the_website, helper_wait_element_and_input_text, helper_wait_element_and_click, get_begin_date, count_phrases, contains_ammounts, take_screenshot, get_article_date, create_or_clean_dir
from datetime import date

import pandas as pd
import logging
from retry import retry
import time


browser = Selenium()
file_system = FileSystem()
wait_time = 30
workItm=WorkItems() 
library = WorkItems()   


# Define a main() function that calls the other functions in order:
def main():
    """ This is the main function that will get the work item variables from Robocorp
    """
    logging.info("[tasks.py][main] - Method has started.")
    
    logging.info("Getting Work Items from Robocorp")
    payload = get_payload()
    phrase = payload['phrase']
    category_section=payload['category']
    #Example of how this should work: 0 or 1 - only the current month, 2 - current and previous month, 3 - current and two previous months,
    number_months= int(str(payload['months']))
    # print("category: "+category_section)
    # print("phrase: "+phrase)
    # print("months: "+str(number_months))
    logging.info("Cleaning/creating output folder")
    create_or_clean_dir("output")
    process(phrase, category_section, number_months)
    #*****************Loading Config File*******************
    logging.info("[Tasks.py][main] - Method has ended.")


def get_payload():
    workItm.get_input_work_item()
    payload = workItm.get_work_item_payload()
    return payload

@retry(delay=1, tries=3)
def process(search_phrase:str, category_section:str, months_number:int):
    """ This is function executes all the UI Interaction and generates the report.
        These are the steps: 
        1. Open the site by following the link
        2. Enter a phrase in the search field
        3. On the result page, apply the following filters:
            - select a news category or section
            - choose the latest news
        4. Get the values: title, date, and description.
        5. Store in an excel file.
        6. 6. Download the news picture and specify the file name in the excel file
        7. Follow the steps 4-6 for all news that fall within the required time period

        Arguments: 
        1. search_phrase: this is the phrase that the bot is going to search on the website
        2. category_section: is the section taht is going to be filter
        3: months_number: quantity of the months that is going to filter
    """
    logging.info("[tasks.py][process] - Method has started.")
    # We open the main website.
    try:
        logging.info("Openning website.")
        #Open the website and Maximize
        open_the_website("www.nytimes.com",browser)
        logging.info("Searching phrase.")
        #Click con Search Button
        selector_btn_search="//*[@data-test-id='search-button']"
        helper_wait_element_and_click(selector=selector_btn_search, wait_time=60, browser=browser)
        #Enter Phrase on Query Input Text
        selector_search="//*[@name='query']"
        helper_wait_element_and_input_text(selector=selector_search,  wait_time=30, value=search_phrase, browser=browser)
        #Click on 'Go' button
        selector_go_btn="//*[@data-test-id='search-submit']"
        helper_wait_element_and_click(selector=selector_go_btn, wait_time=30, browser=browser)
        logging.info("Filter by section.")
        #Clicking on 'Section' Dropdown button 
        selector_section_btn='//*[@data-testid="search-multiselect-button"]'
        helper_wait_element_and_click(selector=selector_section_btn, wait_time=30, browser=browser)
        # Chosing section from the dropdown menu - example 'Magazine'
        selector_category_check = "//*[contains(text(), '"+category_section+"')]"
        helper_wait_element_and_click(selector=selector_category_check, wait_time=30, browser=browser)
        logging.info("Filter by Date Range.")
        #Click on Date Range Dropdown button
        selector_date_range_btn="//*[@data-testid='search-date-dropdown-a']"
        helper_wait_element_and_click(selector=selector_date_range_btn, wait_time=30, browser=browser)
        #Choosing option 'Specific Dates' from DropDown Menu
        selector_specific_dates="//button[@value='Specific Dates']"
        helper_wait_element_and_click(selector=selector_specific_dates, wait_time=30, browser=browser)
        #Select Date Range
        begin_date=get_begin_date(months_number)
        end_date=date.today().strftime("%m/%d/%Y")
        #Input text on End Date field
        selector_begin_date="//input[@data-testid='DateRange-startDate']"
        helper_wait_element_and_input_text(selector=selector_begin_date, wait_time=30, value=begin_date, browser=browser)
        #Input text on End Date field
        selector_end_date="//input[@data-testid='DateRange-endDate']"
        helper_wait_element_and_input_text(selector=selector_end_date, wait_time=30, value=end_date, browser=browser)
        browser.press_keys(None,"ENTER")
        logging.info("Waiting time to apply filters...")
        #Waiting time to apply the filter
        time.sleep(6)
        #Getting the ammount of results 
        count_elements=browser.get_element_count("//li[@data-testid='search-bodega-result']")
        range_count=count_elements+1
        #Building the out dictionary so after this can be converted to a dataframe
        dt_output= {'Title':[], 'Date':[], 'Description':[], 'Picture Filename':[], 'Count of Search Phrases':[], 'Contains Ammount Money?':[]}   
        if(count_elements==0):
            logging.info("No results found.")
            path_exception=take_screenshot(browser, folder_path="output")
            return "Error: No results found. Screenshot: "+path_exception
        
        logging.info("Getting info from the list of articles: "+str(count_elements))
        #Looping through the list of articles
        for x in range(1,range_count):
            #Get Description
            #description=browser.get_text("//li[contains(@data-testid,'search-bodega-result')]["+str(x)+"]//p[contains(@class,'css-16nhkrn')]")
            description = get_article_date(browser=browser, idx=str(x))
            #Get Title
            title=browser.get_text("//li[contains(@data-testid,'search-bodega-result')]["+str(x)+"]//h4[contains(@class,'css-2fgx4k')]")
            #Get Date
            article_date=browser.get_text("//li[contains(@data-testid,'search-bodega-result')]["+str(x)+"]//span[contains(@data-testid,'todays-date')]")
            #Getting the count of search phrases in the title and description 
            counter_desc=count_phrases(description,search_phrase)
            counter_title=count_phrases(title,search_phrase)
            counter_phrases=counter_desc+counter_title  
            #True or False, depending on whether the title or description contains any amount of money
            article_ammount=contains_ammounts(description=description, title=title)
            #Downloading the picture and specify the file name in the excel file
            img=browser.find_element("//li[contains(@data-testid,'search-bodega-result')]["+str(x)+"]//img[contains(@class,'css-rq4mmj')]")
            screenshot_file="output/test"+str(x)+".png"
            img.screenshot(screenshot_file)

            #Appending each field to the dictionary
            dt_output['Title'].append(title)
            dt_output['Date'].append(article_date)
            dt_output['Description'].append(description)
            dt_output['Picture Filename'].append(screenshot_file)
            dt_output['Count of Search Phrases'].append(counter_phrases)
            dt_output['Contains Ammount Money?'].append(article_ammount)

        logging.info("Creating dataframe from dictionary 'dt_output'")
        #Creating the Dataframe
        df_report=pd.DataFrame(dt_output)
        #Generate output report excel file
        df_report.to_excel("output/report.xlsx", sheet_name="result", index=False)
        logging.info("Report had been generated properly.")
        browser.close_all_browsers
        logging.info("[Tasks.py][process] - Try Method has ended properly.")
    except Exception as e:
        path_screenshot=take_screenshot(browser, folder_path="output")
        logging.error("Error"+str(e)+". Screenshot: "+path_screenshot)
        browser.close_all_browsers
        logging.info("[Tasks.py][process] - Except Method has ended.")

# Main function
if __name__ == "__main__":
    main()
