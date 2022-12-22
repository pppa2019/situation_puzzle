import nltk
import gensim
import gensim.downloader as api
def get_answer(KG, q_text):
    """retrivel KG to answer the "yes/no" question by judging if there exist matching path in graph.

    Args:
        KG (dict): graph dict, inculding entity mapper, relation list and event list
        q_text (string): input question
    
    Return:
        result (string): Yes/No/Irrelevent
    """
    return


if __name__=='__main__':
    from gensim.models import KeyedVectors, Phrases
    from gensim.test.utils import datapath
    from sklearn.metrics.pairwise import cosine_similarity
    wv_from_bin = KeyedVectors.load_word2vec_format(datapath("/data/chenyijie/pretrained/GoogleNews/GoogleNews-vectors-negative300.bin"), binary=True)
    # phrase_from_bin = Phrases.load()
    print(wv_from_bin.most_similar("car"))
    def word2vec_similarity(word1, word2):
        word_vec1 = wv_from_bin.get_vector(word1).reshape(1, -1)
        word_vec2 = wv_from_bin.get_vector(word2).reshape(1, -1)
        return cosine_similarity(word_vec1, word_vec2)
    def bert_similarity(word1, word2):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        #Compute embedding for both lists
        embedding_1= model.encode(word1, convert_to_tensor=True)
        embedding_2 = model.encode(word2, convert_to_tensor=True)
        return  cosine_similarity(embedding_1.reshape(1, -1).cpu(), embedding_2.reshape(1, -1).cpu())
    import ipdb;ipdb.set_trace()