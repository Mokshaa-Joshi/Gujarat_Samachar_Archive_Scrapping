import requests
from bs4 import BeautifulSoup
import streamlit as st
from deep_translator import GoogleTranslator
import re
from datetime import datetime

def scrape_articles(date=None):
    base_url = "https://www.gujaratsamachar.com/"
    
    try:
        # If a date is provided, append it to the URL
        if date:
            date_str = date.strftime("%Y-%m-%d")
            url = f"{base_url}archive/{date_str}"
        else:
            url = base_url
        
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        for article in soup.find_all('div', class_='news-box'):
            title_element = article.find('a', class_='theme-link news-title')
            link_element = article.find('a', class_='theme-link')
            summary_element = article.find('p')
            
            if title_element and link_element:
                title = title_element.text.strip()
                link = link_element['href']
                summary = summary_element.text.strip() if summary_element else ""
                
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
        
        return articles
    except Exception as e:
        st.error(f"An error occurred while scraping articles: {e}")
        return []

def scrape_article_content(link):
    try:
        article_response = requests.get(link)
        article_response.raise_for_status()
        
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        
        content_div = article_soup.find('div', class_='article-content')  # Adjust the class as needed
        if content_div:
            content = content_div.get_text(separator=' ').strip()
        else:
            content_elements = article_soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol'])
            content = ' '.join([element.get_text().strip() for element in content_elements])
        
        content_in_gujarati = re.sub(r'[^\u0A80-\u0AFF\s]', '', content)
        
        return content_in_gujarati
    except Exception as e:
        return f"Error loading article content: {e}"

def translate_to_gujarati(query):
    try:
        translated_query = GoogleTranslator(source='en', target='gu').translate(query)
        return translated_query
    except Exception as e:
        return f"Translation Error: {e}"

def search_articles(query, articles):
    return [article for article in articles if query.lower() in article['title'].lower() or query.lower() in article['summary'].lower()]

def main():
    st.title("Gujarat Samachar Article Search")
    st.write("Enter a keyword and optionally a date to search for relevant articles.")

    # Input for search query
    query = st.text_input("Search for articles", "")
    
    # Input for date
    date_input = st.date_input("Select a date (optional)", value=None)
    
    if query:
        translated_query = translate_to_gujarati(query)
        st.write(f"Translated query (Gujarati): {translated_query}")
    else:
        translated_query = ""

    # Scrape articles based on the selected date
    articles = scrape_articles(date_input)
    if not articles:
        st.warning("No articles found. Please try again later.")
        return
    
    if translated_query and not translated_query.startswith("Translation Error"):
        filtered_articles = search_articles(translated_query, articles)
        if filtered_articles:
            st.subheader(f"Search Results for '{query}':")
            for article in filtered_articles:
                st.markdown(f"### <a href='{article['link']}' target='_blank'>{article['title']}</a>", unsafe_allow_html=True)
                st.write(article['summary'])
                st.write(article['content'])
        else:
            st.warning(f"No articles found for '{query}'.")
    else:
        st.info("Please enter a search term.")

if __name__ == "__main__":
    main()
