import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import streamlit as st
from deep_translator import GoogleTranslator
import re
from datetime import datetime

# Function to scrape articles from the archive pages using Selenium
def scrape_articles():
    articles = []
    
    # Setup the WebDriver (make sure you have the ChromeDriver installed)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser window)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    base_url = "https://www.gujaratsamachar.com/archives"
    
    # Loop through the first few pages of the archive (you can increase this range for more pages)
    for page_num in range(1, 6):  # Scraping first 5 pages (adjust as needed)
        url = f"{base_url}?page={page_num}"
        driver.get(url)
        
        time.sleep(2)  # Give time for the page to load
        
        # Parse the page source using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract articles from each page
        for article in soup.find_all('div', class_='news-box'):
            title = article.find('a', class_='theme-link news-title').text.strip()
            link = article.find('a', class_='theme-link')['href']
            summary = article.find('p').text.strip() if article.find('p') else ""
            
            if link.startswith('/'):
                link = base_url + link
            
            content = scrape_article_content(link)
            
            if title and link and content:
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'content': content
                })
    
    driver.quit()  # Close the WebDriver after scraping
    return articles

# Function to scrape content from individual articles
def scrape_article_content(link):
    try:
        response = requests.get(link)
        if response.status_code != 200:
            return "Error loading article content."
        
        article_soup = BeautifulSoup(response.content, 'html.parser')
        
        content_div = article_soup.find('div')
        if not content_div:
            content_elements = article_soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol'])
            content = ' '.join([element.get_text().strip() for element in content_elements])
        else:
            content = content_div.text.strip() if content_div else "Content not available."
        
        content_in_gujarati = re.sub(r'[^\u0A80-\u0AFF\s]', '', content)
        
        return content_in_gujarati
    except Exception as e:
        return f"Error: {e}"

# Function to translate English query to Gujarati
def translate_to_gujarati(query):
    try:
        translated_query = GoogleTranslator(source='en', target='gu').translate(query)
        return translated_query
    except Exception as e:
        return f"Translation Error: {e}"

# Function to search articles based on the query
def search_articles(query, articles):
    return [article for article in articles if query.lower() in article['title'].lower() or query.lower() in article['summary'].lower()]

# Streamlit main function
def main():
    st.title("Gujarat Samachar Article Search")
    st.write("Enter a keyword to search for relevant articles. You can also see the Gujarati translation of your query.")

    query = st.text_input("Search for articles", "")
    
    if query:
        translated_query = translate_to_gujarati(query)
        st.write(f"Translated query (Gujarati): {translated_query}")
    else:
        translated_query = ""

    # Scrape the articles from multiple archive pages using Selenium
    articles = scrape_articles()
    if not articles:
        st.warning("No articles found. Please try again later.")
        return
    
    # Search and filter articles based on the translated query (if available)
    if translated_query:
        filtered_articles = search_articles(translated_query, articles)
        if filtered_articles:
            st.subheader(f"Search Results for '{query}':")
            today_date = datetime.now().strftime("%B %d, %Y")
            for article in filtered_articles:
                st.markdown(f"### <a href='{article['link']}' target='_blank'>{article['title']}</a> - {today_date}", unsafe_allow_html=True)
                st.write(article['summary'])
                st.write(article['content'])
        else:
            st.warning(f"No articles found for '{query}'.")
    else:
        st.info("Please enter a search term.")

if __name__ == "__main__":
    main()
