import regex as re
from nltk.corpus import stopwords
from model import db, connect_to_db, President, Speech, Collocation

excess = stopwords.words('english')


def str_parser(sentence):

    all_lower = sentence.lower()

    clean_text = re.sub(r'\p{P}', '', all_lower)  # removes punctuatation from unicode

    indiv_words = clean_text.split()

    for word in excess:
        while word in indiv_words:
            indiv_words.remove(word)         # removes words like 'and', 'the', 'or'

    return indiv_words


def make_nodes_and_links():
    """Creates dataset for d3 force layout.

    Paths are source/target/type list of dictionaries, nodes are a list of
    id/name/group dictionaries.
    Node groups:
    1: president name
    2: speech title
    3: positive bigram
    4: neutral bigram
    5: negative bigram

    """

   
    speech_lst = Speech.query.all()
    phrase_lst = Collocation.query.all()
    prez_lst = President.query.all()

  
    nodes = []

    for item in prez_lst:
        nodes.append({'id': item.name, 'group': 1, 'name': item.name})

    for item in speech_lst:
        if 'state' in item.title.lower():
            nodes.append({'id': item.title, 'group': 2, 'name': 'SotU'})
        else:
            nodes.append({'id': item.title, 'group': 2, 'name': 'I'})

    phrase_sentiment = db.session.query(Collocation.phrase, Collocation.sentiment_score)
    p_sin_duplicates = phrase_sentiment.group_by('phrase', 'sentiment_score').all()

    for p in p_sin_duplicates:
        bigram, sentiment = p

        if sentiment == 'positive':
            nodes.append({'id': bigram, 'group': 3, 'name': bigram})

        elif sentiment == 'neutral':
            nodes.append({'id': bigram, 'group': 4, 'name': bigram})

        elif sentiment == 'negative':
            nodes.append({'id': bigram, 'group': 5, 'name': bigram})

    node_links = []

    for s in speech_lst:
        node_links.append({'speech': s.title, 'name': s.prez.name})


    phrase_nodes = []

    for p in phrase_lst:
      
        phrase_location = p.connect
        for phrase_info in phrase_location:
            phrase_title = Speech.query.filter(Speech.title == phrase_info.speech.title).first()
        phrase_nodes.append({'collocation': p.phrase, 'speech': phrase_title.title})


    node_links.extend(phrase_nodes)

  

    paths = []

    for speech in node_links:
        if 'name' in speech:
            paths.append({'source': speech['name'], 'target': speech['speech'],
                          'type': 'prez-speech'})

        else:
            paths.append({'source': speech['speech'], 'target': speech['collocation'],
                          'type': 'speech-bigram'})

    return nodes, paths


def graph_data():
    """Makes a data dictionary for vis.js timeline."""

    all_speeches = Speech.query.all()

    items = []

    for s in all_speeches:
        prez_name = s.prez.name
        if 'kennedy' in prez_name.lower():
            prez = 'Kennedy'
        elif 'lyndon' in prez_name.lower():
            prez = 'Johnson'
        elif 'nixon' in prez_name.lower():
            prez = 'Nixon'
        elif 'ford' in prez_name.lower():
            prez = 'Ford'
        elif 'carter' in prez_name.lower():
            prez = 'Carter'
        elif 'reagan' in prez_name.lower():
            prez = 'Reagan'
        elif 'h. w.' in prez_name.lower():
            prez = 'H.W. Bush'
        elif 'clinton' in prez_name.lower():
            prez = 'Clinton'
        elif 'w. bush' in prez_name.lower():
            prez = 'G.W. Bush'
        else:
            prez = 'Obama'

        url = s.link
        get_date = re.findall(r'[\w]+', s.title)   
        date = ' '.join(get_date[-3:])                 
        if 'state' in s.title.lower():
            title = prez + """<a href='{}'> state of union</a>""".format(url)
        else:
            title = prez + """<a href='{}'> inaugural</a>""".format(url)

     
        sentiment = s.sentiment

        items.append({'start': date, 'content': title, 'group': sentiment})

    groups = [{'id': 'pos', 'content': 'positive', 'className': 'pos'},
              {'id': 'neg', 'content': 'negative', 'className': 'neg'}]

    return items, groups



