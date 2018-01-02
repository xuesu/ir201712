# -*- coding: UTF-8 -*-
import datetime
import json

import mes_holder
import utils
import text_extractor


class PlainPredictor:
    def __init__(self):
        with open(mes_holder.DEFAULT_EMOTION_DATASET_PATH) as fin:
            self.emotion = json.load(fin)
        with open(mes_holder.DEFAULT_DEGREE_DATASET_PATH) as fin:
            self.degree = json.load(fin)
        self.word_parser = text_extractor.parser_holder.get_parser()

    def get_score(self, node, lang):
        has_score = False
        child_phrases = []
        child_scores = []
        if node.childrenAsList.size() > 0:
            for child in node.childrenAsList:
                child_score, child_has_score, child_phrase = self.get_score(child, lang)
                if child_has_score:
                    has_score = True
                child_scores.append(child_score)
                child_phrases.append(child_phrase)
        if node.childrenAsList.size() == 0:
            phrase = node.label().value()
        else:
            phrase = child_phrases[0]
            for i, child in enumerate(node.childrenAsList):
                if i == 0:
                    continue
                if lang == 'zh':
                    phrase = phrase + child_phrases[i]
                else:
                    if child.label().value() == '.' or child_phrases[i] == "n't":
                        phrase += child_phrases[i]
                    else:
                        phrase += ' ' + child_phrases[i]
        if phrase in self.emotion:
            score = self.emotion[phrase]
            has_score = True
        else:
            if phrase in self.degree:
                score = self.degree[phrase]
                has_score = True
            else:
                d = 0
                e = 0
                for i, child in enumerate(node.childrenAsList):
                    if child.label().value() in mes_holder.DEFAULT_ADV_LABEL:
                        d += child_scores[i]
                    else:
                        e += child_scores[i]
                if d == 0:
                    score = e
                elif node.label().value() in mes_holder.DEFAULT_ADV_LABEL:
                    score = d
                else:
                    score = d * e
        return score, has_score, phrase

    def predict(self, words, lang='zh'):
        trees = self.word_parser.parse(words, lang)
        score = 0
        has_score = False
        for tree in trees:
            sub_score, sub_has_score, _ = self.get_score(tree, lang)
            score += sub_score
            if sub_has_score:
                has_score = True
        if score < 0:
            return -1  # negative
        elif score == 0 and not has_score:
            return 1  # subjective
        elif score > 0:
            return 0  # positive
        else:
            return 2  # contradict

    def get_test_accuracy(self, col_name, lang):
        start_time = datetime.datetime.now()
        tt_num = 0
        records = [record for record in utils.get_docs(col_name).find({"fold_id": 0})]
        for i, record in enumerate(records):
            if len(record['words']) < 200:
                logit = self.predict(record['words'], lang)
                if logit == record['tag']:
                    tt_num += 1
            if i % 100 == 0:
                accuracy = tt_num * 100.0 / (i + 1)
                now_time = datetime.datetime.now()
                print 'Spend %d seconds, %d records, accuracy: %.2f%%' % ((now_time - start_time).seconds, i + 1, accuracy)
        accuracy = tt_num * 100.0 / len(records)
        now_time = datetime.datetime.now()
        print 'Spend %d seconds, accuracy: %.2f%%' % ((now_time - start_time).seconds, accuracy)
        return accuracy


if __name__ == '__main__':
    predictor = PlainPredictor()
    print predictor.get_test_accuracy('nlpcc_zh', 'zh')
