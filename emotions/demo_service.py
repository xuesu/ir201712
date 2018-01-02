# coding=utf-8

import flask
import functools
import flask_api
import json
import traceback

import utils
import demo_exceptions
import predict_NOLSTM
import mes_holder

app = flask.Flask('demo')
logger = utils.init_logger("demo")

predictors = {
    "nlpcc_zh_NOLSTM": predict_NOLSTM.PredictorNOLSTM('nlpcc_zh', 'ir', trainable=False)
}


def service_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        content = {
            "msg": "",
            "data": {},
            "url": "",
            "error": {"type": "", "message": "", "message_chs": ""}
        }
        headers = {"content-type": "application/json"}
        try:
            return func(*args, **kw)
        except (AssertionError, ValueError, TypeError) as e:
            content["error"]["type"] = "FormatError"
            content["error"]["message"] = "The input format is invalid. EXCEPTION: {}".format(e)
            content["error"]["message_chs"] = "格式或值无效"
            logger.error(func.__name__ + " failed, MESSAGE: " + content["error"]["message"] +
                         "TRACEBACK: " + traceback.format_exc())
            return json.dumps(content), flask_api.status.HTTP_400_BAD_REQUEST, headers
        except demo_exceptions.DEMOBaseException as e:
            content["error"]["type"] = e.error_code
            content["error"]["message"] = e.message
            content["error"]["message_chs"] = e.ch_message
            logger.error(func.__name__ + " failed, MESSAGE: " + content["error"]["message"] +
                         "TRACEBACK: " + traceback.format_exc())
            return json.dumps(content), e.status_code, headers
        except KeyError as e:
            content["error"]["type"] = "InvalidInput"
            content["error"]["message"] = "The request param error, a required parameter was missing. " \
                                          "Exception: {}".format(e)
            content["error"]["message_chs"] = "键缺失"
            logger.error(func.__name__ + " failed, MESSAGE: " + content["error"]["message"] +
                         "TRACEBACK: " + traceback.format_exc())
            return json.dumps(content), flask_api.status.HTTP_400_BAD_REQUEST, headers
        except Exception as e:
            content["error"]["type"] = "InternalServerError"
            content["error"]["message"] = "Internal Server Error. EXCEPTION: " + str(e)
            content["error"]["message_chs"] = "服务器内部错误"
            logger.error(func.__name__ + " failed, MESSAGE: " + content["error"]["message"] +
                         "TRACEBACK: " + traceback.format_exc())
            return json.dumps(content), flask_api.status.HTTP_500_INTERNAL_SERVER_ERROR, headers
    return wrapper


@app.route("/predict/", methods=["POST"])
@service_exception_handler
def prediction():
    content = {"msg": "", "data": {}, "url": "",
               "error": {"type": "", "message": "", "message_chs": ""}}
    headers = {"content-type": "application/json"}
    text = flask.request.form["text"]
    # print text
    # model_type = flask.request.form["model_type"]
    # col_name = flask.request.form["col_name"]
    model_type = "NOLSTM"
    col_name = "nlpcc_zh"
    op = "{}_{}".format(col_name, model_type)
    resp = predictors[op].predict(text)
    content["data"] = resp
    return json.dumps(content), flask_api.status.HTTP_200_OK, headers


@app.route("/", methods=["GET"])
@service_exception_handler
def index():
    return flask.render_template('index.html')

if __name__ == "__main__":
    app.run(host="localhost", debug=True, port=mes_holder.DEFAULT_API_PORT)
