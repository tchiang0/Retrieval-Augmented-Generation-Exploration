from transformers import RagTokenizer, RagTokenForGeneration, Trainer, TrainingArguments
from datasets import load_dataset, DatasetDict
# Assuming you have a dataset in CSV format
climate_change_dataset = load_dataset("csv", data_files={"train": "path/to/train.csv", "validation": "path/to/val.csv"})
# Example structure of each data point: {'query': 'What is climate change?', 'document': 'Climate change refers to...', 'answer': 'Climate change is...'}

tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq")

training_args = TrainingArguments(
    output_dir="./rag_finetuned/",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs/",
    logging_steps=10,
)
# Define a function to process the data for training
def preprocess_function(examples):
    inputs = [ex["query"] + tokenizer.sep_token + ex["document"] for ex in examples]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True)
    # Prepare labels
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["answer"], max_length=512, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Process the dataset
tokenized_datasets = climate_change_dataset.map(preprocess_function, batched=True)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
)
# Start fine-tuning
trainer.train()


# content generation
# from transformers import RagTokenizer, RagTokenForGeneration
# # Load the fine-tuned model and tokenizer
# model = RagTokenForGeneration.from_pretrained("./rag_finetuned/")
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
# # Generating content
# query = "Explain the impact of global warming on polar ice caps."
# input_ids = tokenizer(query, return_tensors="pt").input_ids
# # Generate the answer
# generated_ids = model.generate(input_ids)
# print(tokenizer.decode(generated_ids[0], skip_special_tokens=True))