""" Content Based Filtering (KNN). """
import pandas as pd
# import requests
import json
from scipy import spatial
# from config import API_KEY


class contentBasedFiltering():
    def __init__(self) -> None:
        self.master_movie_data = pd.read_csv("/Users/dianechiang/Desktop/\
            personal_projects/Retrieval_Augmented_Generation_Exploration/\
            Retrieval_Augmented_Generation_Exploration/Master Movie Dataset.csv")


    def contains_name(self, names_list, name):
        """ Check if name is contained in names_list. """
        return name in names_list


    # can be changed to name if needed
    def cosine_similarity(self, movie_id_1, movie_id_2):
        """ Compute cosine distance between two movies in terms of genre, actors, directors, producers, overview. """
        movie_1 = self.master_movie_data["id"] == movie_id_1
        movie_2 = self.master_movie_data["id"] == movie_id_2
        # print(master_movie_data.loc[movie_1, "original_title"].iloc[0])
        # print(master_movie_data.loc[movie_2, "original_title"].iloc[0])

        one_hot_genre_1 = json.loads(self.master_movie_data.loc[movie_1, "one_hot_encoding_genres"].iloc[0])
        one_hot_genre_2 = json.loads(self.master_movie_data.loc[movie_2, "one_hot_encoding_genres"].iloc[0])
        genre_similarity = spatial.distance.cosine(one_hot_genre_1, one_hot_genre_2)

        one_hot_actors_1 = json.loads(self.master_movie_data.loc[movie_1, "one_hot_ecoding_actors"].iloc[0])
        one_hot_actors_2 = json.loads(self.master_movie_data.loc[movie_2, "one_hot_ecoding_actors"].iloc[0])
        actors_similarity = spatial.distance.cosine(one_hot_actors_1, one_hot_actors_2)

        one_hot_director_1 = json.loads(self.master_movie_data.loc[movie_1, "one_hot_encoding_director"].iloc[0])
        one_hot_director_2 = json.loads(self.master_movie_data.loc[movie_2, "one_hot_encoding_director"].iloc[0])
        directors_similarity = spatial.distance.cosine(one_hot_director_1, one_hot_director_2)

        one_hot_producer_1 = json.loads(self.master_movie_data.loc[movie_1, "one_hot_encoding_producer"].iloc[0])
        one_hot_producer_2 = json.loads(self.master_movie_data.loc[movie_2, "one_hot_encoding_producer"].iloc[0])
        producer_similarity = spatial.distance.cosine(one_hot_producer_1, one_hot_producer_2)

        one_hot_overview_1 = json.loads(self.master_movie_data.loc[movie_1, "one_hot_ecoding_overview"].iloc[0])
        one_hot_overview_2 = json.loads(self.master_movie_data.loc[movie_2, "one_hot_ecoding_overview"].iloc[0])
        overview_similarity = spatial.distance.cosine(one_hot_overview_1, one_hot_overview_2)

        return [genre_similarity, actors_similarity, directors_similarity, producer_similarity, overview_similarity]


    def get_genre_sim(lst):
        return lst[0]

def main():
    """ Main Driver. """
    pass


if __name__ == "__main__":
    main()
