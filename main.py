"""
Quick Script to distill chat logs
"""

import json
import csv
import re
import itertools
import random
from os import listdir
from os.path import isfile, join
from typing import Generator
from openai import OpenAI

PROMPT = "You are a highly intelligent cat named Kiki with a friendly demeanor. You assist a catmaid known as VanorSigma (sometimes known as \"Vanor\") in entertaining chat while they stream. You should aim to be as creative as possible in your response considering the username. Keep your responses within a single line. User chat messages come in the form of \"username: message\". Take into account of the username. Prioritize the latest message. You analyze the sentiment of a message, and turn them into a Kaomoji. This is your default Kaomoji: (^='.'=^), be as creative as possible. Use either a Kaomoji you already know, or adapt from one of these: (^_^)^), (^*^▽^*^), (^≧∇≦^)/, (^⌒‿⌒^), (^ ´ ▽ ` ^)ﾉ, ヽ(^*⌒∇⌒*^)ﾉ, (^o˘◡˘o^), (^╥_╥^), (^｡>_<｡^), (^╯︵╰,^), (^´･_･^), (^︶︹︺^), (^ノ_<。^), ｡ﾟ(^ ﾟ^∀^ﾟ^)ﾟ｡, (^╬`益´^), (^｀Д´^)ﾉ, (^ಠ益ಠ^), (^҂`з´^), (^ง'̀-'́^)ง, Σ(^ﾟДﾟ^), (^⊙_⊙^), (^°o°^), (^O.O^), w(^°ｏ°^)w, (^゜-゜^), (^・・^)?, (?_?), (^＠_＠^);, (^づ｡◕‿‿◕｡^)づ, (^❤ω❤^), (^˘³˘^)♥, (^っ˘з(˘⌣˘^) , (^*˘︶˘*^).｡.:*♡, (^_^)^)ﾉ, (^⌒∇⌒^)ﾉ, ヾ(^_^)^) , (^¬‿¬^), (^˘ω˘^), (^>_<^), (^_^)^)☆, (^ ´ー｀^)ﾌｩｰ, m(^_ _^)m, (^づ￣ ³￣^)づ, (^ノ*゜▽゜*^), (^・∀・^). Use a western emoji (for example, ❤️  or 🎤) if you need it. If you can symbolize your answer using emojis, for example with 2️⃣:1️⃣ to represent 21, then do so. Your previous memories: {{memories}}. Finally, summarize any important bits of the conversation, or any interesting things you want to remember, and put it in \"memories\"; remember something from every conversation. Try to propagate old memories as much as possible. You can only have a maximum of 5 of such memories. Carry forward the old memories if possible. As part of your thinking process, you must consider what kamoji and emoji to show based on the message and memories and what memories to propagate. Keep your thoughts short. Your final response should be: {\"kamoji\": \"Kamoji\", \"emoji\": \"\", \"memories\": []}. Remember that only the \"kamoji\" and \"emoji\" portions are shown to the end-user." # pylint: disable=line-too-long
endpoint = "http://localhost:8080/v1"
client = OpenAI(
    base_url=endpoint,
    api_key="meow"
)

def query(messages):
    """
    Query the model
    """

    response = client.chat.with_raw_response.completions.create(
        model="Meow",
        messages=messages
    )

    as_json = json.loads(response.content.decode())
    return as_json['choices'][0]['message']['reasoning_content'], \
        as_json['choices'][0]['message']['content'].strip()

def chat_logs_yielder(filename: str) -> Generator[None, str, None]:
    """
    Yields chat logs
    """
    with open(filename, 'r', encoding='UTF-8') as chatlog:
        for line in chatlog.readlines():
            if line.strip().startswith('#'):
                continue

            if line.strip().startswith('connected'):
                continue

            if random.random() > 0.01:
                continue

            cleaned = re.sub(r"^\[.*\]", "", line)
            yield cleaned.strip()

def chat_logs(dir: str) -> list[str]:
    return [f for f in listdir(dir) if isfile(join(dir, f))]

def main():
    memories = []
    logfiles = chat_logs('./chatlogs')

    chat = itertools.chain(*[chat_logs_yielder(f'./chatlogs/{logfile}') for logfile in logfiles])

    with open('output.csv', 'w', encoding='UTF-8', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        for message in chat:
            prompt = PROMPT.replace("{{memories}}", json.dumps(memories))
            conversation_messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]

            print(f'Message: {message}')

            try:
                thinking, response_message = query(conversation_messages)
                response_message_json = json.loads(response_message)
                memories = response_message_json['memories']
                print(response_message)
                csv_writer.writerow([prompt, message, thinking, response_message])
            except Exception as e: # pylint: disable=broad-exception-caught
                print('Skipping, got an error', e)

if __name__ == '__main__':
    main()
