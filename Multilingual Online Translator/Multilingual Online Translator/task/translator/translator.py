import requests
from bs4 import BeautifulSoup
import re
from sys import argv


languages = {'1': 'Arabic', '2': 'German', '3': 'English', '4': 'Spanish', '5': 'French', '6': 'Hebrew',
             '7': 'Japanese', '8': 'Dutch', '9': 'Polish', '10': 'Portuguese', '11': 'Romanian', '12': 'Russian',
             '13': 'Turkish'}

url_base = 'https://context.reverso.net/translation/'
headers = {'User-Agent': 'Mozilla/81.0'}


def user_input():
    """
    Call user_input in main() below if you want the user to use input() to enter the translation,
    otherwise, the arguments can be read from argv (command line)
    """
    print("Hello, you're welcome to the translator. Translator supports:")
    for k, v in languages.items():
        print(f'{k}. {v}')
    input_source = input('Type the number of your language:\n')
    input_target = input('Type the number of language you want to translate to:\n')
    input_word = input('Type the word you want to translate:\n')
    return input_source, input_target, input_word


def define_query(query_source, query_target, query_word):
    # query = url_base + languages[query_source].lower() + '-' + languages[query_target].lower() + '/' + query_word
    # use version below if languages are specified directly and not by number
    query = url_base + query_source.lower() + '-' + query_target.lower() + '/' + query_word
    print(query)
    return query  # e.g. # https://context.reverso.net/translation/english-french/cheese


def get_translation(url_full, results='full'):
    if results == 'partial':  # if translating to all languages, return 1 translation and 2 examples
        translations_len = 1
        examples_len = 2
    else:  # if only translating to one language, return 5 each of translations and examples
        translations_len = 5
        examples_len = 5

    target_translation = re.findall("(?:-)(\\w+)", url_full)[0].capitalize()
    source_word = re.findall("\\w+", url_full)[-1]

    cr = requests.get(url_full, headers=headers)
    if cr.status_code == 404:  # if the site returns a 404 error that the page can't be found, it's an invalid word
        print(f'Sorry, unable to find {source_word}')
        exit()
    soup = BeautifulSoup(cr.text, 'html.parser')

    div_translations = soup.find('div', {'id': 'translations-content'})
    translations = []

    for a in div_translations.find_all('a')[:translations_len]:  # only keep first 5
        translations.append(a.get_text().strip())

    div_examples = soup.find_all('div', {'class': 'example'})[:examples_len]  # only keep first 5
    examples = []

    # target example class is different for Arabic and Hebrew
    target_example_class = 'trg rtl arabic' if target_translation == 'Arabic' \
        else 'trg rtl' if target_translation == 'Hebrew' \
        else 'trg ltr'

    for d in div_examples:
        # create list of tuples like [('source example', 'ejemplo de destinario'), (..., ...)]
        examples.append((d.find_all('div', {'class': 'src ltr'})[0].find('span').get_text().strip(),  # source
                         d.find_all('div', {'class': target_example_class})[0].find_all('span')[1].get_text().strip()))  # target

    # remove commas
    examples = [(e[0].replace(',', ''), e[1].replace(',', '')) for e in examples]

    # print and write results to a file
    with open(f'{source_word}.txt', 'a', encoding='utf-8') as file:

        print(f'\n{target_translation} Translations:')  # e.g. 'French Translations:'
        file.write(f'{target_translation} Translations:\n')
        for translation in translations:
            print(translation)
            file.write(translation + '\n')
        print()
        file.write('\n\n')

        print(f'{target_translation} Examples:')  # e.g. 'French Examples:'
        file.write(f'{target_translation} Examples:\n')
        for e in examples:
            formatted_e = f'{e[0]}\n{e[1]}\n\n'
            print(formatted_e)
            file.write(formatted_e)


def main():
    # source, target, word = user_input()  # if using input() to get variables
    source, target, word = argv[1:]

    # if target == '0':  # if the user wants translation to all other languages, using the user_input() function
    if target == 'all':  # if the user wants translation to all other languages, using argv
        # targets = [k for k in languages.keys() if k != source]  # if languages are specified by number
        targets = [v for v in languages.values() if v.lower() != source]
        for t in targets:
            get_translation(define_query(source, t, word), results='partial')
    elif target in languages.keys():  # otherwise, get the requested translation
        get_translation(define_query(source, target, word), results='full')
    else:
        print(f"Sorry, the program doesn't support {target}")


main()
