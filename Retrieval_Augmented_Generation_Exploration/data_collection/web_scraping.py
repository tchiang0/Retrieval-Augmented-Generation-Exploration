""" Rotten Tomato Scraping; get movie critics and reviews. """
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class webScraper():
    """ Rotten Tomato web scraper. """
    def __init__(self):
        pass
    

    def find_rotten_tomatoes_url(movie_title):
        """ Get the movie url. """
        # Construct the search URL for the Rotten Tomatoes website
        search_url = f"https://www.rottentomatoes.com/search?search={movie_title.replace(' ', '+')}"
        # Send a GET request to the URL
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, "html.parser")
        movie_url = soup.find('a', {'class': 'unset', 'data-qa': 'thumbnail-link'})['href']
        return movie_url


    def get_critics(self, movie_url):
        """ Get top 100 pages (or all) of movie critics. """
        # Initialize a headless browser (Chrome WebDriver)
        driver = webdriver.Chrome()

        # Load the movie review page
        driver.get(f"{movie_url}/reviews")

        # Locate the "Load More" button
        load_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'rt-button[data-qa="load-more-btn"]'))
        )

        # Click the "Load More" button 100 times
        for _ in range(100):
            load_more_button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract all critics reviews (including the initially visible and dynamically loaded reviews)
        reviews = soup.find_all("p", "review-text")
        visible_reviews = [review.text.strip() for review in reviews]

        driver.quit()
        return visible_reviews


def main():
    pass


if __name__ == "__main__":
    main()
