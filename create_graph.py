from rdflib import Graph, Literal, URIRef
from rdflib.namespace import Namespace, NamespaceManager
import json
import os
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# create a graph
g = Graph()
namespace_manager = NamespaceManager(g)
prefix_d = {
        'lexicog': 'http://www.w3.org/ns/lemon/lexicog#',
        'ontolex': 'http://www.w3.org/ns/lemon/ontolex#',
        'vartrans': 'http://www.w3.org/ns/lemon/vartrans#',
        'lime': 'http://www.w3.org/ns/lemon/lime#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'owl': 'http://www.w3.org/2002/07/owl#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'skos': 'http://www.w3.org/2004/02/skos#',
        'void': 'http://rdfs.org/ns/void#',
        'lexinfo': 'http://www.lexinfo.net/ontology/2.0/lexinfo#',
        'dc': 'http://purl.org/dc/elements/1.1/',
}
ns_d = dict() # namespace dictionary

def bind_namespace(prefix, uri):
    global namespace_manager, ns_d
    ns_d[prefix] = Namespace(uri)
    namespace_manager.bind(prefix, ns_d[prefix], override=False)

# bind namespaces
for prefix_t in prefix_d.keys():
    bind_namespace(prefix_t, prefix_d[prefix_t])

g.base = Namespace("http://ferhengo-ontolex-graph.com")

uri_ref = URIRef("http://uri")
g.add((g.base.subj, g.base.pred, g.base.obj))

with open(os.path.join(THIS_DIR, 'leker_parsed.json'), 'r', encoding='utf-8') as f:
    leker_parsed_d = json.load(f)
leker_l = leker_parsed_d.keys()

# monastery examples from https://www.w3.org/2019/09/lexicog/#example9
for leker_t in leker_l:
    val_d = leker_parsed_d[leker_t]
    l = leker_t.replace(' ', '-')
    # Entries
    # :monastery_n_en a ontolex:LexicalEntry .
    g.add((g.base[f'{l}_v_ku'], ns_d['rdf'].type, ns_d['ontolex'].LexicalEntry))
    # :monastery_n_en ontolex:canonicalForm :monastery_n_en_form .
    g.add((g.base[f'{l}_v_ku'], ns_d['ontolex'].canonicalForm, g.base[f'{l}_v_ku_form']))
    # :monastery_n_en_form a ontolex:Form .
    g.add((g.base[f'{l}_v_ku_form'], ns_d['rdf'].type, ns_d['ontolex'].Form))
    # :monastery_n_en_form ontolex:writtenRep "monastery"@en .
    g.add((g.base[f'{l}_v_ku_form'], ns_d['ontolex'].writtenRep, Literal(l, lang='ku')))
    # :monastery_n_en_form lexinfo:partOfSpeech lexinfo:noun .
    g.add((g.base[f'{l}_v_ku_form'], ns_d['ontolex'].partOfSpeech, ns_d['lexinfo'].verb))
    if 'meanings' in val_d.keys():
        meaning_l = val_d['meanings']
        for meaning_d in meaning_l:
            if 'meaning' in meaning_d.keys():
                # print(meaning_d['meaning']);input()
                # Senses
                # :monastery_n_en ontolex:sense :monastery_n_en_sense .
                g.add((g.base[f'{l}_v_ku'], ns_d['ontolex'].sense, g.base[f'{l}_v_ku_sense']))
                # :monastery_n_en_sense a ontolex:LexicalSense .
                g.add((g.base[f'{l}_v_ku_sense'], ns_d['rdf'].type, ns_d['ontolex'].LexicalSense))
                # :monastery_n_en_sense ontolex:isLexicalizedSenseOf :monastery_n_en_sense_concept .

                meaning_t = meaning_d['meaning']
                meaning_stripped_l = meaning_t.replace('[[', '').replace(']]', '').split(', ')
                for meaning_stripped_t in meaning_stripped_l:
                # example from https://www.w3.org/community/ontolex/wiki/Terminology#Example_2:_Representing_language_and_synonymy
                # <http://www.w3.org/ns/lemon/termlex#1443648_LS1> <http://www.lexinfo.net/ontology/3.0/lexinfo#synonym> <http://www.w3.org/ns/lemon/termlex#1443648_LS2> .
                    if meaning_stripped_t in leker_l:
                        meaning_stripped_t = meaning_stripped_t.replace(' ', '-')
                        g.add((g.base[f'{l}_v_ku_sense'], ns_d['lexinfo'].synonym, g.base[f'{meaning_stripped_t}_v_ku_sense']))

                g.add((g.base[f'{l}_v_ku_sense'], ns_d['ontolex'].isLexicalizedSenseOf, g.base[f'{l}_v_ku_sense_concept']))
                # Concepts
                # :monastery_n_en_sense_concept a ontolex:LexicalConcept .
                g.add((g.base[f'{l}_v_ku_sense_concept'], ns_d['rdf'].type, ns_d['ontolex'].LexicalConcept))
                # :monastery_n_en_sense_concept skos:definition "monk's residence"@en .
                g.add((g.base[f'{l}_v_ku_sense_concept'], ns_d['skos'].definition, Literal(meaning_t, lang='ku')))
            if 'examples' in meaning_d.keys():
                # Examples
                # :monastery_n_en_sense lexicog:usageExample :monastery_n_en_sense_ex .
                g.add((g.base[f'{l}_v_ku_sense'], ns_d['ontolex'].usageExample, g.base[f'{l}_v_ku_sense_ex']))
                example_t = meaning_d['examples']
                # :monastery_n_en_sense_ex rdf:value "We visited a Buddhist monastery deep in a jungle."@en;
                g.add((g.base[f'{l}_v_ku_sense_ex'], ns_d['rdf'].value, Literal(example_t, lang='ku')))
    if 'translations' in val_d.keys():
        translation_d = val_d['translations']
        for key in translation_d.keys():
            # Translations
            if key == 'en':
                en_translation_l = translation_d['en']
                for tr_t in en_translation_l:
                    # :monasterio_n_es a ontolex:LexicalEntry .
                    g.add((g.base[f'{l}_v_en'], ns_d['rdf'].type, ns_d['ontolex'].LexicalEntry))
                    # :monastery_n_en_sense-monasterio_n_es_sense-tr a vartrans:Translation .
                    g.add((g.base[f'{l}_v_ku_en-tr'], ns_d['rdf'].type, ns_d['vartrans'].Translation))
                    # :monastery_n_en_sense-monasterio_n_es_sense-tr vartrans:source :monastery_n_en_sense .
                    g.add((g.base[f'{l}_v_ku_en-tr'], ns_d['vartrans'].source, g.base[f'{l}_v_ku_sense']))
                    # :monastery_n_en_sense-monasterio_n_es_sense-tr vartrans:target :monasterio_n_es_sense .
                    g.add((g.base[f'{l}_v_ku_en-tr'], ns_d['vartrans'].target, g.base[f'{l}_v_en_sense']))
                    # :monastery_n_en ontolex:sense :monastery_n_en_sense .
                    g.add((g.base[f'{l}_v_en'], ns_d['ontolex'].sense, g.base[f'{l}_v_en_sense']))
                    # :monastery_n_en_sense a ontolex:LexicalSense .
                    g.add((g.base[f'{l}_v_en_sense'], ns_d['rdf'].type, ns_d['ontolex'].LexicalSense))
                    # :monastery_n_en_sense ontolex:isLexicalizedSenseOf :monastery_n_en_sense_concept .
                    g.add((g.base[f'{l}_v_en_sense'], ns_d['ontolex'].isLexicalizedSenseOf, g.base[f'{l}_v_en_sense_concept']))
                    # :monastery_n_en_sense_concept a ontolex:LexicalConcept .
                    g.add((g.base[f'{l}_v_en_sense_concept'], ns_d['rdf'].type, ns_d['ontolex'].LexicalConcept))
                    # :monastery_n_en_sense_concept skos:definition "monk's residence"@en .
                    g.add((g.base[f'{l}_v_en_sense_concept'], ns_d['skos'].definition, Literal(tr_t, lang='en')))
            elif key == 'tr':
                tr_translation_l = translation_d['tr']
                for tr_t in tr_translation_l:
                    # :monasterio_n_es a ontolex:LexicalEntry .
                    g.add((g.base[f'{l}_v_tr'], ns_d['rdf'].type, ns_d['ontolex'].LexicalEntry))
                    # :monastery_n_en_sense-monasterio_n_es_sense-tr a vartrans:Translation .
                    g.add((g.base[f'{l}_v_ku_tr-tr'], ns_d['rdf'].type, ns_d['vartrans'].Translation))
                    g.add((g.base[f'{l}_v_ku_tr-tr'], ns_d['vartrans'].source, g.base[f'{l}_v_ku_sense']))
                    # :monastery_n_en_sense-monasterio_n_es_sense-tr vartrans:target :monasterio_n_es_sense .
                    g.add((g.base[f'{l}_v_ku_tr-tr'], ns_d['vartrans'].target, g.base[f'{l}_v_tr_sense']))
                    # :monastery_n_en ontolex:sense :monastery_n_en_sense .
                    g.add((g.base[f'{l}_v_tr'], ns_d['ontolex'].sense, g.base[f'{l}_v_tr_sense']))
                    # :monastery_n_en_sense a ontolex:LexicalSense .
                    g.add((g.base[f'{l}_v_tr_sense'], ns_d['rdf'].type, ns_d['ontolex'].LexicalSense))
                    # :monastery_n_en_sense ontolex:isLexicalizedSenseOf :monastery_n_en_sense_concept .
                    g.add((g.base[f'{l}_v_tr_sense'], ns_d['ontolex'].isLexicalizedSenseOf, g.base[f'{l}_v_tr_sense_concept']))
                    # :monastery_n_en_sense_concept a ontolex:LexicalConcept .
                    g.add((g.base[f'{l}_v_tr_sense_concept'], ns_d['rdf'].type, ns_d['ontolex'].LexicalConcept))
                    # :monastery_n_en_sense_concept skos:definition "monk's residence"@en .
                    g.add((g.base[f'{l}_v_tr_sense_concept'], ns_d['skos'].definition, Literal(tr_t, lang='tr')))

# save graph
g.serialize(destination='ferhengo-ontolex-graph.ttl')
