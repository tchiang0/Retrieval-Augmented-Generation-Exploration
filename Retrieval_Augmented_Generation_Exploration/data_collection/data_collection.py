import requests
import json
import pandas as pd
from config import API_KEY


class DataGather():
    def __init__(self) -> None:
        self.genre_dictionary = self.__get_genre_dictionary__()


    def get_movie_data(self, page_num: int):
        """ Call tmddb api to get movie data. """
        url = "https://api.themoviedb.org/3/discover/movie?with_original_language=en&page=" + str(page_num)
        headers = {
            "accept": "application/json",
            "Authorization": API_KEY
        }
        response = requests.get(url, headers=headers)
        return response


    def __get_genre_dictionary__(self):
        url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
        headers = {
            "accept": "application/json",
            "Authorization": API_KEY
        }
        response = requests.get(url, headers=headers)
        genre_list = json.loads(response.text)['genres']
        genre_dict = {}
        for i in genre_list:
            idx = i['id']
            name = i['name']
            genre_dict[idx] = name
        return genre_dict


    def get_genre_name(self, genre_idx_list):
        return [self.genre_dictionary[idx] for idx in genre_idx_list]


def main():
    master_movie_data = pd.DataFrame()
    data_collector = DataGather()
    page_num = 1
    while True:
        response = data_collector.get_movie_data(page_num)
        if response.status_code != 400:
            movie_json = json.loads(response.text)['results']
            test = pd.json_normalize(movie_json)
            master_movie_data = pd.concat([master_movie_data, test], ignore_index=True)
            page_num += 1
        else:
            break
    master_movie_data.loc[:, 'genre_names'] = master_movie_data['genre_ids'].apply(data_collector.get_genre_name)
    master_movie_data.to_csv("Master Movie Dataset.csv")

if __name__ == "__main__":
    main()
