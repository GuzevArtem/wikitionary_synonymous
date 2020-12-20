import os
from pathlib import Path
from wiktionaryparser import WiktionaryParser
import requests
import bz2

#Possible output
#
#Downloading index
#Gathering synonyms
#activity : [['See also Thesaurus:activity']]
#smell : [['see Thesaurus:smell(pleasant): aroma', 'fragrance', 'odor/odour', 'scent; see also Thesaurus:aroma(unpleasant): niff (informal)', 'pong (informal)', 'reek', 'stench', 'stink; see also Thesaurus:stench'], ['aroma', 'fragrance', 'odor/odour', 'scent; see also Thesaurus:aroma'], ['niff (informal)', 'pong (informal)', 'reek', 'stench', 'stink; see also Thesaurus:stench'], ['olfaction (in technical use)', 'sense of smell']]
#reception : [['front desk']]
#follow up : [['chase up (British)'], ['get back to'], ['revert']]
#ad hoc : [['ad hocly']]
#address : [['adroitness'], ['discourse'], ['harangue'], ['ingenuity'], ['lecture'], ['oration'], ['petition'], ['readiness'], ['speech'], ['tact']]
#affect : [['fake', 'simulate', 'feign']]
#applicable : [['appropriate; See also Thesaurus:suitable or Thesaurus:pertinent']]
#arrogance : [['See also Thesaurus:arrogance.']]
#ASAP : [['stat']]
#availability : [['availableness', 'accessibility']]
#bug : [['See also Thesaurus:defect'], ['See also Thesaurus:annoy']]
#bulletproof : [['foolproof']]
#buy : [['cheap (obsolete)', 'purchase'], ['accept', 'believe', 'swallow (informal)', 'take on'], ['make a buy']]
#string : [['thread'], ['lace']]
#workaround : [['see Thesaurus:workaround']]
#agenda : [['docket', 'worklist', 'schedule']]
#Processed: 102
#Totally processed: 102


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

def download_and_read_index(url, date, filename, save_path_formatable, limit = 10000):
    formatted_url = url.format(date, filename)
    path = save_path_formatable.format(filename)

    #cache download
    if not os.path.exists(path) :
        index = requests.get(formatted_url)
        with open(path, "wb") as f:
            f.write(index.content)

    read_index = []

    with bz2.BZ2File(path, "r", "utf-8") as fp:
        for _ in range(limit):
            line = fp.readline()
            splitted_line = str(line, "utf-8").split(':')
            if 4 > len(splitted_line) > 2 : # if 4 -> its index / template or wiki info
                word = splitted_line[2].replace("\n","").replace("'","").replace("\\","") #remove byte to str conversion garbage
                read_index.append(word)
    return read_index





src = "https://dumps.wikimedia.org/ruwiktionary/{}/{}"
date = "20201201"
filename = "ruwiktionary-{}-pages-articles-multistream-index.txt.bz2".format(date)
temp_path = "./temp"
temp_path_formattable = temp_path + "/{}"



print("Downloading index")
Path(temp_path).mkdir(parents=True, exist_ok=True)
read_index = download_and_read_index(src, date, filename, temp_path_formattable, 1000)
print("Gathering synonyms")
processed_count = 0
for word in read_index:
    synonyms = get_synonyms_for(word)
    if synonyms:
        print ( word, ':', synonyms)
    #save to file?
    processed_count += 1
    print("Processed:", processed_count, end='\r')
print("Totally processed:", processed_count, end='\n')
#print("Clearing temp files")
#os.remove(temp_path_formattable.format(filename))



### sax downloading is too long if we need only partial results
#import xml.sax 
#import re 
# 
#class SynonymExtractorHandler(xml.sax.ContentHandler): 
#    def __init__(self, limit): 
#        self.limit = limit 
#        self.currentTag = '' 
#        self.title = '' 
#        self.on_synonyms = False 
#        self.current_synonyms = None 
#        self.all_synonyms = [] 
# 
#    def startElement(self, tag, attrs): 
#        if self.limit > 0:
#            self.currentTag = tag
#
#    def extract_word(self, seq): 
#        return re.findall('\\[\\[(.*?)\\]\\]', seq) 
#     
#    def characters(self, content): 
#        if self.limit > 0: 
#            if self.currentTag == 'title': 
#                if bool(re.search('\\w', content)): 
#                    self.title = content 
#            elif self.currentTag == 'text': 
#                if not self.on_synonyms and content == '==== Синонимы ====': 
#                    self.on_synonyms = True 
#                    if self.current_synonyms is None: 
#                        self.current_synonyms = [] 
#                elif self.on_synonyms: 
#                    if content.startswith('#'): 
#                        syns = self.extract_word(content) 
#                        self.current_synonyms.extend(syns) 
#                    else: 
#                        if content != '\\n': 
#                            self.on_synonyms = False 
#     
#    def endElement(self, tag): 
#        if self.limit > 0: 
#            if tag == 'text' and self.current_synonyms is not None: 
#                if self.current_synonyms: 
#                    pair = (self.title, self.current_synonyms) 
#                    print(pair) 
#                    self.all_synonyms.append(pair) 
#                    self.limit -= 1 
#                    if self.limit <= 0: 
#                        raise xml.sax.SAXException('limit') 
#                     
#                self.on_synonyms = False 
#                self.current_synonyms = None 
#     
#src = 'ruwiktionary-20201201-pages-articles-multistream.xml' 
# 
#try: 
#    xml.sax.parse(src, SynonymExtractorHandler(10)) 
#except xml.sax.SAXException as e: 
#    if e.getMessage() == 'limit': 
#        pass 
#    else:  
#        raise e
