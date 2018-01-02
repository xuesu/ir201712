import pymongo

if __name__ == '__main__':
    hownet = pymongo.MongoClient("localhost", 27017).paper.hownet
    while raw_input("quit?y/n") != 'y':
        label = raw_input("Please input the Label:")
        value = input("Please input the Value:")
        while True:
            word = raw_input("").strip()
            if len(word) == 0:
                continue
            if word == 'q':
                break
            hownet.save({"word":word, "label":label, "value":value})
