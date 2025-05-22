import json
import pandas as pd # type: ignore
import csv
import re
import chardet # type: ignore

def clean_jsonl_chat_data(filepath, output_file, errors='replace'):
    """Cleans JSONL chat data, linking responses based on reply-to."""
    try:
        # 1. Detect Encoding:
        with open(filepath, 'rb') as ef:
            rawdata = ef.read()
        result = chardet.detect(rawdata)
        encoding = result['encoding']
        print(f"Detected encoding: {encoding}")

        data = []
        utterances = {}  # Store utterances by ID for linking responses

        with open(filepath, 'r', encoding=encoding, errors=errors) as f:
            for line in f:
                try:
                    json_obj = json.loads(line)
                    text = json_obj.get('text', '')
                    text = re.sub(r'\n+', ' ', text).strip()

                    if not text or text == "[deleted]":
                        print(f"Warning: Skipping empty, deleted, or invalid text: {line.strip()}")
                        continue  # Skip to the next line

                    utterance_id = json_obj['id']
                    reply_to = json_obj.get('reply-to')
                    
                    utterances[utterance_id] = {  # Store for later linking
                        "context": text,
                        "response": "",
                    }

                    if reply_to and reply_to in utterances:
                        utterances[reply_to]["response"] = text


                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON: {line.strip()}. Error: {e}")


        if not utterances: # If the 'utterances' is empty after reading the file it gives a dataframe with no data.
             print("Error: No valid data. Creating empty DataFrame.")
             df = pd.DataFrame(columns=["context", "response"]) # Create Empty Dataframe with the specified columns.
        else:
             data = list(utterances.values()) # Convert dictionary to list of dictionaries
             df = pd.DataFrame(data)

        df['original_index'] = df.index  # Create a column to preserve original order
        df = df.sort_values('original_index')
        df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, lineterminator="\n", encoding='utf-8')
        print(f"✅ Saved cleaned data to '{output_file}'")

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()



clean_jsonl_chat_data("conversations-gone-awry-cmv-corpus/utterances.jsonl", "cleaned_convogone_jsonl_data.csv")