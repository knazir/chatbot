import json
import os
import sys

from dateutil import parser as dateparser


SORTED_FILE_PATH = './messages_sorted.json'
NGRAM_LIMIT = 4
NAME = ''


def setup_loading_bar(loading_bar_width):
    sys.stdout.write("[%s]" % (" " * loading_bar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (loading_bar_width + 1))  # return to start of line, after '['


def sort_messages(messages):
    setup_loading_bar(len(messages['threads']))
    for thread in messages['threads']:
        thread['messages'].sort(key=lambda message_list: dateparser.parse(message_list['date_time']))
        sys.stdout.write('-')
        sys.stdout.flush()
    sys.stdout.write('\n')


def use_existing_sorted_file():
    with open(SORTED_FILE_PATH, 'r') as sorted_file:
        return json.load(sorted_file)


def create_sorted_file():
    with open(sys.argv[1]) as messages_file:
        messages = json.load(messages_file)
        sort_messages(messages)
        with open(SORTED_FILE_PATH, 'w') as sorted_file:
            sorted_file.write(json.dumps(messages, indent=4, sort_keys=True))
        return messages


def generate_ngrams(n, messages):
    ngrams_list = []
    for thread in messages['threads']:
        for message in thread['messages']:
            if message['sender'] == NAME and len(message['text'].split()) >= n:
                message_tokens = message['text'].split()
                for gram in zip(*[message_tokens[i:] for i in range(n)]):
                    ngrams_list.append(gram)
    return ngrams_list


def build_messages():
    if not os.path.exists(SORTED_FILE_PATH):
        return create_sorted_file()
    else:
        return use_existing_sorted_file()


def build_ngram_map(messages):
    ngram_map = {}
    for n in range(2, NGRAM_LIMIT + 1):
        ngram_map[n] = generate_ngrams(n, messages)


def main():
    if len(sys.argv) <= 1:
        raise Exception('Usage: create_model.py pathToMessagesJson')

    print('Parsing Chat History...')
    messages = build_messages()
    print('Done.')

    print('Generating Ngrams Map.')
    build_ngram_map(messages)
    print('Done.')


if __name__ == '__main__':
    main()
