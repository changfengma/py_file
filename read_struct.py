#!/bin/bash
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name: read_struct
      Author: changfeng
        date: 2019/8/11
 Description:改脚本读取.h文件中的结构体成员并替换成小驼峰格式，并替换在
             .c文件中的调用
"""

import re

prefix_list = ["pst", "us", "ul", "p"]
# 存储 {结构体名；{就变量名:新变量名}}
g_struct_var = {}
g_struct_type = {}   # {结构体名；{就变量名:类型}}

# 匹配结构体开始位置
reg_stru_begin = r"typedef\s+struct"

# 匹配结构体名
reg_stru_name = r"\s*}\s*(\w+)\s*;"

# 匹配结构体成员
reg_stru_varname = r"\s+(\w+)\s+\*?(\w+)[\[\]\+\-\*/\w ]*;"


# 处理结构体中的成员变量
def get_stru_varname(datalines, struct_name, start, end):
    var_name_dict = {}
    var_type_dict = {}
    for i in range(start, end):
        m = re.match(reg_stru_varname, datalines[i])
        if m is None:
            continue

        var_name = m.group(2).strip()
        for prefix in prefix_list:
            if var_name.startswith(prefix):
                datalines[i] = datalines[i].replace(prefix, "", 1)
                var_name = var_name.replace(prefix, "", 1)
                break
        var_name_dict[m.group(2)] = var_name
        var_type_dict[m.group(2)] = m.group(1)
    g_struct_type[struct_name] = var_type_dict
    g_struct_var[struct_name] = var_name_dict


# 查找.h文件中所有的结构体
def find_struct_file(filepath):
    with open(filepath, 'r') as fd:
        datalines = fd.readlines()

    find_struct = False
    for line_no, line in enumerate(datalines):
        if not find_struct:
            if re.match(reg_stru_begin, line.strip()):
                find_struct = True
                start = line_no
                continue
        if find_struct:
            m1 = re.match(reg_stru_name, line)
            if m1:
                find_struct = False
                struct_name =m1.group(1)
                end = line_no
                get_stru_varname(datalines, struct_name, start, end)


def handle_pointer(varname):
    if varname.strip().startswith("*"):
        varname = varname.replace("*", "") + "->"
    else:
        varname = varname + "."
    return varname


def join_stru_re(structname, var_name):
    old_new_name_dict = g_struct_var[structname]
    join_old_new_name_dict = {}
    var_name = handle_pointer(var_name)
    for old_name in old_new_name_dict:
        join_old_new_name_dict[var_name + old_name] = var_name + old_new_name_dict[old_name]

    # print join_old_new_name_dict
    result_dict = {}
    result_dict[structname] = join_old_new_name_dict
    return result_dict


def get_index(line, startindex):
    index = -1
    if line.find(" ", startindex) > -1:
        index = line.find(" ", startindex)
    elif line.find(";", startindex) > -1:
        index = line.find(";", startindex)
    elif line.find(",", startindex) > -1:
        index = line.find(",", startindex)
    elif line.find(")", startindex) > -1:
        index = line.find(")", startindex)
    return index


def replace_in_file(filepath):
    with open(filepath, 'r') as fd:
        datalines = fd.readlines()

    tmp_dict = {}
    for line_no, line in enumerate(datalines):
        for key in g_struct_var:
            for iter1 in re.finditer(r"\b(%s)\b\s+(.+)[,;\)]" % key, line):
                tmp_dict.update(join_stru_re(iter1.group(1), iter1.group(2)))
    # print tmp_dict

    for line_no, line in enumerate(datalines):
        for stru_name in tmp_dict:
            for key in tmp_dict[stru_name]:
                for m in re.finditer("%s" % key, line):
                    print line, m.start()
                    last_index = get_index(line, m.start())
                    tmp_line = line[m.start(): last_index]
                    var_list = re.split(r"\->|\.", tmp_line)
                    len_var_list = len(var_list)

                    if len_var_list == 3:
                        if g_struct_type[stru_name][var_list[1]] in g_struct_var:
                            tmp_line_data = tmp_line.replace(key, tmp_dict[stru_name][key], 1)
                            tmp_line_data = tmp_line_data.replace(var_list[2], g_struct_var[g_struct_type[stru_name][var_list[1]]][var_list[2]], 1)
                            datalines[line_no] = re.sub(tmp_line, tmp_line_data, datalines[line_no])
                    else:
                        datalines[line_no] = re.sub(key, tmp_dict[stru_name][key], datalines[line_no])

    with open(filepath+"tmp", 'w') as fd:
        fd.writelines(datalines)


if __name__ == "__main__":
    hfile = [r"E:\code\PycharmProjects\Test\files\struct.h"]
    cfile = [r"E:\code\PycharmProjects\Test\files\struct.c"]

    for file in hfile:
        find_struct_file(file)

    for file in cfile:
        replace_in_file(file)
