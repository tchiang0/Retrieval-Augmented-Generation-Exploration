""" Rotten Tomato Scraping; get movie critics and reviews. """
import pandas as pd
import requests
import json
import re
import ast
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.exceptions import ChunkedEncodingError
from bs4 import BeautifulSoup

import sys
sys.path.append('/Users/dianechiang/Desktop/personal_projects/Retrieval_Augmented_Generation_Exploration/Retrieval_Augmented_Generation_Exploration/')
import data_collection as dt

URL_PATTERN = r'^https:\/\/www\.rottentomatoes\.com\/m\/*'

class webScraper():
    """ Rotten Tomato web scraper. """
    def __init__(self):
        self.df = self.get_movie_df()


    def get_movie_df(self):
        df = pd.read_csv("/Users/dianechiang/Desktop/personal_projects/Retrieval_Augmented_Generation_Exploration/Retrieval_Augmented_Generation_Exploration/Master Movie Dataset.csv")
        df['release_date'] = df['release_date'].astype(str)
        df_remove_duplicate = df.drop_duplicates(subset=['id'])
        df_remove_duplicate_not_confirmed_release_date = df_remove_duplicate.loc[df_remove_duplicate["release_date"] != "nan"]
        return df_remove_duplicate_not_confirmed_release_date


    def find_rotten_tomatoes_url(self, movie_title):
        """ Search URL for the Rotten Tomatoes. """
        search_url = f"https://www.rottentomatoes.com/search?search={movie_title.replace(' ', '+')}"
        try:
            response = requests.get(search_url, stream=True)
            soup = BeautifulSoup(response.content, "html5lib")
            all_urls = soup.findAll('a', {'class': 'unset', 'data-qa': 'thumbnail-link'})
            if not all_urls:
                print(f"{movie_title} has no url")
                return None

            all_urls = [url['href'] for url in all_urls]
            print(f"Gathered all urls for {movie_title}")
            return all_urls
        except ChunkedEncodingError as ex:
            print(f"Invalid chunk encoding {str(ex)}. Retrying")
            return self.find_rotten_tomatoes_url(movie_title)


    def find_correct_url(self, url_list, release_date, director_list):
        """ Check which url is correct from url_list. """
        if not url_list:
            return ""
        filtered_urls = [s for s in url_list if re.match(URL_PATTERN, s)]
        res_url = ""
        for url in filtered_urls:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html5lib')

                # Find the label with the text "Release Date (Theaters):"
                label = soup.find('b', class_='info-item-label', string="Release Date (Theaters):")
                if not label:
                    label = soup.find('b', class_='info-item-label', string="Release Date (Streaming):")
                if label:
                    time_element = label.find_next_sibling('span').find('time')
                    if time_element:
                        release_date_tomato = time_element.get_text(strip=True)
                        if release_date_tomato and release_date_tomato[-4:] == release_date[:4]:
                            res_url = url
                            print(f"{res_url} is the correct url")
                            return res_url
            except ChunkedEncodingError as ex:
                return self.find_correct_url(filtered_urls, release_date, director_list)
        if not res_url:
            for url in filtered_urls:
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html5lib')

                    label = soup.find('b', class_="info-item-label", string="Director:")
                    if label:
                        director_element = label.find_next_sibling('span').find('a')
                        if director_element:
                            director_tomato = director_element.get_text(strip=True)

                            if director_tomato in director_list:
                                res_url = url
                                print(f"{res_url} is the correct url")
                                return res_url
                except ChunkedEncodingError as ex:
                    return self.find_correct_url(filtered_urls, release_date, director_list)
        if not res_url:
            print(f"No valid url for this movie")
            return res_url


    def get_movie_info_and_ratings(self, movie_url):
        """ From movie's url, get the movie's info and rating"""
        res = {
            "movie_info": [],
            "movie_rating": []
        }
        if movie_url:
            try:
                print(f"Got movie url for {movie_url}")
                response = requests.get(movie_url)
                soup = BeautifulSoup(response.content, "html.parser")
                movie_info = soup.find('p', {'data-qa': 'movie-info-synopsis', 'slot': 'content'})
                movie_rating = soup.find('span', {'data-qa': 'movie-info-item-value'})
                if movie_info:
                    print(f"Movie info found for {movie_url}")
                    res["movie_info"].append(movie_info.text.strip())
                if movie_rating:
                    print(f"Movie rating found for {movie_url}")
                    res["movie_rating"].append(movie_rating.text.strip())
            except ChunkedEncodingError:
                print("Chunked encoding error occurred. Retrying...")
                return self.get_movie_info_and_ratings(movie_url)
        return res


    def get_critics(self, movie_url):
        """ Get top 100 pages (or all) of movie critics. """
        driver = webdriver.Chrome()
        driver.get(f"{movie_url}/reviews")

        # Locate the "Load More" button
        load_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'rt-button[data-qa="load-more-btn"]'))
        )

        # Click the "Load More" button 100 times
        for _ in range(100):
            load_more_button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")

        reviews = soup.find_all("p", "review-text")
        visible_reviews = [review.text.strip() for review in reviews]

        driver.quit()
        return visible_reviews


    def save_progress(self, progress_data, filename):
        """ Save scraping progress to json. """
        with open(filename, 'w') as file:
            json.dump(progress_data, file)


    def load_progress(self, filename):
        """ Load existing progress json to continue scraping. """
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None


    def process_movies(self, movie_ids, progress_filename):
        """ Process movies. """
        progress_data = self.load_progress(progress_filename)
        if progress_data is None:
            progress_data = {"processed_ids": [], "movie_info_and_rating": {}}

        for movie_id in movie_ids:
            if movie_id in progress_data["processed_ids"]:
                continue

            movie_title = self.df.loc[self.df['id'] == movie_id, "original_title"].iloc[0]
            release_date = self.df.loc[self.df['id'] == movie_id, "release_date"].iloc[0]
            directors_list = self.df.loc[self.df['id'] == movie_id, "directors"].iloc[0]
        
            print(f"Processing {movie_title}")
            all_search_urls = self.find_rotten_tomatoes_url(movie_title)
            movie_url = self.find_correct_url(all_search_urls, release_date, directors_list)
            movie_info = self.get_movie_info_and_ratings(movie_url)
            progress_data["movie_info_and_rating"][movie_id] = movie_info
            progress_data["processed_ids"].append(movie_id)
            self.save_progress(progress_data, progress_filename)


def main():
    """ Main Driver for Rotten Tomator Scraper. """
    web_scraper = webScraper()
    movie_ids = web_scraper.df["id"].to_list()
    progress_filename = "progress.json"
    web_scraper.process_movies(movie_ids, progress_filename)
    movie_json = web_scraper.load_progress('progress.json')
    return movie_json


if __name__ == "__main__":
    main()
