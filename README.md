# Movie Recommendation and Introduction ChatBot
> Outline a brief description of your project.
> Live demo [_here_](Movie_demo.mov). <!-- If you have the project hosted somewhere, include the link here. -->

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
This project aims to enhance the movie-watching experience by solving two main problems: finding personalized movie recommendations and providing accurate answers to movie-related questions. 

- **Problem Solved**: Addresses the challenge of discovering movies that align with individual preferences and providing reliable movie information on demand.

- **Purpose**: Recommend movies tailored to users' tastes based on genres, directors, producers, and actors they like and want to have included in the recommended movies. The chatbot also assists the users by answering specific questions about movies, such as details about cast and crew.

- **Motivation**: The project was undertaken out of a fasicination with Large Language Models (LLM), combined with a personal love for movies. The aim is to leverage these technolgies to create a useful and engaging tool for movies enthusiasts such as myself.


## Technologies Used
- Python 3.11
- HuggingFace Transformers: Utilized DistilBERT (distilbert/distilbert-base-uncased)
- Streamlit: Movie-Konw-It-All Interface


## Features
List the ready features here:
- **Personalized Movie Recommendations**: Based on users' favorite genres, directors, producers, and actors, the chatbot recommends the top three movies

- **Individual Attribute Based Movie Recommedations**: Users can specify the most important metric they are interested in, for example, want the movies recommendation to be closest in genre similarites, the chatbot will recommend three movies most similar in terms of genre while considering other attributes.

- **Movie Question-Answering**: Users can ask specific questions about movies, such as "Who is the director of the movie Poor Thing?" and get accurate answers.


## Setup
### Requirements
The project dependencies are listed in `requirements.txt`. To set up the local environment, please follow these steps:

1. Clone the repository:
```
git clone https://github.com/tchiang0/Retrieval_Augmented_Generation_Exploration.git
```

2. Create a virtual environent and activate it:
```
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies
```
pip install -r requirements.txt
```

### Enviroment
Ensure you have the required environment variables set up for the HuggingFace API keys if necessary.


## Usage
### Running the application
To start the chatbot, run the following command at the root directory
```
python3 -m streamlit run 
Retrieval_Augmented_Generation_Exploration/frontend/Movie_Recommender.py 
```

### Example Usage
#### Recommend me movies!!
1. Users can select the `Recommend me movies!!` button to prompt a dropdown menu and select their favorite movies, must have genres, actors, directors, and producers. Leaving theses blank would signify to the chatbot that the users are looking for any movies.

2. Users will then get three movies recommended based on the inputted attributes. They can then input in the prompt field either `genre`, `actor`, `director`, or `producer` to have the movie recommendation consider either one (or more) of these attributes first (ex. most similar movies by genre).

3. Select the `Recommend me movies!!` button to get new recommendations, input in the prompt field to get more tailored recommendations, or select `Movie Background Know-It-All` to learn more about a particular movie.

#### Movie Background Know-It-All
1. After selecting the `Movie Background Know-It-All` button, users are prompt to select their movie of interest and what questions they have about the movies. Right now, the chatbot only supports 7 questions, which I plan to expand in the future. 


## Room for Improvement
Room for improvement:
- Improve user interface for a more engaing experience
- Enhance QA model to increase accuracy with answering movie related questions


## Acknowledgements
- This project was inspired by needing to find a movie to watch.
- This question ans answering model training was based on [this Hugging Face tutorial](https://huggingface.co/docs/transformers/tasks/question_answering).