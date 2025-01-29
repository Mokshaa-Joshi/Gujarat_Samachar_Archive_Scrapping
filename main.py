import requests
from bs4 import BeautifulSoup
import streamlit as st
from deep_translator import GoogleTranslator
import re
from datetime import datetime

def scrape_articles():
    base_url = "https://www.gujaratsamachar.com/"
    response = requests.get(base_url)
    
    if response.status_code != 200:
        st.error("Failed to retrieve the website. Please check the URL or your internet connection.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for article in soup.find_all('div', class_='news-box'):
        title_element = article.find('a', class_='theme-link news-title')
        date_element = article.find('div', class_='date')  # Update with correct class for date
        
        if not title_element:
            continue
        
        title = title_element.text.strip()
        link = title_element['href']
        summary = article.find('p').text.strip() if article.find('p') else ""
        
        if link.startswith('/'):
            link = base_url + link
        
        # Extracting date (modify based on actual date format)
        if date_element:
            article_date = date_element.text.strip()
            try:
                article_date = datetime.strptime(article_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                article_date = None
        else:
            article_date = None
        
        content = scrape_article_content(link)
        
        if title and link and content:
            articles.append({
                'title': title,
                'link': link,
                'summary': summary,
                'content': content,
                'date': article_date
            })
    
    return articles

def scrape_article_content(link):
    try:
        article_response = requests.get(link)
        if article_response.status_code != 200:
            return "Error loading article content."
        
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        
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

def translate_to_gujarati(query):
    try:
        translated_query = GoogleTranslator(source='en', target='gu').translate(query)
        return translated_query
    except Exception as e:
        return f"Translation Error: {e}"

def search_articles(query, date, articles):
    filtered_articles = []
    
    for article in articles:
        title_match = query.lower() in article['title'].lower()
        summary_match = query.lower() in article['summary'].lower()
        date_match = not date or (article['date'] and article['date'] == date)
        
        if (title_match or summary_match) and date_match:
            filtered_articles.append(article)
    
    return filtered_articles

def main():
    st.title("Gujarat Samachar Article Search")
    st.write("Enter a keyword and select a date to search for relevant articles.")

    query = st.text_input("Search for articles", "")
    selected_date = st.date_input("Select a date (optional)", value=None)
    
    formatted_date = selected_date.strftime("%Y-%m-%d") if selected_date else None
    
    if query:
        translated_query = translate_to_gujarati(query)
        st.write(f"Translated query (Gujarati): {translated_query}")
    else:
        translated_query = ""

    articles = scrape_articles()
    if not articles:
        st.warning("No articles found. Please try again later.")
        return
    
    if translated_query:
        filtered_articles = search_articles(translated_query, formatted_date, articles)
        if filtered_articles:
            st.subheader(f"Search Results for '{query}' on {formatted_date if formatted_date else 'All Dates'}:")
            for article in filtered_articles:
                st.markdown(f"### <a href='{article['link']}' target='_blank'>{article['title']}</a> - {article['date']}", unsafe_allow_html=True)
                st.write(article['summary'])
                st.write(article['content'])
        else:
            st.warning(f"No articles found for '{query}' on {formatted_date}.")
    else:
        st.info("Please enter a search term.")

if __name__ == "__main__":
    main()
