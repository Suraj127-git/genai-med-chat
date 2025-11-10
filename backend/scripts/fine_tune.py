# backend/scripts/fine_tune_run.py
"""
Minimal LoRA/PEFT fine-tune script using Hugging Face Transformers + PEFT.

Requirements:
  pip install transformers datasets accelerate peft bitsandbytes
(note: bitsandbytes enables 8-bit training on CPU/GPU; adjust to your env)

This is a lightweight example. For large models or real medical data, follow strict compliance and validation.
"""
import os
from pathlib import Path
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_int8_training
import torch
import json

# Config — change model_name to a small model for local runs (eg. "gpt2" or "EleutherAI/gpt-neo-125M")
MODEL_NAME = os.getenv("BASE_MODEL", "gpt2")
OUTPUT_DIR = Path("backend/data/ft-model")
TRAIN_FILE = Path("backend/data/training_data.jsonl")  # exported jsonl from script above
EPOCHS = int(os.getenv("EPOCHS", 3))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 4))
LR = float(os.getenv("LR", 5e-5))
MAX_LENGTH = int(os.getenv("MAX_LENGTH", 256))

def prepare_dataset(tokenizer):
    # load jsonl as dataset
    ds = load_dataset("json", data_files=str(TRAIN_FILE))
    # build inputs -> usually combine prompt+completion into single text for causal LM
    def _map(ex):
        prompt = ex["prompt"]
        completion = ex["completion"]
        # create ful text: prompt + completion (you may use stop tokens)
        full = prompt + tokenizer.eos_token + completion + tokenizer.eos_token
        tokens = tokenizer(full, truncation=True, max_length=MAX_LENGTH)
        return {"input_ids": tokens["input_ids"], "attention_mask": tokens["attention_mask"]}
    ds = ds["train"].map(_map, remove_columns=ds["train"].column_names)
    return ds

def main():
    assert TRAIN_FILE.exists(), f"Training file not found: {TRAIN_FILE}. Run export_training_data.py first."

    print("Loading tokenizer and model:", MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    # For causal LM ensure pad_token is defined
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto")

    # Apply PEFT LoRA (example)
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],  # may vary per model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    try:
        # If model supports 8-bit and you have bitsandbytes, you can prepare for int8 training
        model = prepare_model_for_int8_training(model)
    except Exception:
        pass

    model = get_peft_model(model, lora_config)
    print("PEFT/LoRA model ready")

    ds = prepare_dataset(tokenizer)

    data_collator = DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt")

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=1,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        logging_steps=10,
        fp16=torch.cuda.is_available(),
        save_total_limit=2,
        remove_unused_columns=False,
        push_to_hub=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    trainer.train()
    model.save_pretrained(OUTPUT_DIR)
    print("Fine-tuned model saved to", OUTPUT_DIR)

if __name__ == "__main__":
    main()
