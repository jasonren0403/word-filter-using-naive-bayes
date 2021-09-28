import os
import platform
import re


def get_line_separator():
    if platform.system() == 'Windows':
        return '\r\n'
    elif platform.system() == 'Unix':
        return '\n'
    else:
        return '\n'


def count_file(path):
    count = 0
    for root, dirs, files in os.walk(path):
        for _ in files:
            count += 1
    return count


def get_file_list(path):
    list = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            list.append(os.path.join(root, dir))
        for name in files:
            list.append(os.path.join(root, name))
    return list


def filter_text(source_text):
    text = re.sub(u"[\s+\.\!\/_,$%^*()?\[\]\"\' ]+|[<>〉《》；:\-【 】●“”+—！，\r\n。：？、~@#￥%…&*（）]+", u'', source_text)
    return text


def isAllLetters(word):
    return all(97 < ord(c) < 122 or 65 < ord(c) < 90 for c in word)


def notChinese(word):
    return word.isdigit() or re.match(r"^[0-9A-Za-z]+$", word) is not None or isAllLetters(word)


def deleteNonChinese(_dict):
    _list = _dict.keys()
    RE = re.compile(r"[\u4e00-\u9f5a]+")
    _list = [x.strip() for x in _list if x.strip() != '']
    for each in _list:
        if not re.match(RE, each) and notChinese(each):
            _list.remove(each)
    temp = {}
    for each in _list:
        temp.update({each: _dict.get(each)})
    return temp
