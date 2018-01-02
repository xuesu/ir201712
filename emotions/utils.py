# coding=utf-8

import os
import logging
import numpy
import sys

import mes_holder


def plot_emb(embeddings, labels, filename):
    import matplotlib.pyplot as plt

    from matplotlib.font_manager import FontProperties
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    font = FontProperties('Droid Sans Fallback')
    assert embeddings.shape[0] >= len(labels), 'More labels than embeddings'
    plt.figure(figsize=(15, 15))  # in inches
    for i, label in enumerate(labels):
        x, y = embeddings[i, :]
        plt.scatter(x, y)
        plt.annotate(label, xy=(x, y), xytext=(5, 2), textcoords='offset points',
                     ha='right', va='bottom', fontproperties=font)
    plt.savefig(filename)
    plt.show()


def accuracy(predictions, labels):
    num = 1
    for shape in predictions.shape[:-1]:
        num *= shape
    return (100.0 * numpy.sum(numpy.argmax(predictions, -1) == numpy.argmax(labels, -1))
            / num)


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S')
    file_handler = logging.FileHandler(os.path.join(mes_holder.DEFAULT_LOG_DIR, "{}.log".format(name)))
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def get_groups(s, g):
    return int((s + g - 1) / g)


def get_docs(col_name):
    import pymongo
    return pymongo.MongoClient(mes_holder.DEFAULT_MONGO_HOST, mes_holder.DEFAULT_MONGO_PORT)[mes_holder.DEFAULT_MONGO_DB][col_name]


def get_tag_from_logits(logits):
    max_logit = max(logits)
    ans = 0
    for ans in range(len(logits)):
        if max_logit == logits[ans]:
            break
    return ans - 1
