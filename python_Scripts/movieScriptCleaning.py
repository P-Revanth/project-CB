import chardet  # type: ignore
import re
import pandas as pd  # type: ignore
import csv

def clean_movie_script(filepath, output_file, errors='replace'):
    """Cleans movie script data and maps each line as context with any associated response (based on response_num)."""
    try:
        # 1. Detect encoding
        with open(filepath, 'rb') as f:
            rawdata = f.read()
        encoding = chardet.detect(rawdata)['encoding']
        print(f"Detected encoding: {encoding}")

        # 2. Regex pattern
        pattern = re.compile(
            r'^(\d+)\s\+\+\+\$\+\+\+\s(.*?)\s\+\+\+\$\+\+\+\s(\d+)\s\+\+\+\$\+\+\+\s(.*?)\s\+\+\+\$\+\+\+\s(\d+)?\s\+\+\+\$\+\+\+\s(.*)$'
        )

        data = []
        with open(filepath, 'r', encoding=encoding, errors=errors) as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    line_num, movie_title, next_line, speaker, response_num, dialogue = match.groups()
                    data.append({
                        "line_num": int(line_num),
                        "movie_title": movie_title,
                        "speaker": speaker,
                        "dialogue": dialogue,
                        "response_num": int(response_num) if response_num else None
                    })
                else:
                    print(f"⚠️ Skipped malformed line: {line.strip()}")

        if not data:
            print("No valid data found. Exiting.")
            return

        df = pd.DataFrame(data)

        # 3. Create a map of line_num → dialogue
        line_to_dialogue = dict(zip(df['line_num'], df['dialogue']))

        # 4. Create a list of context-response pairs
        result_rows = []

        for i, row in df.iterrows():
            context_line_num = row['line_num']
            context_dialogue = row['dialogue']

            # Find all responses to this context (i.e. where response_num == context_line_num)
            responses = df[df['response_num'] == context_line_num]

            if not responses.empty:
                for i, resp_row in responses.iterrows():
                    result_rows.append({
                        "index": i,
                        "movie_title": row['movie_title'],
                        "speaker": row['speaker'],
                        "context": context_dialogue,
                        "response": resp_row['dialogue']
                    })
            else:
                # No one responded to this line → keep it with empty response
                result_rows.append({
                    "index": i,
                    "movie_title": row['movie_title'],
                    "speaker": row['speaker'],
                    "context": context_dialogue,
                    "response": ""
                })

        # 5. Save to DataFrame and CSV
        final_df = pd.DataFrame(result_rows)
        final_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, lineterminator="\n", encoding='utf-8')
        print(f"✅ Saved cleaned data to '{output_file}'")

    except FileNotFoundError:
        print(f"❌ Error: File not found at '{filepath}'")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

clean_movie_script("cornell_movie_quotes_corpus/moviequotes.scripts.txt", "cleaned_moviequotes_script.csv", errors='replace')