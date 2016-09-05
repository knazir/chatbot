import json
import os
import random
import sys

from dateutil import parser as dateparser


# Configuration
SORTED_FILE_PATH = './messages_sorted.json'
NGRAM_LIMIT = 3
NAME = 'Kashif Nazir'

# Sample Configuration
GENERATE_SAMPLES = True
SAMPLE_N = 3
SAMPLE_WORD_COUNT_MIN = 8
SAMPLE_WORD_COUNT_MAX = 20
SAMPLE_SENTENCES = 20


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
    ngrams_map = {}
    for thread in messages['threads']:
        for message in thread['messages']:
            if message['sender'] == NAME:
                message_tokens = message['text'].split()
                for gram in zip(*[message_tokens[i:] for i in range(n)]):
                    key = ' '.join(gram[:n - 1])
                    if gram[0] in ngrams_map:
                        ngrams_map[key].append(gram[-1])
                    else:
                        ngrams_map[key] = [gram[-1]]
    return ngrams_map


def build_messages():
    return use_existing_sorted_file() if os.path.exists(SORTED_FILE_PATH) else create_sorted_file()


def create_sample_sentence(i, ngram_maps):
    phrase = str(i + 1) + '. '
    next_start = random.choice(list(ngram_maps[SAMPLE_N].keys()))
    for j in range(random.randint(SAMPLE_WORD_COUNT_MIN, SAMPLE_WORD_COUNT_MAX + 1)):
        random_choice = random.choice(ngram_maps[SAMPLE_N][next_start])
        next_start_list = next_start.split()[1:]
        next_start_list.append(random_choice)
        if len(next_start_list) > 1 and next_start_list[-1] == next_start_list[-2]:
            continue
        next_start = ' '.join(next_start_list)
        phrase += random_choice + ' '
        if next_start not in ngram_maps[SAMPLE_N]:
            break
    return phrase[:-1]


def generate_samples(ngram_maps):
    try:
        sample_list = [create_sample_sentence(i, ngram_maps) for i in range(SAMPLE_SENTENCES)]
        print('\n'.join(sample for sample in sample_list))
    except IndexError:
        print('\nUnable to find chat history for ' + NAME + ', please check your messages and try again.')


def main():
    if len(sys.argv) <= 1:
        raise Exception('Usage: create_model.py pathToMessagesJson')

    print('Parsing Chat History...')
    messages = build_messages()
    print('Done.')

    print('Generating Ngrams Map...')
    ngram_maps = {n: generate_ngrams(n, messages) for n in range(2, NGRAM_LIMIT + 1)}
    print('Done.')

    if GENERATE_SAMPLES:
        generate_samples(ngram_maps)


if __name__ == '__main__':
    main()
