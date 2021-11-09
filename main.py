import copy, json, re
from collections import namedtuple
from unicodedata import name
import langid



Category = namedtuple(
    'category', 
    [
        'title', 
        'type'
    ]
)

Info = namedtuple(
    'info', 
    [
        'study_design', 
        'type_of_article'
    ]
)

Article = namedtuple (
    'article',
    [
        'title',
        'abstract',
        'year',
        'authors',
        'journal',
        'category',
        'info'
    ]
)

c19nav = {
    'asset_maturity': None,
    'title': None,
    'author': None,
    'language': None,
    'year': None,
    'publication': 'Journal',
    'source type': 'Directory',
    'description': None
}


filtered_categories = (
    'excluded',
    'retracted articles'
)





def parse_category(category: dict) -> tuple:
    out = []
    for c in category:
        out.append(Category(c.get('title', None), c.get('type', None)))
    return tuple(out)

def calc_asset_maturity(type_of_article: str) -> str:
    if type_of_article == 'Primary studies' or type_of_article == 'primary-study':
        return 'Level 5: Very Mature'
    if type_of_article == 'living evidence synthesis':
        return 'Level 5: Very Mature'
    if type_of_article == 'non-randomised studies':
        return 'Level 5: Very Mature'
    if type_of_article == 'broad synthesis':
        return 'Level 3: Mature'
    if type_of_article == 'preclinical research':
        return "Level 4: More Mature"
    if type_of_article == 'Systematic review':
        return "Level 4: More Mature"
    if type_of_article == 'evidence synthesis':
        return "Level 4: More Mature"
    if type_of_article == 'randomised trial':
        return 'Level 5: Very Mature'

if __name__ == '__main__':
    infile = None
    outfile = None
    records = []
    c19nav_records = []

    with open('./data/references.full.json') as f:
        infile = json.loads(f.read())['data']


    tmp = set()

    for row in infile:
        a = Article(
            row.get('title', None), 
            row.get('abstract', None), 
            row.get('year', None), 
            row.get('authors', None), 
            row.get('journal', None), 
            parse_category(row['categories']) if row.get('categories', None) is not None else None, 
            Info(row['info'].get('study_design', None), row['info'].get('type_of_article', None)))

        for x in a.category:
            if x.type == 'article_classification':
                tmp.add(x.title)
        
        records.append(a)


    print (len(records))

    # remove things we don't want
    for i in reversed(range(len(records))):
        if records[i].category:
            for cat in records[i].category:
                if cat.title in filtered_categories:
                    del records[i]
                    break

    print (len(records))


    for record in records:
        n = copy.deepcopy(c19nav)

        if record.info is not None:
            n['asset_maturity'] = calc_asset_maturity(record.info.type_of_article)

        for cat in record.category:
            if cat.type == 'article_classification' and n['asset_maturity'] is None:
                if n['asset_maturity'] is not None:
                    n['asset_maturity'] = calc_asset_maturity(cat.title) if int(re.findall('[0-9]+', calc_asset_maturity(cat.title))[0]) > int(re.findall('[0-9]+', n['asset_maturity'])[0]) else n['asset_maturity']
                else:
                    n['asset_maturity'] = calc_asset_maturity(cat.title)


        # short things are classified wrong all the time, setting limit to reduce error rate
        if len(record.abstract) < 100:
            n['language'] = 'en'
        else:
            n['language'] = langid.classify(record.abstract)[0]

        n['title'] = record.title

        n['author'] = record.authors

        n['year'] = record.year

        n['description'] = record.abstract

        c19nav_records.append(n)

    with open('./out/results.json', 'w') as f:
        f.write(json.dumps(c19nav_records, indent=4))




    
