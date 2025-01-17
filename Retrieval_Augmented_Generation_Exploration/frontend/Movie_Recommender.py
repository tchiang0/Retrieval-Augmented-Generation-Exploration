""" Movie Recommender Know-It-All Chatbot. """
import pandas as pd
import streamlit as st
from Retrieval_Augmented_Generation_Exploration.content_based_filtering import content_based_filtering as cbf
from Retrieval_Augmented_Generation_Exploration.data_collection import data_collection as dc
from Retrieval_Augmented_Generation_Exploration.model.question_answer import GenerateAnswer as ga


# set web title and icon
st.set_page_config(page_title="Movie Recommender Info Bot", page_icon="🍿")

@st.cache_data
def fetch_and_clean_movie_data(in_place_str):
    """ Cache meta movie dataframe to avoid rerun on re-render. """
    movie_data = pd.read_csv("Retrieval_Augmented_Generation_Exploration/Master Movie Dataset.csv")
    movie_data.rename(columns={'one_hot_ecoding_overview': 'one_hot_encoding_overview'}, inplace=True)
    return movie_data


class movieChat():
    def __init__(self):
        if 'movie_df' not in st.session_state:
            st.session_state.movie_df = fetch_and_clean_movie_data(in_place_str="data_collection")
        # self.content_based_filtering = cbf()
        if 'recommender_button' not in st.session_state:
            st.session_state.recommender_button = False
        if 'background_button' not in st.session_state:
            st.session_state.background_button = False


    def print_save_chat_message(self, party, response):
        """ Generate chat message from assistant and user. """
        with st.chat_message(party):
            st.markdown(response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": party, "content": response})


    def button_click_response_generator(self, res_type):
        """ Generate valid bot response given valid input. """
        for key in st.session_state.keys():
            if key != 'messages':
                del st.session_state[key]
        if "recommender_button" not in st.session_state:
            st.session_state.recommender_button = False
        if "background_button" not in st.session_state:
            st.session_state.background_button = False
        valid_button_vals = ["Recommend me movies!!", "Movie Background Know-It-All"]
        if not isinstance(res_type, str):
            raise TypeError("[Wrong response type] response should be a string")
        if res_type not in valid_button_vals:
            raise ValueError("[Wrong response]: should choose one of the valid buttons")
        recommender_res = "You selected the Movie Recommender!"
        background_res = "You selected the Movie Know-It-All to learn about a specific movie's background!"
        if res_type == "Recommend me movies!!":
            response = recommender_res
            st.session_state.recommender_button = True
            st.session_state.background_button = False
        else:
            response = background_res
            st.session_state.recommender_button = False
            st.session_state.background_button = True
        return response


    def handle_fav_movie_detail(self):
        """ Handle favorite movie form submitted. """
        if 'movie_meta' not in st.session_state:
            st.session_state.movie_meta = {
                "titles": [],
                "genres": [],
                "actors": [], 
                "directors": [],
                "producers": []
            }
        st.session_state.movie_meta['titles'] = st.session_state.movie_titles
        st.session_state.movie_meta['genres'] = st.session_state.movie_genres
        st.session_state.movie_meta['actors'] = st.session_state.movie_actors
        st.session_state.movie_meta['directors'] = st.session_state.movie_directors
        st.session_state.movie_meta['producers'] = st.session_state.movie_producers
        if 'form_submitted' not in st.session_state:
            st.session_state.form_submitted = True


    def handle_movie_background_select(self):
        """ Handle interested movie selection. """
        if 'movie_interested_form_submitted' not in st.session_state:
            st.session_state.movie_interested_form_submitted = True


    def gather_necessary_movie_detail(self):
        """ Render favorite movie form and gather user input. """
        if st.session_state.recommender_button:
            with st.form(key="fav_movie_form", clear_on_submit=True):
                movie_titles = st.selectbox(label='What is your favorite movie?',
                                            key="movie_titles",
                                            options=['Any', 'Atomic Blonde', 'Kung Fu Panda 4', 'Avengers 3'])
                movie_genres = st.multiselect(label='What is/are some must have genre(s)?',
                                              key="movie_genres",
                                              options=['Any', 'Action', 'Family', 'Comedy'],
                                              default=["Any"])
                movie_actors = st.multiselect(label='Who is/are some must have actor(s)',
                                              key="movie_actors",
                                              options=['Any', 'Robert Downey Jr.', 'Charlize Theron', 'Jack Black'],
                                              default=["Any"])
                movie_directors = st.multiselect(label="Who is/are the directors you want to specifically looking for?",
                                                 key="movie_directors",
                                                 options=['Any', 'Martin Scorsese', 'Steven Spielberg', 'David Lynch'],
                                                 default=["Any"])
                movie_producers = st.multiselect(label="Who is/are the producer(s) you are specifically looking for?",
                                                 key="movie_producers",
                                                 options=['Any', 'Kathleen Kennedy', 'Kevin Feige', 'Jason Blum'],
                                                 default=['Any'])
                st.form_submit_button(label='submit', on_click=self.handle_fav_movie_detail)


    def get_recommended_movies(self):
        """ Get recommended movie from content based filtering (KNN). """
        movie_ids = st.session_state.movie_df.loc[st.session_state.movie_df["original_title"] == st.session_state.movie_meta['titles'],
                                                  "id"].tolist()
        response = f"We found {len(movie_ids)} movies under the title {st.session_state.movie_meta['titles']}"
        self.print_save_chat_message("assistant", response)
        for idx in movie_ids:
            temp_df = cbf.main(masterDf=st.session_state.movie_df,
                                movieID=int(idx),
                                movieName=st.session_state.movie_meta['titles'],
                                genre=st.session_state.movie_meta['genres'],
                                actors=st.session_state.movie_meta['actors'],
                                directors=st.session_state.movie_meta['directors'],
                                producers=st.session_state.movie_meta['producers'])
            if 'sim_movie_df' not in st.session_state:
                st.session_state.sim_movie_df = pd.DataFrame()
            if st.session_state.sim_movie_df.empty:
                st.session_state.sim_movie_df = temp_df
            else:
                movie_ids_in_sim_movie_df = st.session_state.sim_movie_df['Movie 1 ID'].unique().tolist()
                if idx not in movie_ids_in_sim_movie_df:
                    st.session_state.sim_movie_df = pd.concat([st.session_state.sim_movie_df, temp_df])


    def get_top_3_movies_all_metrics(self):
        """ Return top 3 recommended movies based on all metric (sum of cosine distance). """
        if len(st.session_state.movie_meta['genres']) == 1:
            genre_str = st.session_state.movie_meta['genres'][0]
        elif len(st.session_state.movie_meta['genres']) == 2:
            genre_str = st.session_state.movie_meta['genres'][0] + ' and ' + st.session_state.movie_meta['genres'][0]
        else:
            genre_str = ', '.join(st.session_state.movie_meta['genres'][:-1]) + ', and ' + st.session_state.movie_meta['genres'][-1]
        response = f"Out of all the movies with {genre_str} genre(s), Here are the top 3 movies most related by the overall metrics: "
        st.session_state.sim_movie_df['sum_of_values'] = st.session_state.sim_movie_df['cosine_sim_genre_actor_dir_prod_overview'].apply(sum)
        df_sorted = st.session_state.sim_movie_df.sort_values(by='sum_of_values')
        df_sorted = df_sorted.drop(columns=['sum_of_values'])
        sort_by_sum_title = df_sorted["Movie 2 Name"].tolist()[:4]
        title_str = ', '.join(sort_by_sum_title[1:-1]) + ', and ' + sort_by_sum_title[-1]
        response += f"{title_str}"
        return response


    def get_top_3_movies_user_metric(self, metric):
        """ Return top 3 recommended movies based on user input metrics (genre, actor, director, and/or producer). """
        if metric[-1] == 's':
            metric = metric[:-1]
        if metric == "genre":
            df_sorted = st.session_state.sim_movie_df.iloc[st.session_state.sim_movie_df['cosine_sim_genre_actor_dir_prod_overview'].map(lambda x: x[0]).argsort()]
        elif metric == "actor":
            df_sorted = st.session_state.sim_movie_df.iloc[st.session_state.sim_movie_df['cosine_sim_genre_actor_dir_prod_overview'].map(lambda x: x[1]).argsort()]
        elif metric == "director":
            df_sorted = st.session_state.sim_movie_df.iloc[st.session_state.sim_movie_df['cosine_sim_genre_actor_dir_prod_overview'].map(lambda x: x[2]).argsort()]
        else:
            df_sorted = st.session_state.sim_movie_df.iloc[st.session_state.sim_movie_df['cosine_sim_genre_actor_dir_prod_overview'].map(lambda x: x[3]).argsort()]
        sort_by_met_title = df_sorted["Movie 2 Name"].tolist()[:4]
        title_str = ', '.join(sort_by_met_title[1:-1]) + ', and ' + sort_by_met_title[-1]
        return title_str


    def get_answers(self, all_questions):
        """ Given the movie title and questions, generate answers using trained distilBERT qa model. """
        question_answering_mod = ga()
        indices = [all_questions.index(item) for item in st.session_state.movie_questions]
        answer_list = question_answering_mod.answer_general(indices, st.session_state.movie_of_interest)
        answer_idx = 0
        res_list = []
        for idx in indices:
            response = ""
            if idx == 0:
                response = f"The genre of {st.session_state.movie_of_interest} is/are {answer_list[answer_idx]}."
            elif idx == 1:
                response = f"The director(s) of {st.session_state.movie_of_interest} is/are {answer_list[answer_idx]}."
            elif idx == 2:
                response = f"The producer(s) of {st.session_state.movie_of_interest} is/are {answer_list[answer_idx]}."
            elif idx == 3:
                response = f"The rating of {st.session_state.movie_of_interest} is {answer_list[answer_idx]}."
            elif idx == 4:
                response = f"The release date of {st.session_state.movie_of_interest} is {answer_list[answer_idx]}."
            elif idx == 5:
                response = f"Some actors that starred in {st.session_state.movie_of_interest} is/are {answer_list[answer_idx]}."
            else:
                response = f"The overview of the {st.session_state.movie_of_interest} is: {answer_list[answer_idx]}"
            res_list.append(response)
            answer_idx += 1
        return res_list


    def render_movie_chatbot(self):
        """ Renders Infobot interface. """
        st.title("Movie ChatBot")
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # Display buttons for predefined prompts
        col1, _, col2 =  st.columns((8, 5, 12))
        with col1:
            if st.button("Recommend me movies!!"):
                selected_prompt = "Recommend me movies!!"
        with col2:
            if st.button("Movie Background Know-It-All"):
                selected_prompt = "Movie Background Know-It-All"

        # Handle the button selection
        if 'selected_prompt' in locals():
            if selected_prompt == "Recommend me movies!!":
                response = self.button_click_response_generator(selected_prompt)
            else:
                response = self.button_click_response_generator(selected_prompt)
            self.print_save_chat_message("user", selected_prompt)
            self.print_save_chat_message("assistant", response)

        if st.session_state.recommender_button and ('form_submitted' not in st.session_state or st.session_state.form_submitted == False):
            self.gather_necessary_movie_detail()

        if "movie_meta" in st.session_state and "refine_rec" not in st.session_state:
            self.get_recommended_movies()
            if st.session_state.sim_movie_df.empty:
                response = "There are no movies based on your chosen genres, actors, directors, and producers collection.\
                    Please try again with other selections. (For example, instead of selecting all genres, try selecting 'Any'!)"
            else:
                response = self.get_top_3_movies_all_metrics()
            self.print_save_chat_message("assistant", response)
            if 'refine_rec' not in st.session_state:
                st.session_state.refine_rec = True

        if 'refine_rec' in st.session_state:
            response = "Do you want a more refined recommendation? For example, do you want know the most similar movies by genres? By actors? By directors? Or by producers?"
            self.print_save_chat_message("assistant", response)
            if prompt := st.chat_input("Please let me know what metrics to recommend by. (Ex, genre actor director producer)"):
                self.print_save_chat_message("user", prompt)
                met_list = prompt.split()
                for met in met_list:
                    title_str = self.get_top_3_movies_user_metric(met)
                    response = f"Recommending by the most similar {met}, here are the top 3 movies: {title_str}"
                    self.print_save_chat_message("assistant", response)
            del st.session_state['refine_rec']
            prompt_know_it_all_click = "To learn more about a specific movie, click the **Movie Background Know-It-All** Button!"
            self.print_save_chat_message("assistant", prompt_know_it_all_click) 

        # Prompt user to click on the Movie Know It All button and remind them to remember the movie title
        if st.session_state.background_button:
            all_questions = ["What is the genre?", "Who is/are the director(s)?",
                             "Who is/are the producer(s)?", "What is the rating?",
                             "When is/was the release date?", "Who are some of the actors?",
                             "Give me an overview of the movie!"]
            if "movie_interested_form_submitted" not in st.session_state or not st.session_state.movie_interested_form_submitted:
                with st.form(key="movie_of_interest", clear_on_submit=True):
                    movie_of_interest = st.selectbox(label="Please let me know which movie you are interested in!",
                                                    key="movie_of_interest",
                                                    options=["Kung Fu Panda 4", "Poor Things", "Atomic Blonde", "Legacy"])
                    movie_related_questions =  st.multiselect(label='What are some questions you have about the movie?',
                                                                key="movie_questions",
                                                                options=all_questions,
                                                                default=["What is the genre?"])
                    st.form_submit_button(label='submit', on_click=self.handle_movie_background_select)
            else:
                response = f"The title of the movie you're interested in is {st.session_state.movie_of_interest}."
                response += f"\n Here are the questions you are interested in {st.session_state.movie_questions}"
                res_list = self.get_answers(all_questions)
                for res in res_list:
                    self.print_save_chat_message("assistant", res)
                response = "If you want to know more about this movie or others, or get other movie recommendations, please click the buttons above!!"
                self.print_save_chat_message("assistant", response)


        for key in st.session_state.keys():
            print(f"{key} has {st.session_state[key]}")



        

if __name__ == "__main__":
    infobot_page = movieChat()
    infobot_page.render_movie_chatbot()
