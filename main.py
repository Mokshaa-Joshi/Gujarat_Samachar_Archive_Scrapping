import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Function to scrape articles from a page
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Print the HTML to understand the structure (optional, for debugging)
    # Uncomment the following line if you want to inspect the HTML structure
    # print(soup.prettify())  # Uncomment to inspect HTML structure

    # Assuming the articles are contained in <article> tags (adjust as necessary)
    articles = soup.find_all('article')

    scraped_articles = []
    for article in articles:
        title = article.find('h2')
        content = article.find('div', class_='entry-summary')
        link = article.find('a')

        # Ensure valid content is extracted before processing
        if title and content and link:
            title = title.text.strip()
            content = content.text.strip()
            link = link['href']
            date_str = article.find('time')['datetime']
            pub_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

            # Collect the article data
            scraped_articles.append({
                "title": title,
                "content": content,
                "link": link,
                "date": pub_date
            })

    return scraped_articles

# Function to scrape multiple pages
def scrape_all_pages():
    base_url = "https://www.gujaratsamachar.com/archives"
    all_articles = []
    for page in range(1, 6):  # Scrape the first 5 pages (adjust as needed)
        url = f"{base_url}?page={page}"
        articles = scrape_page(url)
        all_articles.extend(articles)

    return all_articles

if __name__ == "__main__":
    articles = scrape_all_pages()
    if articles:
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"Date: {article['date'].strftime('%B %d, %Y')}")
            print(f"Link: {article['link']}")
            print("---")
    else:
        print("No articles found.")
