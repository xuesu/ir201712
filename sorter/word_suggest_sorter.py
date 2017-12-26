class Word_Suggest_Sorter(object):
    def __init__(self):
        pass

    def mysort(self, words):
        words_graded = [(word.cf / word.df, word) for word in words]
        words_graded.sort(reverse=True)
        return [word_grade[1] for word_grade in words_graded]