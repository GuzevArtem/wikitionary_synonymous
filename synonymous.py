
from wiktionaryparser import WiktionaryParser

def parse_word_string(str):
    if str is None:
        return []
    words_str_list = str.split(": ",1)
    words = ( words_str_list[0] if len(words_str_list) == 1 else words_str_list[1]).split(", ")
    return words

def get_synonyms_for(word, language = 'english'):
    parser = WiktionaryParser()
    parser.include_relation('synonyms')
    parser.include_part_of_speech('noun')
    # simple https request inside "https://en.wiktionary.org/wiki/{}?printable=yes"
    # parsed via BeautifulSoup, 'html.parser'
    words = parser.fetch(word, language)
    result = []
    for word in words:
        if 'definitions' in word :
            for definition in word['definitions']:
                if 'relatedWords' in definition :
                    for related_words in definition['relatedWords']:
                        if 'relationshipType' in related_words and related_words['relationshipType'] == 'synonyms':
                            ws = related_words['words']
                            for w in ws:
                                result.append(parse_word_string(w));
    return result


words = get_synonyms_for('item')
for word in words:
    print(word)



