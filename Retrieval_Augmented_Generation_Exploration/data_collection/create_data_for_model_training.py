""" Create data for RAG model training; data grathered from web_scraping. """
import pandas as pd
import json
import ast
import string


class createMetaData():
    def __init__(self):
        self.queries = [
            "What is the movie title for the movie ",
            "What is the overview for the movie ",
            "What is the rating for the movie ",
            "When's the release date for the movie ",
            "What are the genres for the movie ",
            "Who are the actors for the movie ",
            "Who's the director(s) for the movie ",
            "Who's the producer(s) for the movie "
        ]


    def make_movie_meta_data(self, movie_id, df, movie_info):
        """ Make movie meta data dictionary. """
        meta_dict = {}
        row = df.loc[df["id"] == int(movie_id)]
        meta_dict["movie title"] = row["original_title"].iloc[0]
        meta_dict["overview"] = str(row["overview"].iloc[0])
        meta_dict["info"] = movie_info["movie_info"]
        meta_dict["ratings"] = movie_info["movie_rating"]
        meta_dict["release date"] = row["release_date"].iloc[0]
        meta_dict["genre names"] = ast.literal_eval(row["genre_names"].iloc[0])
        meta_dict["actors"] = ast.literal_eval(row["actors"].iloc[0])
        meta_dict["directors"] = ast.literal_eval(row["directors"].iloc[0])
        meta_dict["producers"] = ast.literal_eval(row["producers"].iloc[0])
        return meta_dict

    
    def create_document(self, movie_meta_dict):
        """ Create document (movie context). """
        movie_title = movie_meta_dict["movie title"]
        doc_str = f"{movie_title}, "
        # directors
        dir_list = movie_meta_dict["directors"]
        if dir_list:
            if len(dir_list) == 1:
                director_str = dir_list[0]
            elif len(dir_list) == 2:
                director_str = ' and '.join(dir_list)
            else:
                director_str = ', '.join(dir_list[:-1]) + ', and ' + dir_list[-1]
            doc_str += f"directed by {director_str} "

        # producers
        prod_list = movie_meta_dict["producers"]
        if prod_list:
            if len(prod_list) == 1:
                prod_str = prod_list[0]
            elif len(prod_list) == 2:
                prod_str = ' and '.join(prod_list)
            else:
                prod_str = ', '.join(prod_list[:2]) + ', and ' + prod_list[2]
            doc_str += f"and produced by {prod_str}, "
        else:
            doc_str += ", "

        release_date = movie_meta_dict["release date"]
        doc_str += f"is released on {release_date}. "

        # actors
        actors_list = movie_meta_dict["actors"]
        if actors_list:
            if len(actors_list) == 1:
                actor_str = actors_list[0]
            elif len(actors_list) == 2:
                actor_str = ' and '.join(actors_list)
            else:
                actor_str = ', '.join(actors_list[:2]) + ', and ' + actors_list[2]
            doc_str += f"Some actors of the {movie_title} includes: {actor_str}. "

        # rating
        rating = movie_meta_dict["ratings"]
        if rating:
            doc_str += f"The movie is rated as {rating[0]}. "

        # genre
        genre_names = movie_meta_dict["genre names"]
        if genre_names:
            if len(genre_names) == 1:
                genre_str = genre_names[0]
            elif len(genre_names) == 2:
                genre_str = ' and '.join(genre_names)
            else:
                genre_str = ', '.join(genre_names[:-1]) + ', and ' + genre_names[-1]
            doc_str += f", and the movie's genre is {genre_str}. "
        else:
            doc_str += ". "

        # overview
        overview = movie_meta_dict["overview"]
        if overview != "nan":
            lower_overview = overview[:1].lower() + overview[1:]
            doc_str += f"The overview of the movie is that {lower_overview}"
            if doc_str[-1] not in string.punctuation:
                doc_str += "."
            doc_str += " "
        else:
            # info
            info = movie_meta_dict["info"]
            if info:
                info_str = info[0]
                lower_info = info_str[:1].lower() + info_str[1:]
                doc_str += f"The overview of the movie is that {lower_info}"
        return doc_str


    def create_queries(self, movie_title, director, release_date):
        """ Create queries for training. """
        movie_title_str = movie_title + "?"
        custom_queries = []
        for q in self.queries:
            q_str = q + movie_title_str
            custom_queries.append(q_str)
        return custom_queries


    def create_answers(self, movie_meta_dict):
        answers = []
        has_overview = False
        for metric, val in movie_meta_dict.items():
            if metric == "overview" and val != "":
                has_overview = True
            if metric == 'info' and has_overview:
                continue
            val_str = ""
            if isinstance(val, list):
                if val:
                    val = [v.strip() for v in val]
                    if len(val) == 1:
                        val_str = val[0]
                    elif len(val) == 2:
                        val_str = val[0] + ' and ' + val[1]
                    else:
                        if metric == "genre names":
                            val_str = ', '.join(val[:-1]) + ', and ' + val[-1]
                        else:
                            val_str = ', '.join(val[:2]) + ', and ' + val[2]
                else:
                    val_str = "Unknown."
            else:
                val_str = str(val)
            answers.append(val_str)
        return answers


    def create_answer_idx(self, movie_doc, answers_list):
        idx_list = []
        for answer in answers_list:
            start_idx = movie_doc.find(answer)
            end_idx = -1
            if start_idx != -1:
                end_idx = start_idx + len(answer)
                idx_list.append((start_idx, end_idx))
            else:
                answer_lowered = answer[:1].lower() + answer[1:]
                start_idx = movie_doc.find(answer_lowered)
                if start_idx != -1:
                    end_idx = start_idx + len(answer_lowered)
                    idx_list.append((start_idx, end_idx))
                else:
                    idx_list.append((-1, -1))
        return idx_list


    def format_answer_data(self, answers_list, idx_list):
        # 'answers': {'text': ['Kazimierz Palace'], 'answer_start': [137]}}
        data_list = []
        for i in range(len(answers_list)):
            data_format = {
                "answer_idx": [],
                "text": []
            }
            data_format["answer_idx"] = idx_list[i]
            data_format["text"] = answers_list[i]
            data_list.append(json.dumps(data_format))
        return data_list


    def load_progress(self, filename):
        """ Load movie json. """
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None


def main(df):
    """ Main Driver. """
    custom_df = pd.DataFrame()
    create_meta = createMetaData()
    progress_1 = create_meta.load_progress('progress_movie_id.json')
    progress_2 = create_meta.load_progress('progress_movie_id_2.json')
    for movie_id, movie_info in progress_1["movie_info_and_rating"].items():
        temp_df = pd.DataFrame()
        movie_info = progress_1["movie_info_and_rating"][movie_id]

        # check if progress_ver_3 has the info; if not, it's okay
        if not movie_info["movie_info"] and not movie_info["movie_rating"]:
            if movie_id in progress_2["processed_ids"]:
                movie_info = progress_2["movie_info_and_rating"][movie_id]
        director_list = df.loc[df["id"] == int(movie_id), "directors"].iloc[0]
        if isinstance(director_list, str):
            director_list = ast.literal_eval(director_list)
            if len(director_list):
                if len(director_list) == 1:
                    director = director_list[0]
                elif len(director_list) == 2:
                    director = director_list[0] + ' and ' + director_list[-1]
                else:
                    director = ', '.join(director_list[:-1]) + ', and ' + director_list[-1]
            else:
                director = ""
        release_date = df.loc[df["id"] == int(movie_id), "release_date"].iloc[0]
        if not release_date:
            release_date = ""
        movie_title = df.loc[df["id"] == int(movie_id), "original_title"].iloc[0]

        movie_meta_dict = create_meta.make_movie_meta_data(movie_id, df, movie_info)
        document_str = create_meta.create_document(movie_meta_dict)
        query_list = create_meta.create_queries(movie_title)
        answer_list = create_meta.create_answers(movie_meta_dict)
        answer_idx_pair_list = create_meta.create_answer_idx(document_str, answer_list)
        data_format_list = create_meta.format_answer_data(answer_list, answer_idx_pair_list)
        temp_df["id"] = [movie_id] * len(answer_list)
        temp_df["title"] = [movie_title] * len(answer_list)
        temp_df["context"] = [document_str] * len(answer_list)
        temp_df["question"] = query_list
        temp_df["answers"] = data_format_list
        custom_df = pd.concat([custom_df, temp_df])
    return custom_df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='What movie are you looking for?')
    parser.add_argument('--df', metavar='path', required=True,
                        help='The movie dataset with duplicates and movies-without-release-date removed')
    args = parser.parse_args()
    main(df=args.df)
