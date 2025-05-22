import json
import re

def clean_jsonl_file(input_filepath, output_filepath):
    """Cleans a JSONL file with nested JSON and saves to JSONL."""
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            with open(input_filepath, 'r', encoding='utf-8') as infile:
                for line in infile:  # Process each line individually
                    cleaned_row = clean_json_data(line) # Call this for every line in the jsonl file.
                    if cleaned_row:
                        output_json = {
                            "context": cleaned_row["context"],
                            "response": cleaned_row["response"]
                        }
                        json.dump(output_json, outfile, ensure_ascii=False)
                        outfile.write('\n')


        print(f"✅ Cleaned data saved to {output_filepath}")

    except FileNotFoundError:
        print(f"Error: File not found at {input_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()



def clean_json_data(input_string):  # Remains the same
    try:
        json_data = json.loads(input_string)
        inner_json_string = json_data.get("f0_", "{}")
        inner_json = json.loads(inner_json_string)
        # ... (rest of the inner function is the same)
        context = inner_json.get("context", "")
        response = inner_json.get("response", "")


        # Perform text cleaning here if needed (e.g., remove HTML entities, extra spaces)

        return {
            "context": context,
            "response": response,
            "original_index": inner_json.get("original_index")  # Include index if needed.
        }


    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Example Usage (with JSONL input and output)
clean_jsonl_file("bigQuery_uploads_export_bq_cleaned_friends_table_2025-05-19 05_08_50.170349+00000000000000.jsonl", "bigQuery_uploads_export_bq_cleaned_friends_table.jsonl")