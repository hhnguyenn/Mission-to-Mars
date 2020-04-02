
#Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path={'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
 
    news_title, news_paragraph = mars_news(browser)
    
    mars_pix = list()
    products = ['Cerberus','Schiaparelli','Syrtis Major','Valles Marineris']
    for product in products:
        hemi_title, hemi_url = hemi_data(browser, product)
        hemi_dict = {"img_url":hemi_url, "title": hemi_title}
        mars_pix.append(hemi_dict)

# Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(browser),
        "hemi_data": mars_pix,
        "last_modified": dt.datetime.now()
    }

    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem=news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one("figure.lede a img").get("src")

    except AttributeError:
        return None
 
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url

def mars_facts(browser):
    fact_url = 'https://space-facts.com/mars/'
    raw_fact_table = pd.read_html(fact_url)
    df = raw_fact_table[0] 
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def hemi_data(browser, product):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    
    browser.is_element_present_by_text(f'{product} Hemisphere Enhanced', wait_time = 1)
    browser.click_link_by_partial_text(f'{product} Hemisphere Enhanced')
    
    #BeautifulSoup to parse and extract image url
    hemi_soup = BeautifulSoup(browser.html, 'html.parser')
    try:
        hemi_url = hemi_soup.select_one('img.wide-image').get('src')
        hemi_title = hemi_soup.select_one('h2.title').text
    except AttributeError:
        return None
    
    img_url = f'https://astrogeology.usgs.gov{hemi_url}'

    return hemi_title, img_url

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



