import re
import pandas as pd # type: ignore

# Load WhatsApp exported chat file
with open("anish.txt", "r", encoding="utf-8") as file:
    raw_lines = file.readlines()

# Regular expression pattern to match messages
# Supports both 12-hour and 24-hour formats
msg_pattern = re.compile(
    r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\s?[APMapm]{2})?) - ([^:]+): (.+)'
)

messages = []
current_msg = {}

for line in raw_lines:
    line = line.strip()

    match = msg_pattern.match(line)
    if match:
        # Save previous message if present
        if current_msg:
            messages.append(current_msg)

        date, time, sender, message = match.groups()
        current_msg = {
            "date": date,
            "time": time,
            "sender": sender.strip(),
            "message": message.strip(),
        }
    else:
        # Continuation of a previous message (multi-line)
        if current_msg:
            current_msg["message"] += "\n" + line

# Append last message
if current_msg:
    messages.append(current_msg)

# Convert to DataFrame
df = pd.DataFrame(messages)

# Optional: Filter out system messages if needed
df = df[~df["sender"].str.contains("Messages to this|end-to-end encryption", case=False)]

# Save to CSV
df.to_csv("cleaned_chat_anish.csv", index=False, encoding="utf-8")

print("Parsing completed. Output saved as 'cleaned_chat_anish.csv'")