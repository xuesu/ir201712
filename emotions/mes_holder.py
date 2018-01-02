import os
import json
import yaml

DEFAULT_DATA_DIR = "data"
DEFAULT_CONFIG_DIR = "config"
DEFAULT_LOG_DIR = "log"
DEFAULT_META_DIR = "meta"
DEFAULT_MODEL_DIR = "model"
DEFAULT_MODEL_NAME = "m"
DEFAULT_CONFIG_FNAME = "config.yml"
DEFAULT_FEATURE_FNAME_FORMAT = "feature{}.json"
DEFAULT_FEATURE_IDS_FNAME_FORMAT = "feature{}_ids.json"
DEFAULT_FEATURE_EMB_FNAME_FORMAT = "feature{}_emb.json"
DEFAULT_FEATURE_FREQ_FNAME_FORMAT = "feature{}_freq.json"
DEFAULT_EMOTION_DATASET_FNAME = "emotion.json"
DEFAULT_DEGREE_DATASET_FNAME = "degree.json"
DEFAULT_EMOTION_DATASET_PATH = os.path.join(DEFAULT_DATA_DIR, DEFAULT_EMOTION_DATASET_FNAME)
DEFAULT_DEGREE_DATASET_PATH = os.path.join(DEFAULT_DATA_DIR, DEFAULT_DEGREE_DATASET_FNAME)
DEFAULT_API_PORT = 8090
DEFAULT_RARE_WORD = "RareWord"
DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = 27017
DEFAULT_MONGO_DB = "paper"
DEFAULT_ADV_LABEL = {"RB", "AD", "VE"}

# -1 neg 0 pos 1 neural 2 contradict


class Mes:
    def __init__(self, train_col, model_type, model_name, config_fname=None):
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        self.train_col = train_col
        self.model_type = model_type
        assert(model_type in ["ABSA_LSTM", "ABSA_NOLSTM", "LSTM", "NOLSTM", "Plain", "StandfordParser", "Other"])
        self.model_name = model_name
        self.meta_path = os.path.join(DEFAULT_DATA_DIR, train_col, DEFAULT_META_DIR)
        if not os.path.exists(self.meta_path):
            os.makedirs(self.meta_path)
        self.model_path = os.path.join(DEFAULT_DATA_DIR, train_col,
                                       DEFAULT_MODEL_DIR, model_type, model_name)
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        self.model_save_path = os.path.join(self.model_path, DEFAULT_MODEL_NAME)
        self.model_log_path = os.path.join(self.model_path, DEFAULT_LOG_DIR)
        if not os.path.exists(self.model_log_path):
            os.makedirs(self.model_log_path)
        if config_fname is None:
            config_fname = "{}_{}.yml".format(train_col, model_type)
        config_path = os.path.join(DEFAULT_DATA_DIR, DEFAULT_CONFIG_DIR, config_fname)
        if os.path.exists(config_path):
            with open(config_path, "r") as fin:
                self.config = yaml.load(fin)
                self.lang = self.config['LANG']
            print 'Successfully load {}'.format(config_path)
            print json.dumps(self.config, indent=4, sort_keys=True)
        self.config_path = os.path.join(DEFAULT_DATA_DIR, train_col,
                                        DEFAULT_MODEL_DIR, model_type, model_name, DEFAULT_CONFIG_FNAME)

    def dump(self, config_path=None):
        if config_path is None:
            config_path = self.config_path
        assert(config_path is not None)
        with open(config_path, "w") as fout:
            yaml.dump(vars(self), fout)

    def get_feature_path(self, fid):
        return os.path.join(self.meta_path, DEFAULT_FEATURE_FNAME_FORMAT.format(fid))

    def get_feature_ids_path(self, fid):
        return os.path.join(self.meta_path, DEFAULT_FEATURE_IDS_FNAME_FORMAT.format(fid))

    def get_feature_emb_path(self, fid):
        return os.path.join(self.meta_path, DEFAULT_FEATURE_EMB_FNAME_FORMAT.format(fid))

    def get_feature_freq_path(self, fid):
        return os.path.join(self.meta_path, DEFAULT_FEATURE_FREQ_FNAME_FORMAT.format(fid))

if __name__ == '__main__':
    # Test
    mes = Mes('hotel', 'LSTM', 'test', 'semval14.yml')
    mes.dump()
