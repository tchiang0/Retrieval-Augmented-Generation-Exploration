import streamlit as st


class movieChat():
    def __init__(self):
        if 'recommender_button' not in st.session_state:
            st.session_state.recommender_button = False
        if 'background_button' not in st.session_state:
            st.session_state.background_button = False


    # Streamed response emulator
    def button_click_response_generator(self, res_type):
        """ Generate valid bot response given valid input. """
        for key in st.session_state.keys():
            if key != 'messages':
                del st.session_state[key]
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


    def gather_necessary_movie_detail(self):
        if st.session_state.recommender_button:
            with st.form(key="fav_movie_form", clear_on_submit=True):
                movie_titles = st.multiselect(label='What is/are your favorite movie(s)?',
                                              key="movie_titles",
                                              options=['Any', 'Atomic Blonde', 'Kung Fu Panda 4', 'Avengers 3'],
                                              default=["Any"])
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

        # Handle the selection from "Recommend me movies!!"
        if 'selected_prompt' in locals():
            if selected_prompt == "Recommend me movies!!":
                if not st.session_state.recommender_button:
                    response = self.button_click_response_generator(selected_prompt)
            else:
                if not st.session_state.background_button:
                    response = self.button_click_response_generator(selected_prompt)

            st.session_state.messages.append({"role": "user", "content": selected_prompt})
            with st.chat_message("user"):
                st.markdown(selected_prompt, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)


        # Accept user input after a button is pushed
        if st.session_state.recommender_button and ('form_submitted' not in st.session_state or st.session_state.form_submitted == False):
            self.gather_necessary_movie_detail()
            # st.session_state.movie_meta pass into content_based_filtering
            
            # Add user message to chat history
            # st.session_state.messages.append({"role": "user", "content": prompt})
            # # Display user message in chat message container
            # with st.chat_message("user"):
            #     st.markdown(prompt)

            # # Display assistant response in chat message container
            # with st.chat_message("assistant"):
            #     response = st.write_stream(self.response_generator())
            # # Add assistant response to chat history
            # st.session_state.messages.append({"role": "assistant", "content": response})

        for key in st.session_state.keys():
            print(f"{key} has {st.session_state[key]}")

if __name__ == "__main__":
    infobot_page = movieChat()
    infobot_page.render_movie_chatbot()
# if prompt := st.chat_input("Please select either of the two buttons to start!!!"):
