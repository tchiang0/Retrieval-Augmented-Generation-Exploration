""" Content Based Filtering (KNN). """
import pandas as pd
# import requests
import json
import ast
from scipy import spatial
# from config import API_KEY


class contentBasedFiltering():
    def __init__(self) -> None:
        pass


    def contains_metrics(self, full_metric_list, metric_to_be_contained):
        """ Check if name is contained in names_list. """
        return set(metric_to_be_contained).issubset(set(full_metric_list))


    def not_contain_metrics(self, full_metric_list, metric_not_to_be_contained):
        """ Check if metric is contained in full_metric_list. If so, return False. """
        for metric in metric_not_to_be_contained:
            if metric in full_metric_list:
                return False
        return True


    # can be changed to name if needed
    def cosine_similarity(self, df, movie_id_1, movie_id_2):
        """ Compute cosine distance between two movies in terms of genre, actors, directors, producers, overview. """
        movie_1 = df["id"] == movie_id_1
        movie_2 = df["id"] == movie_id_2

        one_hot_genre_1 = json.loads(df.loc[movie_1, "one_hot_encoding_genres"].iloc[0])
        one_hot_genre_2 = json.loads(df.loc[movie_2, "one_hot_encoding_genres"].iloc[0])
        genre_similarity = spatial.distance.cosine(one_hot_genre_1, one_hot_genre_2)

        one_hot_actors_1 = json.loads(df.loc[movie_1, "one_hot_ecoding_actors"].iloc[0])
        one_hot_actors_2 = json.loads(df.loc[movie_2, "one_hot_ecoding_actors"].iloc[0])
        actors_similarity = spatial.distance.cosine(one_hot_actors_1, one_hot_actors_2)

        one_hot_director_1 = json.loads(df.loc[movie_1, "one_hot_encoding_director"].iloc[0])
        one_hot_director_2 = json.loads(df.loc[movie_2, "one_hot_encoding_director"].iloc[0])
        directors_similarity = spatial.distance.cosine(one_hot_director_1, one_hot_director_2)

        one_hot_producer_1 = json.loads(df.loc[movie_1, "one_hot_encoding_producer"].iloc[0])
        one_hot_producer_2 = json.loads(df.loc[movie_2, "one_hot_encoding_producer"].iloc[0])
        producer_similarity = spatial.distance.cosine(one_hot_producer_1, one_hot_producer_2)

        one_hot_overview_1 = json.loads(df.loc[movie_1, "one_hot_encoding_overview"].iloc[0])
        one_hot_overview_2 = json.loads(df.loc[movie_2, "one_hot_encoding_overview"].iloc[0])
        overview_similarity = spatial.distance.cosine(one_hot_overview_1, one_hot_overview_2)

        return [genre_similarity, actors_similarity, directors_similarity, producer_similarity, overview_similarity]


    def get_genre_sim(self, lst):
        """ Get genre cosine distance. """
        return lst[0]


    def get_actors_sim(self, lst):
        """ Get actors cosine distance. """
        return lst[1]


    def get_directors_sim(self, lst):
        """ Get directors cosine distance. """
        return lst[2]


    def get_producer_sim(self, lst):
        """ Get producers cosine distance. """
        return lst[3]
    

    def get_overview_sim(self, lst):
        """ Get overview cosine distance. """
        return lst[4]


    def metric_specific_filtering(self, df, have_or_without, specific_metrics_dict):
        """ Filter movie df to including specific metrics. """
        filtered_df = df
        if isinstance(filtered_df['genre_names'].iloc[0], str):
            filtered_df['genre_names'] = filtered_df['genre_names'].apply(ast.literal_eval)
        if isinstance(filtered_df["actors"].iloc[0], str):
            filtered_df['actors'] = filtered_df['actors'].apply(ast.literal_eval)
        if isinstance(filtered_df["directors"].iloc[0], str):
            filtered_df['directors'] = filtered_df['directors'].apply(ast.literal_eval)
        if isinstance(filtered_df["producers"].iloc[0], str):
            filtered_df['producers'] = filtered_df['producers'].apply(ast.literal_eval)

        for metric_type, metric_list in specific_metrics_dict.items():
            if len(metric_list) > 0:
                if have_or_without == "contain":
                    if metric_type == "genres":
                        filtered_df = filtered_df[filtered_df['genre_names'].apply(lambda x: self.contains_metrics(x, metric_list))]
                    elif metric_type == "actors":
                        filtered_df = filtered_df[filtered_df['actors'].apply(lambda x: self.contains_metrics(x, metric_list))]
                    elif metric_type == "directors":
                        filtered_df = filtered_df[filtered_df['directors'].apply(lambda x: self.contains_metrics(x, metric_list))]
                    else:
                        filtered_df = filtered_df[filtered_df['producers'].apply(lambda x: self.contains_metrics(x, metric_list))]
                else:
                    if metric_type == "genres":
                        filtered_df = filtered_df[filtered_df['genre_names'].apply(lambda x: self.not_contain_metrics(x, metric_list))]
                    elif metric_type == "actors":
                        filtered_df = filtered_df[filtered_df['actors'].apply(lambda x: self.not_contain_metrics(x, metric_list))]
                    elif metric_type == "directors":
                        filtered_df = filtered_df[filtered_df['directors'].apply(lambda x: self.not_contain_metrics(x, metric_list))]
                    else:
                        filtered_df = filtered_df[filtered_df['producers'].apply(lambda x: self.not_contain_metrics(x, metric_list))]
        return filtered_df

    
    def populate_specific_metric_dict(self, genre, actors, directors, producers):
        metric_dict = {
            "genres": [],
            "actors": [],
            "directors": [],
            "producers": []
        }
        metric_dict["genres"] = genre
        metric_dict["actors"] = actors
        metric_dict["directors"] = directors
        metric_dict["producers"] = producers
        return metric_dict


def main(masterDf, movieID, movieName, genre=[], contain="contain", actors=[], directors=[], producers=[]):
    """ Main Driver. """
    content_filtering = contentBasedFiltering()
    specific_metric_dict = content_filtering.populate_specific_metric_dict(genre, actors, directors, producers)
    subset_movies = content_filtering.metric_specific_filtering(masterDf, contain, specific_metric_dict)
    if subset_movies.empty:
        return subset_movies
    movie_1_list = [movieID] * len(subset_movies)
    movie_1_name = [movieName] * len(subset_movies)
    data_df = {
            "Movie 1 ID": movie_1_list,
            "Movie 1 Name": movie_1_name,
            "Movie 2 ID": subset_movies["id"].to_list(),
            "Movie 2 Name": subset_movies["original_title"].to_list()
    }
    df = pd.DataFrame(data_df)
    df["cosine_sim_genre_actor_dir_prod_overview"] = df.apply(lambda row: content_filtering.cosine_similarity(subset_movies, row["Movie 1 ID"], row["Movie 2 ID"]), axis=1)
    return df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='What movie are you looking for?')
    parser.add_argument('--masterDf', metavar='path', required=True,
                        help='the full movie dataset')
    parser.add_argument('--movieID', metavar='path', required=True,
                        help='the movie ID you are looking to associate with')
    parser.add_argument('--movieName', metavar='path', required=True,
                        help='the movie name you are looking to associate with')
    parser.add_argument('--contain', metavar='path', required=False, default="contain",
                        help='Look for the movies that include the genre, actors, directors, producers')
    parser.add_argument('--genre', metavar='path', required=False, default=[],
                        help='movie genre')
    parser.add_argument('--actors', metavar='path', required=False, default=[],
                        help='movie actors')
    parser.add_argument('--directors', metavar='path', required=False, default=[],
                        help='movie directors')
    parser.add_argument('--producers', metavar='path', required=False, default=[],
                        help='movie producers')
    args = parser.parse_args()
    main(masterDf=args.masterDf, movieID=args.movieID, movieName=args.movieName, genre=args.genre,
         contain=args.contain,actors=args.actors, directors=args.directors, producers=args.producers)
