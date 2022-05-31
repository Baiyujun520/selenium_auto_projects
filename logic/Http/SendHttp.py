import os.path

import requests
import time
import base64
import json
import random

from common.LoggerHelper import logger

header = {"Sec-Fetch-Mode": "cors", "Referer": "https://try.shengtai.cmccsi.cn/police/survey-user/police_competition"
                                               "/login.html", "Sec-Fetch-Site": "same-origin",
          "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
          "Accept": "application/json, text/javascript, */*; q=0.01",
          "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"100\", \"Microsoft Edge\";v=\"100\"",
          "Content-Type": "application/json", "Accept-Encoding": "gzip, deflate, br",
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44 ",
          "sec-ch-ua-mobile": "?0",
          "sec-ch-ua-platform": "\"Windows\"",
          "Sec-Fetch-Dest": "empty"}

host = "https://try.shengtai.cmccsi.cn"


def get_time():
    now = time.time() * 1000
    time_str = str(long(round(now)))
    tmp = base64.standard_b64encode(time_str)
    return tmp, time_str


def send_http(url, param, headers=header):
    respond = requests.get(host + url, params=param, headers=headers)
    request_body = respond.request.body
    return respond.content


def mentor_login(identity):
    tmp, time_str = get_time()
    param = {"identityCard": identity, "tmp": tmp, "timeStamp": time_str}
    url = "/police/survey-user/survey-admin-api/mentorLogin"
    respond = requests.get(host + url, params=param, headers=header)
    request_body = respond.request.path_url
    logger.debug("mentor_login request: %s", str(request_body))
    response = respond.content
    logger.info("mentor_login response_body: %s", str(response).decode("utf-8"))
    response_body = json.loads(response)
    team_id = response_body["teamId"]
    user_id = response_body["userId"]
    token = response_body["token"]
    header["Authorization"] = token
    respond.close()
    return team_id, user_id, token


def get_round_id(response_body, user_id):
    round_id = None
    round_list = []
    for data in response_body["data"]:
        status = data.get("status")
        round_list.append(data.get("roundId"))
        if status == 1:
            round_id = data.get("roundId")
            break
    if round_id is None:
        logger.error("user_id: %s - round id is None!!!", str(user_id))
        round_id = min(round_list)
        logger.info("user_id: %s - min round id: %s", str(user_id), str(round_id))
    return round_id


def round_round(user_id):
    url = "/police/survey-user/survey-admin-api/contest/round/round/"
    domain_name = host + url + str(user_id)
    respond = requests.get(domain_name, headers=header)
    request_body = respond.request.path_url
    logger.debug("round/round request: %s", str(request_body))
    response_body = respond.content
    logger.info("round/round response body: %s", str(response_body).decode("utf-8"))
    response_json = json.loads(response_body)
    round_id = get_round_id(response_json, user_id)
    respond.close()
    # round_id = 65
    return round_id


def check_code(respond_body, user_id):
    respond_json = json.loads(respond_body)
    if respond_json.get("code") == 200:
        logger.info("save answers response body: %s", str(respond_body).decode("utf-8"))
    else:
        logger.error("save answers response error, user id: %s", str(user_id))


def save_answers(user_id, team_id, round_id):
    url = "/police/survey-user/survey-admin-api/contest/answer/saveAnswers"
    answers_list = [{
        "examId": "1",
        "examItem": "1"
    }]
    score = random.randint(0, 100)
    logger.info("user id: %s - score: %s", str(user_id), str(score))
    request_body = {"userId": user_id, "roundId": str(round_id), "teamId": str(team_id), "answerVoList": answers_list,
                    "score": score}
    json_data = json.dumps(request_body)
    respond = requests.post(host + url, data=json_data, headers=header)
    request_body = respond.request.body
    logger.debug("save answers request body: %s", str(request_body))
    respond_body = respond.content
    check_code(respond_body, user_id)
    respond.close()
    return score


def test(identity):
    team_id, user_id, token = mentor_login(identity=identity)
    # round_id = round_round(user_id=user_id)
    # score = save_answers(user_id, team_id, str(round_id))
    score = 0
    return score


def read_txt():
    code_list = []
    path = os.path.dirname(__file__)
    txt_file = os.path.join(path, "code.txt")
    code_file = open(txt_file, "r")
    file_data = code_file.readlines()
    for code_data in file_data:
        code_data = code_data.strip("\n")
        code_list.append(code_data)
    code_file.close()
    return code_list


if __name__ == "__main__":
    id_list = read_txt()
    all_score = 0
    for code in id_list:
        single_score = test(code)
        all_score = all_score + single_score
    logger.info("All score is: %s", all_score)
