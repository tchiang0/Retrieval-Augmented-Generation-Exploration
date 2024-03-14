""" Data Collection from TMDB. """
import requests
import json
import pandas as pd
from config import API_KEY


class DataGather():
    """ DataGather class; call TMDB APIs """
    def __init__(self) -> None:
        self.genre_dictionary = self.__get_genre_dictionary__()
        self.actors_list = []
        self.actors_dict = {}
        self.crew_map = {
            "Director": ["Director", "Co-Director"],
            "Producer": ["Producer", "Co-Producer"]
        }
        self.crew_dict = {
            "Director": {}, 
            "Producer": {}
        }
        self.crew_list = {
            "Director": [],
            "Producer": []
        }


    def __get_genre_dictionary__(self):
        """ Build genre dictionary. """
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


    def get_movie_data(self, page_num: int):
        """ Call tmddb api to get movie data. """
        url = "https://api.themoviedb.org/3/discover/movie?with_original_language=en&page=" + str(page_num)
        headers = {
            "accept": "application/json",
            "Authorization": API_KEY
        }
        response = requests.get(url, headers=headers)
        return response


    def get_genre_name(self, genre_idx_list):
        """ Get genre name from genre id list. """
        return [self.genre_dictionary[idx] for idx in genre_idx_list]


    def get_movie_credits(self, movie_id):
        """ Get movie cast and crew. """
        url = "https://api.themoviedb.org/3/movie/" + str(movie_id) + "/credits?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzNGZmNTVjNTkzNjZjMDA1ZTRmNDJiMWEzMDYzZmM3MyIsInN1YiI6IjY1ZWZiYzM4NDFlZWUxMDE2MjU4ZmJhYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.y3opq16YWBh_uD-i1kUnI5BIhgnq0yf1OTOamVKe1DI"
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)


    def get_movie_actors(self, movie_id):
        """ Get movie actors and make master actor list. """
        movie_credits = self.get_movie_credits(movie_id)
        cast = movie_credits['cast']
        cur_actors_list = []
        for actor in cast:
            actor_name = actor["name"]
            cur_actors_list.append(actor_name)
            if actor_name not in self.actors_dict:
                self.actors_list.append(actor_name)
                self.actors_dict[actor_name] = len(self.actors_list) - 1
        return cur_actors_list


    def get_crew(self, crew_type, movie_id):
        movie_credit = self.get_movie_credits(movie_id)
        crew = movie_credit['crew']
        cur_list = []
        for c in crew:
                cur_list.append(c["name"])
                if c["name"] not in self.crew_dict[crew_type]:
                    self.crew_list[crew_type].append(c["name"])
                    self.crew_dict[crew_type][c["name"]] = len(self.crew_list[crew_type]) - 1
        return cur_list


def main():
    """ Main driver. """
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
    master_movie_data.loc[:, 'actors'] = master_movie_data['id'].apply(data_collector.get_movie_actors)
    master_movie_data.loc[:, "directors"] = master_movie_data.apply(
        lambda row: data_collector.get_crew("Director", row["id"]), axis=1)
    master_movie_data.loc[:, "producers"] = master_movie_data.apply(
        lambda row: data_collector.get_crew("Producer", row["id"]), axis=1)
    master_movie_data.to_csv("Master Movie Dataset.csv")

if __name__ == "__main__":
    main()
