import re
import pandas as pd # type: ignore
import csv
from datetime import datetime

# === Step 1: Parse WhatsApp Chat File ===

with open("Vishnu.txt", "r", encoding="utf-8") as file:
    raw_lines = file.readlines()

# Regular expression for parsing messages
msg_pattern = re.compile(
    r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\s?[APMapm]{2})?) - ([^:]+): (.+)'
)

messages = []
current_msg = {}
message_id_counter = 0  # Initialize message ID counter

# Parse the chat messages into a structured format
for line in raw_lines:
    line = line.strip()
    match = msg_pattern.match(line)
    if match:
        if current_msg:
            messages.append(current_msg)
        date_str, time_str, sender, message = match.groups()
        message_id_counter += 1  # Increment message ID for each new message
        current_msg = {
            "message_id": message_id_counter,  # Assign unique ID
            "date": date_str,
            "time": time_str,
            "sender": sender.strip(),
            "message": message.strip(),
        }
    else:
        if current_msg:
            current_msg["message"] += "\n" + line

if current_msg:
    messages.append(current_msg)

# === Step 2: Create DataFrame & Add Timestamps ===

df = pd.DataFrame(messages)

# Remove system messages (e.g., encryption info, etc.)
df = df[~df["sender"].str.contains("Messages to this|end-to-end encryption", case=False)]

# Combine date and time to create a timestamp
def parse_datetime(row):
    try:
        return pd.to_datetime(f"{row['date']} {row['time']}", errors='coerce')
    except:
        return pd.NaT

df["timestamp"] = df.apply(parse_datetime, axis=1)
df = df.dropna(subset=["timestamp"]).sort_values(by="timestamp").reset_index(drop=True)

# === Step 3: Calculate Time Difference & Response Logic ===

df["time_diff"] = df["timestamp"].diff().dt.total_seconds().div(60)  # in minutes

# Initialize 'response_to_id' column. This will store the message_id that each message is responding to.
df["response_to_id"] = None

# Iterate through the DataFrame to determine responses.  Critically important to use .iloc for index-based access.
for i in range(1, len(df)): # start from 1 to avoid index error.
    # Same sender:  This message is likely a continuation of the previous message from the same sender.
    if df.iloc[i]['sender'] == df.iloc[i-1]['sender']:
        df.at[i, 'response_to_id'] = df.iloc[i-1]['message_id']  #Responds to previous message

    # Different sender, but short time difference: Likely a direct response.
    elif df.iloc[i]['time_diff'] <= 30:
        df.at[i, 'response_to_id'] = df.iloc[i-1]['message_id'] # Responds to previous message

# Save cleaned chat to CSV
df.to_csv("cleaned_chat_Vishnu.csv", index=False, encoding="utf-8", quoting=csv.QUOTE_ALL, lineterminator="\n")
print("✅ Saved structured chat with response IDs to 'cleaned_chat.csv'")

# === Step 4: Flatten the Data for BigQuery ===
# Now, instead of creating separate CSVs for prompt-response pairs and group chats, create a single DataFrame
# that includes all messages with the 'response_to_id' column. This is much easier to load into BigQuery.

# No need to group or split the data further.
# The 'response_to_id' column provides the necessary information to understand the conversation flow.

# print("Data is now ready to be loaded into BigQuery.")