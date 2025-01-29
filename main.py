import requests
from bs4 import BeautifulSoup
import streamlit as st

def scrape_articles():
    base_url = "https://www.gujaratsamachar.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    articles = []
    page_number = 1  # Start from the first page
    
    while True:
        response = requests.get(f"{base_url}archive?page={page_number}", headers=headers)
        
        if response.status_code != 200:
            st.error(f"Failed to retrieve the website. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all article containers
        article_boxes = soup.find_all('div', class_='news-box')
        if not article_boxes:
            st.warning("No articles found on this page.")
            break
        
        for article in article_boxes:
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
        
        # Check if there is a next page; if not, stop
        next_page = soup.find('a', class_='next')
        if not next_page:
            break
        
        # Move to the next page
        page_number += 1
    
    return articles
