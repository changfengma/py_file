#!/bin/bash
# -*- coding: utf-8 -*-



# 读取配置文件
'''
文件格式
# excel文件路径
[excel]
path1
path2

# 消息日志文件路径
[txtpath]
txtpath1
txtpath2

# 消息源
[Source]
MMC
MSC

# 消息目的
[Destination]
MMRM
RRMM
'''


import re

reg_excel = "\[excel\]"
reg_txt = "\[txtpath\]"
reg_source = "\[Source\]"
reg_dest = "\[Destination\]"


def get_configs(configfile):
    conf_dict = {}
    with open(configfile, 'r') as fd:
        for line in fd:
            if len(line.strip()) == 0:
                continue
            if line.strip().startswith("#"):
                continue
            if line.strip().startswith("["):
                key = re.match(r"\[(\w+)\]", line.strip()).group(1)
                conf_dict[key] = []
            else:
                conf_dict[key].append(line.strip())
    return conf_dict


if __name__ == "__main__":
    path = r"E:\code\PycharmProjects\Test\Practice\config.ini"
    print get_configs(path)
















