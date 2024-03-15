""" Data Collection from TMDB. """
import requests
import json
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from config import API_KEY

nltk.download('stopwords')
nltk.download('all')


class DataGather():
    """ DataGather class; call TMDB APIs """
    def __init__(self) -> None:
        self.master_movie_data = pd.DataFrame()
        self.genre_list, self.genre_dictionary = self.__get_genre_dictionary__()
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
        self.word_list = []
        self.word_dict = {}
        self.metrics = {
            "Genre": self.genre_list,
            "Actor": self.actors_list, 
            "Director": self.crew_list["Director"], 
            "Producer": self.crew_list["Producer"], 
            "Overview": self.word_list
        }


    def __get_genre_dictionary__(self):
        url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
        headers = {
            "accept": "application/json",
            "Authorization": API_KEY
        }
        response = requests.get(url, headers=headers)
        genres = json.loads(response.text)['genres']
        genre_dict = {}
        genre_list = []
        for i in genres:
            idx = i['id']
            name = i['name']
            genre_dict[idx] = name
            genre_list.append(idx)
        return (genre_list, genre_dict)


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
            "Authorization": API_KEY
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


    def one_hot_encoding(self, metric_type, id_list):
        if isinstance(id_list, str):
            id_list = json.loads(id_list)
        metric_list = self.metrics[metric_type]
        cur_list = [0] * len(metric_list)
        for id in id_list:
            cur_list[metric_list.index(id)] = 1
        return cur_list


    def tokenize_overview(self, movie_id):
        overview = self.master_movie_data[self.master_movie_data["id"] == movie_id]["overview"].values[0]
        filtered_sentence = []
        if isinstance(overview, str):
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(overview)
            word_tokens = [w.lower() for w in word_tokens]
            filtered_sentence = [w for w in word_tokens if not w in stop_words]
            filtered_sentence = [w for w in filtered_sentence if w.isalnum()]
            lemmatizer = WordNetLemmatizer()
            filtered_sentence = [lemmatizer.lemmatize(w) for w in filtered_sentence]
            filtered_sentence = list(set(filtered_sentence))
            for word in filtered_sentence:
                if word not in self.word_dict:
                    self.word_list.append(word)
                    self.word_dict[word] = len(self.word_list) - 1
        return filtered_sentence

def main():
    """ Main driver. """
    data_collector = DataGather()
    page_num = 1
    while True:
        response = data_collector.get_movie_data(page_num)
        if response.status_code != 400:
            movie_json = json.loads(response.text)['results']
            test = pd.json_normalize(movie_json)
            data_collector.master_movie_data = pd.concat([data_collector.master_movie_data, test], ignore_index=True)
            page_num += 1
        else:
            break
    data_collector.master_movie_data.loc[:, 'genre_names'] = data_collector.master_movie_data['genre_ids'].apply(data_collector.get_genre_name)
    data_collector.master_movie_data.loc[:, 'actors'] = data_collector.master_movie_data['id'].apply(data_collector.get_movie_actors)
    data_collector.master_movie_data.loc[:, "directors"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.get_crew("Director", row["id"]),
        axis=1)
    data_collector.master_movie_data.loc[:, "producers"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.get_crew("Producer", row["id"]),
        axis=1)
    # one hot encoding for genre
    data_collector.master_movie_data.loc[:, "one_hot_encoding_genres"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.one_hot_encoding("Genre", row["genre_ids"]),
        axis=1)
    # one hot encoding for actor
    data_collector.master_movie_data.loc[:, "one_hot_ecoding_actors"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.one_hot_encoding("Actor", row["actors"]),
        axis=1)
    # one hot encoding for director
    data_collector.master_movie_data.loc[:, "one_hot_encoding_director"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.one_hot_encoding("Director", row["directors"]),
        axis=1)
    # one hot encoding for producer
    data_collector.master_movie_data.loc[:, "one_hot_encoding_producer"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.one_hot_encoding("Producer", row["producers"]),
        axis=1)
    data_collector.master_movie_data.loc[:, "tokenized_overview"] = data_collector.master_movie_data['id'].apply(
        data_collector.tokenize_overview)
    data_collector.master_movie_data.loc[:, "one_hot_ecoding_overview"] = data_collector.master_movie_data.apply(
        lambda row: data_collector.one_hot_encoding("Overview", row["tokenized_overview"]),
        axis=1)
    print(data_collector.master_movie_data.shape)
    data_collector.master_movie_data.to_csv("Master Movie Dataset.csv")


if __name__ == "__main__":
    main()
