import requests
from bs4 import BeautifulSoup
import streamlit as st
from deep_translator import GoogleTranslator
import re
from datetime import datetime, timedelta

BASE_URL = "https://www.gujaratsamachar.com/"

def get_articles():
    """Fetches articles from Gujarat Samachar."""
    response = requests.get(BASE_URL)
    
    if response.status_code != 200:
        st.error("Failed to retrieve the website. Please check your internet connection.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    for article in soup.find_all('div', class_='news-box'):
        title_tag = article.find('a', class_='theme-link news-title')
        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = title_tag['href']
        summary = article.find('p').text.strip() if article.find('p') else ""

        # Ensure full link
        if link.startswith('/'):
            link = BASE_URL + link

        # Extract article content
        content = scrape_article_content(link)

        # Extract the publication date (assuming it's present in the article)
        date_tag = article.find('span', class_='date')  # Update with correct class if necessary
        article_date = date_tag.text.strip() if date_tag else ""

        # Store article data
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
    """Extracts article content from a given link."""
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

        # Extract only Gujarati text
        content_in_gujarati = re.sub(r'[^\u0A80-\u0AFF\s]', '', content)
        
        return content_in_gujarati
    except Exception as e:
        return f"Error: {e}"

def translate_to_gujarati(query):
    """Translates the query to Gujarati using Google Translator."""
    try:
        return GoogleTranslator(source='auto', target='gu').translate(query)
    except Exception as e:
        return f"Translation Error: {e}"

def search_articles(query, articles):
    """Filters articles based on the query."""
    query_lower = query.lower()
    return [
        article for article in articles 
        if query_lower in article['title'].lower() or query_lower in article['summary'].lower() or query_lower in article['content'].lower()
    ]

def filter_articles_by_date(selected_date, articles):
    """Filters articles based on the selected date."""
    selected_date_str = selected_date.strftime("%d-%m-%Y")  # Adjust date format if necessary
    return [article for article in articles if selected_date_str in article['date']]

def main():
    st.title("Gujarat Samachar Article Search by Date and Keyword")

    # User input for date selection
    selected_date = st.date_input("Select a date", datetime.today())

    # User input for keyword
    query = st.text_input("Enter keyword for search", "")

    # Translate query
    translated_query = translate_to_gujarati(query) if query else ""

    if query:
        st.write(f"Translated Query: {translated_query}")

    # Fetch articles
    articles = get_articles()

    if not articles:
        st.warning("No articles found.")
        return

    # Filter articles by date
    filtered_by_date = filter_articles_by_date(selected_date, articles)

    if not filtered_by_date:
        st.warning(f"No articles found for the selected date: {selected_date.strftime('%B %d, %Y')}")
        return

    # Filter articles by query
    if translated_query:
        filtered_articles = search_articles(translated_query, filtered_by_date)
    else:
        filtered_articles = filtered_by_date

    # Display results
    if filtered_articles:
        st.subheader(f"Articles from {selected_date.strftime('%B %d, %Y')}:")
        for article in filtered_articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.write(f"**Summary:** {article['summary']}")
            st.write(f"**Content:** {article['content'][:300]}...")  # Limit preview
            st.write("---")
    else:
        st.warning(f"No articles found matching '{query}'.")

if __name__ == "__main__":
    main()
