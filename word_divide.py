from utils import *
import json

LINE_SEPARATOR = get_line_separator()


def MM(text, max_len=5, _dict=None, delimiter=" ", output=None):
    from collections import defaultdict
    returning_dict = defaultdict(int)
    s_2 = []  # split result
    s_1 = text  # the text to be split
    if text is None or len(text) == 0:
        return
    n = 0
    while n < len(s_1):
        matched = False  # if the word match the word stored in dictionary, it is true
        for i in range(max_len, 0, -1):
            s = text[n:n + i]  # select string from left with length i
            if s != LINE_SEPARATOR and notChinese(s):
                temp = i
                temp += 1
                # print("%s is letters or digit" % s)
                while notChinese(text[n:n + temp]):
                    temp += 1
                    # print("%s is letters or digit" % text[n:n + temp])
                s_2.append(text[
                           n:n + temp - 1])  # if string is made of all-num or all-digit ,it should be split out!(for this task only)
                print("%s is letters or digit,ignored" % text[n:n + temp - 1])
                n += (temp - 1)
                matched = True
                break
            # print("s:{},length:{}".format(s, i))
            if s in _dict:
                s_2.append(s)
                matched = True
                n = n + i
                print("s:{} found in dictionary.".format(s))
                returning_dict[s] += 1
                break
        if not matched:
            s_2.append(s_1[n])  # text[n] is a single-character word,add it!
            returning_dict[s_1[n]] += 1
            n = n + 1
    print("output:", os.path.abspath(output))
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(returning_dict, f, ensure_ascii=False)
    return s_2, returning_dict
