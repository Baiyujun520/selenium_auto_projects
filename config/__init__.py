# coding=utf-8
import os

from configparser import ConfigParser


class ConfDict(dict):
    def __init__(self):
        super(ConfDict, self).__init__()

    def __getattr__(self, name):
        name = name.lower()
        if name not in self.keys():
            raise ValueError("Cannot get the key: " + str(name))
        value = self.get(name)
        if value is not None:
            return value
        else:
            raise ValueError("The key:" + str(name) + "can not find the value!!!")


def format_value(value):
    # 去除配置项值中的单引号与双引号
    if str(value).startswith("\'") and str(value).endswith("\'"):
        value = str(value).strip("\'")
    elif str(value).startswith("\"") and str(value).endswith("\""):
        value = str(value).strip("\"")
    else:
        value = str(value)
    # 将配置项（变量value）的值转为int string bool类型
    if value.isdigit():
        value = int(value)
    elif value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    return value


def dict_config(key_list, config_parser, parent_key, parent_dict):
    conf_dict = ConfDict()
    for key in key_list:
        if key in config_parser.sections():
            dict_config(config_parser.options(section=key), config_parser, key, conf_dict)
        else:
            value = config_parser.get(section=parent_key, option=key)
            conf_dict[str(key).lower()] = format_value(value)
    parent_dict[str(parent_key).lower()] = conf_dict


def read_config():
    config = ConfDict()
    file_path = os.path.dirname(__file__)
    for each_file in os.listdir(file_path):
        file_name = os.path.basename(each_file)
        if ".cfg" in file_name or ".ini" in file_name:
            file_key = file_name.split(".")[0]
            config_parser = ConfigParser()
            config_parser.read(filenames=os.path.join(file_path, file_name), encoding="GB18030")
            dict_config(config_parser.sections(), config_parser, file_key, config)
    return config


conf = read_config()
