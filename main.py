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
    'description': None,
    'taxonomy': set()
}


filtered_categories = (
    'excluded',
    'retracted articles'
)

cat2tax = {
 'Environmental': 'Environment',
 'colony stimulating factors': 'Clinical Features and Diagnosis',
 'breastfeeding': 'Special Populations',
 'human immunodeficiency virus (HIV) disease': 'COMORBIDITY',
 'specific age groups': 'Special Populations',
 'families with children': 'Special Populations',
 'children and adolescents': 'Special Populations',
 'cancer patients': 'Special Populations',
 'health workers': 'Special Populations',
 'pregnant women': 'Special Populations',
 'automated or semi-automated contact tracing': 'Public Health and Case Reporting',
 'COVID-19': 'DIAGNOSIS',
 'asymptomatic or presymptomatic individuals': 'DIAGNOSIS',
 'SARS-CoV-2 variants': 'DIAGNOSIS',
 'educational interventions': 'Education',
 'digital interventions': 'Education',
 'nudging interventions': 'Education',
 'telehealth': 'Telemedicine',
 'communication interventions': 'Education',
 'interventions for smoking cessation': 'Therapeutics and Prevention',
 'behavioral': 'Therapeutics and Prevention',
 'psychological': 'Therapeutics and Prevention',
 'educational and self-care interventions': 'Education',
 'interventions to prevent or alleviate occupational burnout': 'Therapeutics and Prevention',
 'nutritional support': 'Therapeutics and Prevention',
 'cardiopulmonary resuscitation techniques': 'Therapeutics and Prevention',
 'renal replacement therapy': 'Therapeutics and Prevention',
 'dieting': 'Therapeutics and Prevention',
 'public health interventions': 'Public Health and Case Reporting',
 'interventions to handle the bodies of deceased persons': 'Logistics',
 'interventions related with paid sick leave': 'Logistics',
 'relaxation techniques': 'Therapeutics and Prevention',
 'exercise or physical activity': 'Therapeutics and Prevention',
 'therapeutic procedures': 'Therapeutics and Prevention',
 'electric stimulation': 'Therapeutics and Prevention',
 'parenteral access methods': 'Therapeutics and Prevention',
 'Primary studies': 'Primary Study ',
 'evidence synthesis': 'Systemic Review',
 'non-randomised studies': 'Paper',
 'Systematic review': 'Systemic Review',
 'living evidence synthesis': 'Systemic Review',
 'vaccination': 'Therapeutics and Prevention',
 'infection protective measures': 'Personal Protection',
 'public space disinfection': 'Personal Protection',
 'Disinfection and sanitisation': 'Personal Protection',
 'passive immunization': 'Therapeutics and Prevention',
 'social distancing measures': 'Personal Protection',
 'broad synthesis': 'Other',
 'preclinical research': 'Paper',
 'randomised trial': 'Paper',
 'older adults': 'Special Populations',
 'specific settings': 'All',
 'specific healthcare settings': '(Specify)',
 'corticosteroids': 'Therapeutics and Prevention',
 'Phosphodiesterase-5 inhibitors': 'Therapeutics and Prevention',
 'parenting interventions': 'Therapeutics and Prevention',
 'psychotherapy': 'Therapeutics and Prevention',
 'Behavioural': 'Therapeutics and Prevention',
 'Social and Systems Interventions': 'Therapeutics and Prevention',
 'serine': 'Therapeutics and Prevention',
 'targeted therapies': 'Therapeutics and Prevention',
 'colchicine': 'Therapeutics and Prevention',
 'nonsteroidal anti-inflammatory drugs': 'Therapeutics and Prevention',
 'lactoferrin': 'Therapeutics and Prevention',
 'antihistamines': 'Therapeutics and Prevention',
 'Calcium channel blockers': 'Therapeutics and Prevention',
 'Ampion': 'Therapeutics and Prevention',
 'coenzyme Q10': 'Therapeutics and Prevention',
 'dietary supplements': 'Therapeutics and Prevention',
 'nutraceuticals': 'Therapeutics and Prevention',
 'functional foods and herbal therapies': 'Therapeutics and Prevention',
 'pharmaceutical anticonvulsants': 'Therapeutics and Prevention',
 'antipsychotics': 'Therapeutics and Prevention',
 'antidepressants': 'Therapeutics and Prevention',
 'oxytocin and oxytocin analogues': 'Therapeutics and Prevention',
 'lipid-lowering pharmacological agents': 'Therapeutics and Prevention',
 'diet and dietary interventions': 'Therapeutics and Prevention',
 'inhaled β2-adrenergic agonists': 'Therapeutics and Prevention',
 'paracetamol (acetaminophen)': 'Therapeutics and Prevention',
 'mood stabilizers': 'Therapeutics and Prevention',
 'radiation therapy': 'Therapeutics and Prevention',
 'antacid': 'Therapeutics and Prevention',
 'antiulcer and antireflux drugs': 'Therapeutics and Prevention',
 'pentoxifylline': 'Therapeutics and Prevention',
 'chemotherapy': 'Therapeutics and Prevention',
 'physical therapy and rehabilitation': 'Therapeutics and Prevention',
 'antisense therapy': 'Therapeutics and Prevention',
 'melatonin': 'Therapeutics and Prevention',
 'mucolytic  agents': 'Therapeutics and Prevention',
 'immunosuppressive and immunomodulator agents': 'Therapeutics and Prevention',
 'creative arts therapies': 'Therapeutics and Prevention',
 'vasoactive intestinal polypeptide analog': 'Therapeutics and Prevention',
 'NMDA receptor antagonists': 'Therapeutics and Prevention',
 'synthetic cannabinoids': 'Therapeutics and Prevention',
 'succinic acid': 'Therapeutics and Prevention',
 'iron chelating agents': 'Therapeutics and Prevention',
 'antioxidant supplementation': 'Therapeutics and Prevention',
 'antithrombotic agents': 'Therapeutics and Prevention',
 'leukotriene receptor antagonists': 'Therapeutics and Prevention',
 'targeted radionuclide therapy': 'Therapeutics and Prevention',
 'polyunsaturated fatty acids (PUFAs)': 'Therapeutics and Prevention',
 'probiotics': 'Therapeutics and Prevention',
 'prebiotics and synbiotics': 'Therapeutics and Prevention',
 'erythropoiesis-stimulating agents': 'Therapeutics and Prevention',
 'Neurokinin 1 receptor antagonists': 'Therapeutics and Prevention',
 'Aldose reductase inhibitors': 'Therapeutics and Prevention',
 'Intravenous general anesthesia': 'Therapeutics and Prevention',
 'prostacyclin analogues': 'Therapeutics and Prevention',
 'dimethyl fumarate': 'Therapeutics and Prevention',
 'extracts or concentrates from natural sources': 'Therapeutics and Prevention',
 'cytokines': 'Therapeutics and Prevention',
 'bile acids and derivatives': 'Therapeutics and Prevention',
 'antifibrotic agents': 'Therapeutics and Prevention',
 'agents acting on the renin–angiotensin system': 'Therapeutics and Prevention',
 'minerals': 'Therapeutics and Prevention',
 'cell-based therapies (i.e. cellular therapy and extracellular vesicles': 'Therapeutics and Prevention',
 'respiratory stimulants': 'Therapeutics and Prevention',
 'hormonal therapies': 'Therapeutics and Prevention',
 'carnitine': 'Therapeutics and Prevention',
 'antiarrhythmics': 'Therapeutics and Prevention',
 'antifibrinolytic agents': 'Therapeutics and Prevention',
 'S-Adenosyl methionine': 'Therapeutics and Prevention',
 'vitamins': 'Therapeutics and Prevention',
 'alpha blockers': 'Therapeutics and Prevention',
 'fecal microbiota transplant': 'Therapeutics and Prevention',
 'beta blockers': 'Therapeutics and Prevention',
 'acetylcholinesterase inhibitors': 'Therapeutics and Prevention',
 'endothelin receptor antagonists': 'Therapeutics and Prevention',
 'inosine supplementation': 'Therapeutics and Prevention',
 'opioid receptor antagonists': 'Therapeutics and Prevention',
 'anti-diabetic medication': 'Therapeutics and Prevention',
 'respiratory support': 'Therapeutics and Prevention',
 'serine protease inhibitors': 'Therapeutics and Prevention',
 'Phosphodiesterase-4 inhibitors': 'Therapeutics and Prevention',
 'light-based and laser therapies': 'Therapeutics and Prevention',
 'Vasoactive drugs': 'Therapeutics and Prevention',
 'antimicrobials': 'Therapeutics and Prevention',
 'xanthine oxidase inhibitors': 'Therapeutics and Prevention',
 'neprilysin inhibitors': 'Therapeutics and Prevention',
 'extracorporeal circulatory procedures': 'Therapeutics and Prevention',
 'pharmacological interventions': 'Therapeutics and Prevention',
 'tracheal intubation': 'Therapeutics and Prevention',
 'self-care interventions': 'Therapeutics and Prevention',
 'hand hygiene and interventions to improve hand hygiene compliance': 'Personal Protection',
 'strategies to manage blood glucose within a specific target': 'Therapeutics and Prevention',
 'national pandemic strategies': 'Government',
 'physical activity and physical therapy': 'Therapeutics and Prevention'
}



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

            if cat2tax.get(cat.title, None) is not None:
                n['taxonomy'].add(cat2tax[cat.title])

            if cat2tax.get(cat.type, None) is not None:
                n['taxonomy'].add(cat2tax[cat.type])


        # short things are classified wrong all the time, setting limit to reduce error rate
        if len(record.abstract) < 100:
            n['language'] = 'en'
        else:
            n['language'] = langid.classify(record.abstract)[0]

        n['title'] = record.title

        n['author'] = record.authors

        n['year'] = record.year

        n['description'] = record.abstract

        n['taxonomy'] = tuple(n['taxonomy'])

        c19nav_records.append(n)

    with open('./out/results.json', 'w') as f:
        f.write(json.dumps(c19nav_records, indent=4))




    
