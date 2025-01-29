import requests
from bs4 import BeautifulSoup
import streamlit as st

def scrape_articles():
    base_url = "https://www.gujaratsamachar.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    articles = []
    
    # Try scraping the main page first
    response = requests.get(base_url, headers=headers)
    
    # Check the response status code
    if response.status_code != 200:
        st.error(f"Failed to retrieve the website. Status code: {response.status_code}")
        return []
    
    st.write(f"Successfully retrieved the main page")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print out the parsed HTML to verify its structure
    st.write(f"Parsed HTML (first 500 chars): {soup.prettify()[:500]}")
    
    # Now, let's find all articles on this page
    article_boxes = soup.find_all('div', class_='news-box')
    if not article_boxes:
        st.warning("No articles found on this page.")
        return []
    
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
        
        return content
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("Gujarat Samachar Article Search")
    st.write("Enter a keyword to search for relevant articles.")
    
    query = st.text_input("Search for articles", "")
    
    articles = scrape_articles()
    if not articles:
        st.warning("No articles found. Please try again later.")
        return
    
    if query:
        filtered_articles = [article for article in articles if query.lower() in article['title'].lower() or query.lower() in article['summary'].lower()]
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
