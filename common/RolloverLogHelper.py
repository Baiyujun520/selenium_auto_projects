# coding=utf-8
import datetime

import os
from common.LoggerHelper import logger


def rollover_log():
    logger.debug("Start to rollover log files...")
    now = datetime.datetime.now()  # 获取当前时间
    delta = datetime.timedelta(days=30)  # 设定30天的日志文件为过期

    cwd = os.getcwd()  # 获取当前执行路径
    project_path = os.path.dirname(os.path.dirname(__file__))
    log_path = os.path.join(project_path, "log")
    os.chdir(log_path)
    delete_num = 0
    for each_file in os.listdir(log_path):
        file_name = os.path.basename(each_file)
        if ".log" in file_name:
            create_time = datetime.datetime.fromtimestamp(os.path.getctime(each_file))
            if create_time < (now - delta):
                try:
                    os.remove(each_file)
                    delete_num = delete_num + 1
                except Exception:
                    continue
        else:
            continue
    if delete_num > 0:
        logger.debug("Successfully delete expired log files: %s.", delete_num)
    os.chdir(cwd)  # 恢复当前执行路径
    logger.debug("Finish to rollover log files.")


if __name__ == "__main__":
    rollover_log()
