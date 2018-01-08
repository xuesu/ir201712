import gensim
from sklearn.externals import joblib
import jieba


def corpora_process(raw_corpora):
    corpora_cut_list = []
    # 切词处理
    for text in raw_corpora:
        corpora_cut_list.append(list(jieba.cut(text)))
    # 生成字典
    dictionary = gensim.corpora.Dictionary(corpora_cut_list)
    # 存储字典
    dictionary.save('./models/dictionary.mtx')
    #向量语料
    corpora_vector = [dictionary.doc2bow(text) for text in corpora_cut_list]
    # 存储语料库
    gensim.corpora.MmCorpus.serialize('./models/corpus.mtx', corpora_vector)
    # 计算tfidf
    tf_idf_model = gensim.models.TfidfModel(corpora_vector)
    joblib.dump(tf_idf_model, './models/tf_idf_model.pkl')
    # corpora_tfidf = tf_idf_model[corpora_vector]
    # # 数据比较大时事先跑好进行存储
    # return corpora_tfidf


# 使用LSI模型进行相似度计算
def similarity_id(test_data, feature_nums=400,similarity_nums=5):
    '''
    :param feature_nums: 相似度函数中所需要的特征数目
    :param similarity_nums: 返回的相似文档数目
    :param test_data: 用于计算相似度的文档
    :return: 返回列表，列表长度为similarity_nums，列表中每一个元素都为(相似文档id，相似度(浮点型))
    '''
    # 加载tfidf模型、语料库
    tf_idf_model = joblib.load('./models/tf_idf_model.pkl')
    copora_vector = gensim.corpora.MmCorpus('./models/corpus.mtx')
    # 生成tfidf
    copora_tfidf = tf_idf_model[copora_vector]
    # 建立lsi模型
    # lsi模型与similarity都可进行存储
    lsi_model = gensim.models.LsiModel(copora_tfidf)
    corpus_lsi = lsi_model[copora_tfidf]
    # similarity_lsi = similarities.MatrixSimilarity(corpus_lsi)
    # 第一个参数是存储模型，第二个参数：lsi
    # 第三个：feature数目，第四个：是返回最相似条目的个数
    similarity_lsi = gensim.similarities.Similarity('./models/Similarity-LSI-index.pkl',corpus_lsi,
                                             num_features = feature_nums,num_best = similarity_nums)
    # similarity_lsi = similarities.Similarity.load('Similarity-LSI-index.0')

    # 测试
    print()
    test_data_cut = list(jieba.cut(test_data))

    dictionary = gensim.corpora.Dictionary.load('./models/dictionary.mtx')
    test_data_vector = dictionary.doc2bow(test_data_cut)
    test_data_tfidf = tf_idf_model[test_data_vector]
    test_data_lsi = lsi_model[test_data_tfidf]
    return similarity_lsi[test_data_lsi]
