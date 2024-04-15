import pandas as pd
from transformers import pipeline
import streamlit as st


class GenerateAnswer:
    def __init__(self):
        self.question_answerer = pipeline("question-answering", model="/Users/dianechiang/Library/CloudStorage/GoogleDrive-tchiang0@uw.edu/My Drive/qa_mod_2")
        self.movie_data = pd.read_csv("/Users/dianechiang/Desktop/personal_projects/Retrieval_Augmented_Generation_Exploration/Retrieval_Augmented_Generation_Exploration/data/Movie Data For RAG Training.csv")

    
    def answer_general(self, question_idx_list, movie_title):
        all_questions = ["What are the genres for the movie ", "Who's the director(s) for the movie ",
                             "Who's the producer(s) for the movie ", "What is the rating for the movie ",
                             "When's the release date for the movie ", "Who are the actors for the movie ",
                             "What is the overview for the movie "]
        context = self.movie_data.loc[self.movie_data["title"] == movie_title, "context"].iloc[0]
        answer_list = []
        for question_idx in question_idx_list:
            question = all_questions[question_idx] + movie_title
            answer = self.question_answerer(question=question, context=context)
            answer_list.append(answer['answer'])
        return answer_list
