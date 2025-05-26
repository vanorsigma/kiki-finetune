# A script to inspect the contents of the dataset (so that we get it
# write on first try with an actual GPU)

from typing import TypedDict
import csv

class ConversationItem(TypedDict):
    role: str
    content: str

class Conversations(TypedDict):
    conversations: list[ConversationItem]

def make_conversation(row: list[str]) -> tuple[list[ConversationItem], list[ConversationItem]]:
    prompt, message, thinking, response_message = row
    combined_response = f'<think>{thinking}</think>{response_message}'
    return [{
        'role': 'system',
        'content': prompt
    }, {
        'role': 'user',
        'content': message,
    }, {
        'role': 'assistant',
        'content': combined_response
    }], [{
        'role': 'system',
        'content': prompt
    }, {
        'role': 'user',
        'content': message,
    }, {
        'role': 'assistant',
        'content': response_message
    }]

def from_file_load_conversation(filename: str) -> tuple[list[list[ConversationItem]], list[list[ConversationItem]]]:
    with open(filename, mode='r', encoding='utf8') as f:
        reader = csv.reader(f)
        think_conversations = []
        no_think_conversations = []

        for item in reader:
            think_conv, no_think_conv = make_conversation(item)
            think_conversations.append(think_conv)
            no_think_conversations.append(no_think_conv)
    return think_conversations, no_think_conversations

def main():
    think_conversations, no_think_conversations = from_file_load_conversation('output.csv')
    print(think_conversations[:5])
    print(no_think_conversations[:5])

if __name__ == '__main__':
    main()
