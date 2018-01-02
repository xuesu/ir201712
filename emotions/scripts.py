# -*- coding: utf-8 -*-
import codecs
import json
import os
import random
import re
import string
import sys
import xml.dom.minidom as minidom

import mes_holder
import text_extractor
import utils
import predict_NOLSTM


def draw_words_num(col_name):
    import matplotlib.pyplot as plt
    import pymongo
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    records = docs.find()
    x = [len(record["words"]) for record in records]
    maxx = max(x)
    print('max: ', maxx)
    n, bins, patches = plt.hist(x, 50, facecolor='b', alpha=0.8)
    plt.xlabel("Number of Words")
    plt.ylabel("Frequency")
    plt.savefig("wordsnum_{}.png".format(col_name))
    plt.show()
    plt.axis('tight')


def draw_several_accuracy_plots(in_names, labels, gap, sz, title):
    assert(len(in_names) == len(labels))
    train_accuracies = []
    valid_accuracies = []
    test_accuracies = []
    x = [i * gap for i in range(sz)]
    num = len(in_names)
    for in_name in in_names:
        with open(in_name) as fin:
            data = json.load(fin)
            train_accuracies.append(data[0][:sz])
            valid_accuracies.append(data[1][:sz])
            if len(data) > 2:
                test_accuracies.append(data[2][:sz])
            else:
                test_accuracies.append([])
    alpha_start = 0.1
    alpha_end = 1.0
    alpha_gap = (alpha_end - alpha_start) / num
    train_color = 'g'
    valid_color = 'b'
    test_color = 'c'
    for i in range(num):
        alpha = alpha_end - alpha_gap * i
        # if len(train_accuracies[i]) > 0:
        #     plt.plot(x, train_accuracies[i], color=train_color, alpha=alpha, label=labels[i] + " train")
        if len(valid_accuracies[i]) > 0:
            plt.plot(x, valid_accuracies[i], color=valid_color, alpha=alpha, label=labels[i] + " valid")
        if len(test_accuracies[i]) > 0:
            plt.plot(x, test_accuracies[i], color=test_color, alpha=alpha, label=labels[i] + " test")
    plt.xlabel("Training Iteration")
    plt.ylabel("Accuracy(%)")
    plt.axis('tight')
    plt.title(title)
    plt.legend(loc='upper left')
    plt.savefig(title + ".png")
    plt.show()


def show_text_by_tag(col_name, tag, limit, feature=False, plainword=False, rank=None, words_num_min=0, words_num_max=1e5, rareword=False):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    query = {}
    if tag is not None:
        query["tag"] = tag
    if rank is not None:
        query["rank"] = rank
    records = docs.find(query)
    records = [record for record in records
               if words_num_min < len(record['words']) < words_num_max]
    if rareword:
        new_records = []
        for record in records:
            for word in record['words']:
                if mes_holder.DEFAULT_RARE_WORD in word:
                    new_records.append(record)
                    break
        records = new_records
        del new_records
    random.shuffle(records)
    records = records[:limit]
    fnum = len(records[0]['words'][0])
    for record in records:
        words = [[] for _ in range(fnum)]
        print 'Text:', record["text"]
        if plainword:
            words_infos = []
            for word in record['words']:
                # print word
                words_infos.append('[' + ','.join([unicode(w) for w in word]) + ']')
            print 'Words:', ','.join(words_infos)
        if feature:
            for word in record['words']:
                for i in range(fnum):
                    words[i].append(word[i])
            for i in range(fnum):
                print 'Feature %d:' % i, u' '.join([unicode(word) for word in words[i]])


def restore_semval_14(col_name, fname):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    cutter = text_extractor.WordParser()
    tree = minidom.parse(fname)
    sentences = tree.documentElement.getElementsByTagName("sentence")
    polarity2tag = {"negative": 0, "neutral": 1, "positive": 2, "conflict": 3}
    for sentence in sentences:
        record = dict()
        text = sentence.getElementsByTagName("text")[0].firstChild.data
        record["text"] = text
        record["words"] = cutter.split(text, 'en')
        words = [word[0] for word in record["words"]]
        record["aspectTerm"] = []
        aspect_terms = sentence.getElementsByTagName("aspectTerm")
        inds = [0] * len(text)
        ind = 0
        for i, word in enumerate(words):
            for char in word:
                while text[ind] != char and text[ind].isalnum():
                    inds[ind] = inds[ind - 1] if ind > 0 else 0
                    ind += 1
                inds[ind] = i
                ind += 1
        for aspect in aspect_terms:
            term = {
                "term": aspect.getAttribute("term"),
                "polarity": polarity2tag[aspect.getAttribute("polarity")],
                "from": int(aspect.getAttribute("from")),
                "to": int(aspect.getAttribute("to"))
            }
            record["aspectTerm"].append(term)
            for i in range(term["from"], term["to"]):
                record["words"][inds[i]][2] = term["polarity"]
        record["tag"] = [word[2] for word in record["words"]]
        docs.save(record)
    print "Save %d sentences." % len(sentences)


def restore_imdb(col_name, dir_name, tag, is_train):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    cutter = text_extractor.WordParser()
    for root, dirs, files in os.walk(dir_name):
        for fname in files:
            record = {}
            with open(os.path.join(root, fname)) as fin:
                record['text'] = fin.read()
            record['text'] = "".join(char for char in record['text'] if char in string.printable)
            record['text'] = record['text'].replace("<br />", '\n')
            print record['text']
            record['tag'] = tag
            record['words'] = cutter.split(record['text'], lang='en')
            record['is_train'] = is_train
            if not is_train:
                record['fold_id'] = 0
            docs.save(record)


def restore_nlpcc(col_name, fname, tag, lang, is_train):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    cutter = text_extractor.WordParser()
    with open(fname) as fin:
        content = fin.read()
    content = content.replace('&', '##AND##')
    tree = minidom.parseString(content)
    reviews = tree.documentElement.getElementsByTagName("review")
    for review in reviews:
        record = dict()
        text = review.firstChild.data
        text = text.replace('##AND##', '&').strip()
        if lang == 'en':
            text = "".join(char for char in text if char in string.printable)
        text = text.replace('\n\r', '\n').replace('\r', '\n').replace('\n\n', '\n')
        record["text"] = text
        if tag is not None:
            record['tag'] = tag
        else:
            record['tag'] = int(review.getAttribute('label')) - 1
        record["words"] = cutter.split(text, lang)
        record['is_train'] = is_train
        if not is_train:
            record['fold_id'] = 0
        docs.save(record)
    del cutter


def insert_emotion(word, tag, emotion, forbidden):
    if word not in forbidden:
        if word in emotion and tag != emotion[word]:
            if emotion[word] * tag < 0:
                print 'Pop', word
                emotion.pop(word)
                forbidden.add(word)
                return
            elif abs(tag) < abs(emotion[word]):
                emotion[word] = tag
        if word not in emotion:
            emotion[word] = tag


def get_emotion(path, outfname):
    emotion = {}
    forbidden = set()
    for root, dir, fnames in os.walk(path):
        for fname in fnames:
            with codecs.open(os.path.join(root, fname), 'r', 'utf8') as fin:
                op = float(fin.readline())
                texts = [text.strip() for text in fin.readlines() if text.strip()]
                if op != 0:
                    for text in texts:
                        insert_emotion(text, op, emotion, forbidden)
                else:
                    for text in texts:
                        infos = re.split('\s', text)
                        score = float(infos[-1])
                        word = ' '.join(infos[:-1])
                        insert_emotion(word, score, emotion, forbidden)
    with codecs.open(outfname, 'w', 'utf8') as fout:
        json.dump(emotion, fout)


def run():
    print ('col_name:', sys.argv[1])
    print ('model_type', sys.argv[2])
    model_name = raw_input("Please input model name:")
    if sys.argv[2] == 'LSTM':
        predictor = predict_LSTM.PredictorLSTM(sys.argv[1], model_name)
    elif sys.argv[2] == 'NOLSTM':
        predictor = predict_NOLSTM.PredictorNOLSTM(sys.argv[1], model_name)
    elif sys.argv[2] == 'ABSA_LSTM':
        predictor = predict_ABSA_LSTM.PredictorABSALSTM(sys.argv[1], model_name)
    elif sys.argv[2] == 'ABSA_NOLSTM':
        predictor = predict_ABSA_NOLSTM.PredictorABSANOLSTM(sys.argv[1], model_name)
    else:
        raise ValueError
    predictor.train()


def divide_fold_imdb(col_name, fold_num=11):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    records = [record for record in docs.find({"fold_id": {"$ne": 0}})]
    random.shuffle(records)
    fold_sz = (len(records) + fold_num - 1) / fold_num
    for i, record in enumerate(records):
        record["fold_id"] = i / fold_sz + 1
        docs.save(record)
    print 'Dataset Fold Divided!'


def count_word_num(col_name):
    docs = pymongo.MongoClient("localhost", 27017).paper[col_name]
    records = [record for record in docs.find({"fold_id": {"$ne": 0}})]
    words = set()
    for record in records:
        for word in record['words']:
            words.add(word[0])
    return len(words)


def lemmarize(col_name):
    import nltk
    docs = utils.get_docs(col_name)
    stemmer = nltk.stem.SnowballStemmer("english")
    for record in docs.find():
        for word in record['words']:
            word[4] = stemmer.stem(word[4])
        docs.save(record)


if __name__ == '__main__':
    # show_text_by_tag("nlpcc_zh", 0, 200, False, False)
    restore_nlpcc('nlpcc_zh', 'data/nlpcc_zh/test.label.cn.txt', None, 'zh', True)
