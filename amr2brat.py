from collections import defaultdict
import os
os.environ['CUDA_VISIBLE_DEVICES']  = '1,7'
import amrlib
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from fuzzywuzzy import fuzz
import spacy
amrlib.setup_spacy_extension()
nlp = spacy.load('en_core_web_sm')


def load_files(path='assign_annotation/B_folder'):
    examples = {}
    files = os.listdir(path)
    for file in files:
        if '.txt' in file:
            prefix = file.replace('.txt', '')
            with open(os.path.join(path, file), 'r') as f:
                lines = f.readlines()
                examples[prefix] = ' '.join(lines)
    return examples



def merge_multihop_relationship(triples):

    return

def triples2graph(instance_dict, triples, output_path):
    import networkx as nx
    import pydot
    from matplotlib import pyplot as plt
    from networkx.drawing.nx_pydot import graphviz_layout
    
    G = nx.DiGraph()
    pos = []
    label_dict = {}
    abbv2id = {}
    
    for idx, (abbv, word) in enumerate(instance_dict.items()):
        abbv2id[abbv] = idx
        pos.append(word)
    # import ipdb;ipdb.set_trace()
    for triple in triples:
        try:
            G.add_edge(instance_dict[triple[0]], instance_dict[triple[2]], rel=triple[1])
            label_dict[(abbv2id[triple[0]], abbv2id[triple[2]])] = triple[1]
        except:
            pass
    pos = graphviz_layout(G)
    # import ipdb;ipdb.set_trace()
    edge_labels = nx.get_edge_attributes(G, 'rel')
    plt.figure(figsize=(8, 8))
    nx.draw(G, pos, node_size=20, alpha=0.5, node_color="blue", with_labels=True, font_size=15)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=15)
    plt.axis('equal')
    plt.savefig(output_path)
    # import ipdb;ipdb.set_trace()
    addition_relationship = []
    template_dict = {
        'head': None,
        'tail': None,
        'rel': None
    }
    if 'cause' in G:
        print('May have CAUSE relationship.')
    if 'and' in G:
        if len(G['and'])==2:
            nodes =  [item for item in G.neighbors('and')]
            if ({'rel': ':ARG0'} in G[nodes[0]].values()) and ({'rel': ':ARG0'} in G[nodes[1]].values()):
                if 'after' in G[nodes[0]]:
                    relation_dict = template_dict.copy()
                    relation_dict['head'] = nodes[0]
                    relation_dict['tail'] = nodes[1]
                    relation_dict['rel'] = 'EventTemperal'
                    addition_relationship.append(relation_dict)
                elif 'after' in G[nodes[1]]:
                    relation_dict = template_dict.copy()
                    relation_dict['head'] = nodes[1]
                    relation_dict['tail'] = nodes[0]
                    relation_dict['rel'] = 'EventTemperal'
                    addition_relationship.append(relation_dict)
                else:
                    relation_dict = template_dict.copy()
                    relation_dict['head'] = nodes[1]
                    relation_dict['tail'] = nodes[0]
                    relation_dict['rel'] = 'EventSameTime'
                    addition_relationship.append(relation_dict)


        print('May have PartOf or SameTime relationship')
    if "after" in G:
        print('May have temporal relationship')
    if "domain" in edge_labels.values():
        print("May have partof or same relationship")
    return addition_relationship

def convert_AMR2EventGraph(instance_dict, relation_triples, raw_sent, begin_idx, span_dict, event_dict, relation_dict):
    span_type = ['Head_End', "Att_span", "Event"]
    relationship_type = [
        [span_type[0], "Entity_att", span_type[1]], #mod
        [span_type[2], "Head", span_type[0]], # ARG0
        [span_type[2], "End", span_type[0]], # ARG1
        [span_type[0], "EntityPartOf", span_type[0]], # domain op op
        [span_type[0], "EntityEqual", span_type[1]], # domain name op
        [span_type[2], "EventSameTime", span_type[2]], # and op1 op2 event, should preprocess the triples and convert.
        [span_type[2], "EventCause", span_type[2]], # cause, argw w
        [span_type[2], "EventTemporal", span_type[2]], # and op op time after
        [span_type[2], "EventEqual", span_type[2]], # and op op
        [span_type[2], "Event_att", span_type[0]], # ARG2
    ]
    amr_converter = {
        ':ARG0': relationship_type[1],
        ':ARG1': relationship_type[2],
        # ':ARG2': relationship_type[0],
        # ':ARG1-of': relationship_type[6],
        ':mod': relationship_type[0]
    }
    word_list = raw_sent.split()

    # span_dict = {}
    # relation_dict  = {}
    # event_dict = {}
    instance2spanid = {}
    instance2eventid = {}
    event_entity_dict = defaultdict(list)

    def fuzzy_match_word(word):
        threashold = 70
        max_score = 0
        best_match = None
        result_len = 0
        wnl = WordNetLemmatizer()
        if word not in word_list:
            for origin_word in word_list:
                lemma_word = wnl.lemmatize(origin_word, 'v')
                lemma_word = wnl.lemmatize(lemma_word, 'n')
                match_score = fuzz.ratio(word, lemma_word)
                if match_score>=threashold:
                    if match_score>max_score:
                        best_match = origin_word  
                        max_score = match_score
            if best_match is not None:
                result_len = len(best_match)
            return best_match, result_len
        return word, len(word)

    # import ipdb;ipdb.set_trace()
    for item in relation_triples:
        if  item[1] in amr_converter.keys():
            schema = amr_converter[item[1]]
            span_type0 = schema[0]
            relation = schema[1]
            span_type1 = schema[2]
            try:
                instance0, span0_len = fuzzy_match_word(instance_dict[item[0]])
            except:
                continue
            if instance0 is None:
                continue
            try:
                instance1, span1_len = fuzzy_match_word(instance_dict[item[2]])
            except:
                continue
            if instance1 is None:
                continue
            span0_start = raw_sent.index(instance0)
            span0_end = span0_start + span0_len
            span1_start = raw_sent.index(instance1)
            span1_end = span1_start + span1_len
            if instance0 not in instance2spanid:
                span_dict[f'T{len(span_dict)+1}'] = [span_type0, str(span0_start+begin_idx), str(span0_end+begin_idx), instance0]
                instance2spanid[instance0] =  f'T{len(span_dict)}'
            if instance1 not in instance2spanid:
                span_dict[f'T{len(span_dict)+1}'] = [span_type1, str(span1_start+begin_idx), str(span1_end+begin_idx), instance1]
                instance2spanid[instance1] =  f'T{len(span_dict)}'
            # event triples contain event and event's relationships
            if span_dict[instance2spanid[instance0]][0]==span_type[2] and span_dict[instance2spanid[instance1]][0]!=span_type[2]:
                event = instance0
                # import ipdb;ipdb.set_trace()
                if event not in instance2eventid:
                    instance2eventid[event] = f'E{len(event_dict)+1}'
                if instance2eventid[event] not in event_dict:
                    event_dict[instance2eventid[event]] = [f'Event:{instance2spanid[instance0]}']
                if instance2spanid[instance1] not in event_entity_dict[instance2eventid[event]]:
                    event_entity_dict[instance2eventid[event]].append(instance2spanid[instance1])
                    event_dict[instance2eventid[event]].append(f'{relation}:{instance2spanid[instance1]}')
            # event event relationship
            if span_type0==span_type[2] and span_type1==span_type[2]:
                relation_dict[f"R{len(relation_dict)+1}"] = [schema[1], f'Arg1:{instance2spanid[instance1]}', f'Arg2:{instance2spanid[instance0]}']
            # entity entity relationship

            # attribuite recognization
            # TODO: remove replicated triples
            if 'att' in schema[1]:
                relation_dict[f"R{len(relation_dict)+1}"] = [schema[1], f'Arg1:{instance2spanid[instance1]}', f'Arg2:{instance2spanid[instance0]}']

    return span_dict, relation_dict, event_dict

if __name__=='__main__':
    input_path = 'assign_annotation/A_folder'
    output_path = 'assign_annotation/A_auto_annotate'
    examples = load_files(path=input_path)
    for prefix, example in examples.items():
        example = example.strip()
        doc = nlp(example)
        graphs, sent_triples = doc._.to_amr()
        begin_idx = 0
        relation_dict = {}
        span_dict = {}
        event_dict = {}
        sents = []
        for sent, graph, triples in zip(doc.sents, graphs, sent_triples):
            sent = sent.text
            sent = sent.replace('.', '')
            sent = sent.replace(',', ' ')
            sent = sent.replace('?', ' ')
            sent = sent.lower()
            sents.append(sent)
            print(graph)
            relation_triples = []
            instance_dict = {}
            for item in triples:
                if item[1]==':instance':
                    instance_dict[item[0]] = item[2].split('-')[0]
                else:
                    relation_triples.append(item)
            try:
                triples2graph(instance_dict, relation_triples, f'/data/chenyijie/software/brat/data/amr_test_ann/{prefix}.jpg')
            except:
                pass
            span_dict, relation_dict, event_dict = convert_AMR2EventGraph(instance_dict, relation_triples, sent, begin_idx, span_dict, event_dict, relation_dict)
            begin_idx += len(sent)+2
            print(span_dict)
            print(relation_dict)
            print(event_dict)
            print('\n' + '*-'*50+'\n')
        with open(os.path.join(output_path, f'{prefix}.txt'), 'w') as f:
            f.write('. '.join(sents)+'\n')
        with open(os.path.join(output_path, f'{prefix}.ann'), 'w') as f:
            for key, value in span_dict.items():
                f.write(key+'\t'+' '.join(value[:-1])+'\t'+value[-1]+'\n')
            for key, value in event_dict.items():
                f.write(key+'\t'+' '.join(value)+'\n')
            for key, value in relation_dict.items():
                f.write(key+'\t'+' '.join(value)+'\n')
