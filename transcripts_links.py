import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException
)

# Load the Fortune 500 companies list
fortune_500_df = pd.read_csv('/Users/sanchitarane/Desktop/CompanyList.csv')  # Replace with your actual CSV file
companies = fortune_500_df['Company Name'].tolist()
tickers = fortune_500_df['Ticker Symbol'].tolist()

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

# List to store all results
all_results = []

# Loop through each company
for company, ticker in zip(companies[:100], tickers[:100]):
    success = False
    for exchange in ['nasdaq', 'nyse']:
        # Convert exchange and ticker to lowercase
        ticker_lower = ticker.lower()

        # Construct the Fool.com URL for the company
        url = f"https://www.fool.com/quote/{exchange}/{ticker_lower}/#quote-earnings-transcripts"

        try:
            driver.get(url)
            
            # Check if the page resulted in a 404 error by looking for specific text
            if "404 Error" in driver.page_source or "Page Not Found" in driver.page_source:
                print(f"404 Error detected for {company} on {exchange.upper()}. Trying next exchange.")
                continue  # Try the next exchange

            success = True
            print(f"Successfully accessed {company} on {exchange.upper()}.")

            # Wait for the pop-up to appear and close it (if it exists)
            try:
                close_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="popup-x"]'))
                )
                close_button.click()
                print(f"Pop-up closed for {company}.")
            except TimeoutException:
                print(f"No pop-up appeared for {company}.")

            # Attempt to click the "View More" button to load all transcripts
            click_count = 0
            max_clicks = 7

            while click_count < max_clicks:
                try:
                    element = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="quote-earnings-transcripts"]/button'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    driver.execute_script("arguments[0].click();", element)
                    print(f"Button clicked {click_count + 1} time(s) for {company}.")
                    click_count += 1
                    time.sleep(1)
                except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException):
                    print(f"Stopping after {click_count} click(s) for {company}.")
                    break
                except TimeoutException:
                    print(f"Button was not found within the time limit for {company}.")
                    break

            # Extract transcript links
            transcript_links = driver.find_elements(By.CSS_SELECTOR, '#earnings-transcript-container a')
            hrefs = [link.get_attribute('href') for link in transcript_links]

            # Store the results
            for href in hrefs:
                full_url = href if href.startswith('http') else 'https://www.fool.com' + href
                all_results.append({'company': company, 'ticker': ticker, 'exchange': exchange, 'link': full_url})

            break  # Exit the exchange loop if successful

        except WebDriverException as e:
            print(f"Failed to access {company} on {exchange.upper()}: {e}")
            continue  # Try the next exchange if there's a WebDriver issue

    if not success:
        print(f"Failed to find transcripts for {company} on both NASDAQ and NYSE.")

# Close the browser
driver.quit()

# Convert the results to a DataFrame
all_transcripts_df = pd.DataFrame(all_results)

# Save the DataFrame to a CSV file
all_transcripts_df.to_csv('transcripts.csv', index=False)
print("All transcripts saved to transcripts.csv")
