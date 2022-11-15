from collections import defaultdict
import os
os.environ['CUDA_VISIBLE_DEVICES']  = '1,7'
import amrlib
from nltk.stem import WordNetLemmatizer
# from nltk import pos_tag
from fuzzywuzzy import fuzz
import spacy
amrlib.setup_spacy_extension()
nlp = spacy.load('en_core_web_sm')
examples = [
    "He jump down and then caught the cat.",
    "Two women are talking.  One goes into the bathroom, comes out five minutes later, and kills the other.",
    "A man is sitting in a room. Another person enters, carrying a closed cardboard box, and sits down nearby. Though the first man can't see, hear, or smell the box's contents, he knows what's in the box."
]

def convert_AMR2EventGraph(instance_dict, relation_triples, raw_sent):
    span_type = ['Head_End', "Att_span", "Event"]
    relationship_type = [
        [span_type[0], "Entity_att", span_type[1]], #ARG2 or mod
        [span_type[2], "Head", span_type[0]], # ARG0
        [span_type[2], "End", span_type[0]], # ARG1
        [span_type[0], "EntityPartOf", span_type[0]],
        [span_type[0], "EntityEqual", span_type[1]],
        [span_type[2], "EventSameTime", span_type[2]],
        [span_type[2], "EventCause", span_type[2]],
        [span_type[2], "EventTemporal", span_type[2]],
        [span_type[2], "EventEqual", span_type[2]],
        [span_type[2], "Event_att", span_type[0]],
    ]
    amr_converter = {
        ':ARG0': relationship_type[1],
        ':ARG1': relationship_type[2],
        # ':ARG2': relationship_type[0],
        ':mod': relationship_type[0]
    }
    word_list = raw_sent.split()

    span_dict = {}
    relation_dict  = {}
    event_dict = {}
    instance2spanid = {}
    instance2eventid = {}
    event_entity_dict = defaultdict(list)


    def fuzzy_match_word(word):
        threashold = 70
        max_score = 0
        best_match = None
        wnl = WordNetLemmatizer()
        # if word=='talk':
        #     import ipdb;ipdb.set_trace()
        if word not in word_list:
            for origin_word in word_list:
                lemma_word = wnl.lemmatize(origin_word, 'v')
                lemma_word = wnl.lemmatize(lemma_word, 'n')
                match_score = fuzz.ratio(word, lemma_word)
                if match_score>=threashold:
                    if match_score>max_score:
                        best_match = origin_word               
            return best_match
        return word

    for item in relation_triples:
        if  item[1] in amr_converter.keys():
            schema = amr_converter[item[1]]
            span_type0 = schema[0]
            relation = schema[1]
            span_type1 = schema[2]
            instance0 = fuzzy_match_word(instance_dict[item[0]])
            if instance0 is None:
                continue
            instance1 = fuzzy_match_word(instance_dict[item[2]])
            if instance1 is None:
                continue
            span0_start = raw_sent.index(instance0)
            span0_end = span0_start + len(instance0)
            span1_start = raw_sent.index(instance1)
            span1_end = span1_start + len(instance1)
            if instance0 not in instance2spanid:
                span_dict[f'T{len(span_dict)+1}'] = [span_type0, str(span0_start), str(span0_end), instance0]
                instance2spanid[instance0] =  f'T{len(span_dict)}'
            if instance1 not in instance2spanid:
                span_dict[f'T{len(span_dict)+1}'] = [span_type1, str(span1_start), str(span1_end), instance1]
                instance2spanid[instance1] =  f'T{len(span_dict)}'
            # event triples contain event and event's relationships
            if span_type0==span_type[2] and span_type1!=span_type[2]:
                event = instance0
                if event not in instance2eventid:
                    instance2eventid[event] = f'E{len(event_dict)+1}'
                if instance2eventid[event] not in event_dict:
                    event_dict[instance2eventid[event]] = [f'Event:{instance2spanid[instance0]}']
                if instance2spanid[instance1] not in event_entity_dict[instance2eventid[event]]:
                    event_entity_dict[instance2eventid[event]].append(instance2spanid[instance1])
                    event_dict[instance2eventid[event]].append(f'{relation}:{instance2spanid[instance1]}')
            # event event relationship

            # entity entity relationship

            # attribuite recognization
            # TODO: remove replicated triples
            if 'att' in schema[1]:
                # import ipdb;ipdb.set_trace()
                relation_dict[f"R{len(relation_dict)+1}"] = [schema[1], f'Arg1:{instance2spanid[instance1]}', f'Arg2:{instance2spanid[instance0]}']

    # import ipdb;ipdb.set_trace()
    return span_dict, relation_dict, event_dict

idx = 0
for example in examples:
    doc = nlp(example)
    graphs, sent_triples = doc._.to_amr()
    for sent, graph, triples in zip(doc.sents, graphs, sent_triples):
        # import ipdb;ipdb.set_trace()
        sent = sent.text
        print(graph)
        # import ipdb;ipdb.set_trace()
        relation_triples = []
        instance_dict = {}
        for item in triples:
            if item[1]==':instance':
                instance_dict[item[0]] = item[2].split('-')[0]
            else:
                relation_triples.append(item)
        span_dict, relation_dict, event_dict = convert_AMR2EventGraph(instance_dict, relation_triples, sent)
        print(span_dict)
        print(event_dict)
        # import ipdb;ipdb.set_trace()
        print('\n' + '*-'*50+'\n')
        with open(f'/data/chenyijie/software/brat/data/amr_test_ann/{idx}.txt', 'w') as f:
            f.write(sent+'\n')
        with open(f'/data/chenyijie/software/brat/data/amr_test_ann/{idx}.ann', 'w') as f:
            for key, value in span_dict.items():
                f.write(key+'\t'+' '.join(value[:-1])+'\t'+value[-1]+'\n')
            for key, value in event_dict.items():
                f.write(key+'\t'+' '.join(value)+'\n')
            for key, value in relation_dict.items():
                f.write(key+'\t'+' '.join(value)+'\n')
        idx += 1
