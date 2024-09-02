import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load the CSV file
csv_file_path = '/Users/sanchitarane/Desktop/transcripts.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file_path)

# Extract the URLs from the 'link' column
url_paths = df['link'].tolist()

# Function to scrape content from each URL
def scrape_content(url):
    try:
        page = requests.get(url)
        page.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(page.text, 'html.parser')

        # Find the div with class "article body"
        article_body = soup.find('div', class_='article-body')

        if not article_body:
            print(f"Could not find the article body for {url}")
            return None

        # Initialize a flag to start collecting content after finding the header
        content_started = False
        collected_content = []

        # Iterate through all child elements in the article body
        for element in article_body.find_all(True, recursive=False):
            if element.name == 'h2' and 'Prepared Remarks' in element.text:
                content_started = True
                continue  # Skip the header itself

            if content_started and element.name == 'p':
                collected_content.append(element.get_text(strip=True))

        return '\n'.join(collected_content).strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# List to store the results
results = []

# Iterate over the URL paths from the CSV and scrape the content
for path in url_paths:
    full_url = path if path.startswith('http') else 'https://www.fool.com' + path  # Adjust if full URLs are provided
    content = scrape_content(full_url)
    if content:  # Only append if content was successfully scraped
        results.append({'url': full_url, 'content': content})

# Convert the results into a DataFrame
scraped_df = pd.DataFrame(results)

# Save the DataFrame to a CSV file
scraped_df.to_csv('scraped_content.csv', index=False)

print("Scraped content saved to 'scraped_content.csv'.")
