from selenium import webdriver
from atlassian import Confluence
from tqdm import tqdm
from time import sleep
from configs import *
import warnings
import os

# Filter warnings
warnings.filterwarnings('ignore')

# Params
DRIVER = os.path.join(LOCAL_DIR, 'chromedriver.exe')
CONF = Confluence(url=ROOT_PAGE, username=USER, password=TOKEN)
os.chdir(LOCAL_DIR)

# Functions
def need_sleep(seconds=5):
    sleep(seconds)
    
def find_children_pages(conf_client, root_page_id):
    pages = conf_client.get_subtree_of_content_ids(root_page_id)
    dict_pages = {}
    
    for page_id in pages:
        page_title = conf_client.get_page_by_id(page_id)['title']
        dict_pages[str(page_id)] = page_title
    
    return dict_pages
    
def init_driver():
    # Create download directory
    confluence_path = os.path.join(os.getcwd(), 'confluence_pages')
    chrome_options = webdriver.ChromeOptions()
    if not os.path.exists(confluence_path):
        os.mkdir(confluence_path)
    
    # Set download directory
    prefs = {"download.default_directory" : confluence_path}
    chrome_options.add_experimental_option("prefs", prefs)

    # Init driver
    driver = webdriver.Chrome(executable_path=DRIVER, options=chrome_options)
    driver.maximize_window()
    
    return driver

def auth_confluence(driver, url, user, password):
    # Get page
    driver.get(url)
    need_sleep()
    
    # User
    driver.find_element_by_id('username').send_keys(user)
    driver.find_element_by_id('login-submit').click()
    need_sleep()
    
    # Password
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_id('login-submit').click()
    need_sleep()
    
    return driver

def load_page(driver, url):
    # Get page
    driver.get(url)
    need_sleep(10)
    
    # Export page
    driver.find_element_by_id('downloadableLink').click()
    need_sleep(2)

def main():
    # Start
    print('Start.')
    
    # Get pages ids
    dict_pages = find_children_pages(CONF, ROOT_PAGE_ID)
    print(f'Got {len(dict_pages)} pages.')
    
    # Init driver
    driver = init_driver()
    print('Inited driver.')
    
    # Authentification
    driver = auth_confluence(driver, ROOT_PAGE, USER, PASSWORD)
    print('Driver auth successful.')
    
    # Export pages as PDF
    error_pages = []
    for page_id, title in tqdm(dict_pages.items()):
        try:
            url = PDF_LOAD_BASE_URL + page_id
            load_page(driver, url)
        except:
            error_pages += [f'TITLE: {title}; PAGE_ID: {page_id}']
            
    if bool(error_pages):
        print(f'Errors occurred: {len(error_pages)}. See file.')
        file = open('!Not loaded pages.txt', 'w')
        [file.write(page + '\n') for page in error_pages]
        file.close()
    else:
        print('No errors occurred.')
    
    driver.close()
    print('End.')

if __name__ == '__main__':
    main()
