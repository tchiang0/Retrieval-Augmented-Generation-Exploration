""" Question Answer Model Training (Run on Google Colab). """
# !pip install faiss-cpu
# !pip install faiss-gpu
# !pip install transformers datasets evaluate
# !pip install transformers[torch]
# !pip install accelerate -U
# !pip install huggingface_hub
# !python -c "from huggingface_hub.hf_api import HfFolder; HfFolder.save_token('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')"

from transformers import AutoTokenizer, DefaultDataCollator, AutoModelForQuestionAnswering, TrainingArguments, Trainer
from transformers import pipeline
from datasets import load_dataset
import json


class qaTraining():
    def __init__(self):
        self.movie_dataset = load_dataset("csv",data_files={"train": "/Users/dianechiang/Desktop/personal_projects/Retrieval_Augmented_Generation_Exploration/Retrieval_Augmented_Generation_Exploration/data/train/train.csv",
                                                            "validation": "/Users/dianechiang/Desktop/personal_projects/Retrieval_Augmented_Generation_Exploration/Retrieval_Augmented_Generation_Exploration/data/validation/val.csv"})
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")


    def __preprocess_function__(self, examples):
        """ Preprocess  data to feed into qa model. """
        questions = [q.strip() for q in examples["question"]]
        inputs = self.tokenizer(
            questions,
            examples["context"],
            max_length=512,
            truncation="only_second",
            return_offsets_mapping=True,
            padding="max_length",
        )

        offset_mapping = inputs.pop("offset_mapping")
        answers = examples["answers"]
        start_positions = []
        end_positions = []

        for i, offset in enumerate(offset_mapping):
            answer = json.loads(answers[i])
            start_char = answer["answer_idx"][0]
            end_char = answer["answer_idx"][1]
            sequence_ids = inputs.sequence_ids(i)

            # Find the start and end of the context
            idx = 0
            while sequence_ids[idx] != 1:
                idx += 1
            context_start = idx
            while sequence_ids[idx] == 1:
                idx += 1
            context_end = idx - 1

            # If the answer is not fully inside the context, label it (0, 0)
            if offset[context_start][0] > end_char or offset[context_end][1] < start_char:
                start_positions.append(0)
                end_positions.append(0)
            else:
                # Otherwise it's the start and end token positions
                idx = context_start
                while idx <= context_end and offset[idx][0] <= start_char:
                    idx += 1
                start_positions.append(idx - 1)

                idx = context_end
                while idx >= context_start and offset[idx][1] >= end_char:
                    idx -= 1
                end_positions.append(idx + 1)

        inputs["start_positions"] = start_positions
        inputs["end_positions"] = end_positions
        return inputs


    def qa_training(self):
        """ Fine tune distilbert model. """
        tokenized_movie = self.movie_dataset.map(self.__preprocess_function__,
                                                 batched=True,
                                                 remove_columns=self.movie_dataset["train"].column_names)
        data_collator = DefaultDataCollator()
        model = AutoModelForQuestionAnswering.from_pretrained("distilbert/distilbert-base-uncased")

        training_args = TrainingArguments(
            output_dir="qa_mod",
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=8,
            weight_decay=0.01,
            push_to_hub=True,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_movie["train"],
            eval_dataset=tokenized_movie["validation"],
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )
        trainer.train()


def main(question, context):
    """ Main Driver. """
    qa_training = qaTraining()
    qa_training.qa_training()
    question_answerer = pipeline("question-answering", model="qa_mod")
    # {'score': 1.0987860150635242e-06, 'start': 310, 'end': 311, 'answer': ')'}
    answer_dict = question_answerer(question=question, context=context)
    response = answer_dict['answer']
    return response


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='qa training')
    parser.add_argument('--question', metavar='path', required=True,
                        help='The question you want to ask about the movie')
    parser.add_argument('--context', metavar='path', required=True,
                        help='The context of the movie')
    args = parser.parse_args()
    main(question=args.question, context=args.context)

# question = "What is the rating for the movie Poor Thing?"
# context =  "Poor Things, directed by Yorgos Lanthimos and produced by David Minkowski, Andrew Lowe, and Ed Guiney,\
#     is released on 2023-12-07. Some actors of the Poor Things includes: Emma Stone, Mark Ruffalo, and Willem Dafoe.\
#     The movie is rated as R (Gore|Disturbing Material|Graphic Nudity|Language|Strong Sexual Content), \
#     and the movie's genre is Science Fiction, Romance, and Comedy. The overview of the movie is that brought\
#     back to life by an unorthodox scientist, a young woman runs off with a debauched lawyer on a whirlwind\
#     adventure across the continents. Free from the prejudices of her times, she grows steadfast in her\
#     purpose to stand for equality and liberation."
