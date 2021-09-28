import codecs

from log import *
from word_divide import *


# 读取分词文件
def load(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content


# 合并两个字典，相同索引值相加，无索引直接添加
def merge_dict(x, y):
    from collections import Counter
    X, Y = Counter(x), Counter(y)
    z = dict(X + Y)
    return z


def file_count_by_category(category_path):
    if not os.path.isdir(category_path):
        return 0
    files = os.listdir(category_path)  # 得到文件夹下的所有文件名称
    i = 0
    for _ in files:
        i = i + 1
    return i


# 计算总共有多少个文件|D|
def total_file_count(path):
    if not os.path.isdir(path):
        return 0
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    d = 0
    for file in files:
        i = file_count_by_category(os.path.join(path, file))
        d = d + i
    return d


# 计算P(ci)=|Di|/|D|
def ci(path, file_count):
    i = file_count_by_category(path)
    pci = i / file_count
    return pci


# 计算ni,即Di中词的总数,dic为一类的字典,
def ni(dic):
    ni = 0
    for value in dic.values():
        ni += value
    return ni


# 对每个词wj∈V，计算Di中P(wi|ci)=(nij+1)/(ni+|V|),dic1表示V，dic2表示集合Di
def wi_ci(V, di, ni):
    dic3 = {}
    for key in V:
        if key not in di:
            nij = 0
        else:
            nij = di[key]
        p = (nij + 1) / (ni + len(V))
        dic3[key] = p
    return dic3


# 对计算出来的P(wi|ci)=(nij+1)/(ni+|V|)构成的字典进行排序，取最大的m个，dic1表示V，dic2表示Di
def sort(dic1, dic2, ni, max):
    dic3 = wi_ci(dic1, dic2, ni)  # wj∈V，计算Di中P(wi|ci)=(nij+1)/(ni+|V|),dic1表示V，dic2表示集合Di
    z = zip(dic3.values(), dic3.keys())
    x = sorted(z)
    x.reverse()
    print("x:", x)
    y = x[0:max]
    return y


# V为文档集合D所有词词表
def getV(train_path, categories):
    a = {}
    for cat in categories:
        path = os.path.join(train_path, cat)
        for file in os.listdir(path):
            json_content = load(os.path.join(path, file))
            # 拿到去了停用词的词频文件(json)
            a = merge_dict(a, json_content)
            # 此时拿到了所有词的词频
            # 类似于{ "<word>":<wordcount>,...}
    V = set(list(a.keys()))
    return V


def get_categories(path):
    categories = []
    for file in os.listdir(path):
        categories.append(file)
    return categories


# 计算测试文档的贝叶斯值，即argmaxP(ci)×P(wi|ci)× dic2是Di，
def get_bayes(path1, dic2, ni, pci, m):  # path1为测试文档分词后的文档的路径，是个json
    d = load(path1)
    y = sort(d, dic2, ni, m)  # y是p（wi|ci）数组 dic1表示V，dic2表示Di
    print("from sort():", y)
    pwi = 1
    for key in d:
        i = 0
        while i < m:
            if key in y[i][1]:
                pwi = pwi * y[i][0]
                break
            i = i + 1
    arg = pci * pwi
    # print(arg)
    return arg


def get_dict(dict_file_name):
    print('getting dict...')
    with codecs.open(os.path.join(".\\dict\\", dict_file_name), "r", encoding='gbk', errors='ignore')as f:
        content = f.read()
    # print(content)
    _dict = content.split('\n')
    if '' in _dict:
        _dict.remove('')
    print('dict get')
    return _dict


def train(train_path=None, given_category=False, category_list=None):
    import sys
    if not os.path.exists(".\\result"):
        os.mkdir(".\\result")
    sys.stdout = Logger(".\\result\\train_log.txt")
    print("Preparing training datas...")
    D = 0  # 文件总数D
    file_count = {}
    trained = {}
    file_lists = {}
    if not given_category:
        categories = []
        for directory in os.listdir(train_path):
            categories.append(directory)
            path = os.path.join(train_path, directory)
            D += file_count_by_category(path)
            print("Category: {},{} file(s)".format(directory, file_count_by_category(path)))
            file_count.update({directory: file_count_by_category(path)})
    else:
        categories = category_list
        for category in category_list:
            try:
                path = os.path.join(os.path.abspath(train_path), category)
            except IOError as e:
                print(e)
                print('You should make directories in ./test_datas/train/ first, using your category name')
            else:
                D += file_count_by_category(path)
                print("Category: {},{} file(s)".format(category, file_count_by_category(path)))
                file_count.update({category: file_count_by_category(path)})
    print("Total file count:", D)
    assert D == total_file_count(train_path)
    # 分类在train下，一个分类是一个文件夹
    V = getV(train_path, categories)
    for cat in categories:
        di = {}
        list_temp = []
        path = os.path.join(train_path, cat)
        for file in os.listdir(path):
            file_temp = os.path.join(path, file)
            json_content = load(file_temp)
            di = merge_dict(di, json_content)
            list_temp.append(file_temp)
        ni_temp = ni(di)
        L = sort(V, di, ni_temp, 200)
        trained.update({cat: L})
        file_lists.update({cat: list_temp})
    for category in trained:
        list_value = trained.get(category)
        list_value.sort(key=lambda item: (item[0], item[1]), reverse=True)
        trained.update({
            category: list_value
        })
    return trained


# trained:{"category_name":[P(ci)],...}


def predict(test_data_path=None, given_model=None):
    import sys
    from collections import defaultdict

    classified = defaultdict(int)
    classified_files = defaultdict(list)
    categories = get_categories(".\\test_datas\\train")
    sys.stdout = Logger(".\\result\\classify_log.txt")

    for folder in os.listdir(test_data_path):  # 所有测试文件在test_datas/test下是分类存放的，是txt
        for file in os.listdir(os.path.join(test_data_path, folder)):
            a = {}
            # print("file:",file)
            # todo:对测试文档分词，取词频
            with open(os.path.join(test_data_path, folder, file), 'r', encoding='gbk', errors='ignore') as f:
                content = f.read()
                filename = file.split('\\')[-1][0:-4]
                if file.endswith(".json"):
                    continue
                print("Word dividing: %s" % file)
                using_dict = get_dict("dict.txt")
                word_list, returning_dict = MM(content, 10, using_dict,
                                               output=os.path.join(test_data_path, folder, filename + ".json"))
                # di = json.dumps(returning_dict)
                # di = json.loads(di)
                # print(di)
                # print(returning_dict)
                di = deleteNonChinese(returning_dict)
                print("Predicting file:{}".format(file))
                for category in categories:
                    a.update(
                        {category: get_bayes(os.path.join(test_data_path, folder, filename + ".json"),
                                             given_model[category], ni(di),
                                             ci(os.path.join(test_data_path, folder), total_file_count(test_data_path)),
                                             total_file_count(os.path.join(test_data_path, folder)))}
                    )
            print("a: ", a)
            lst = sorted(a.items(), key=lambda d: d[1], reverse=True)
            print("lst:", lst)
            for key, value in lst:
                name, argmax = key, value
                print("File:{} is classified as {}".format(file, name))
                classified[name] += 1
                classified_files[name].append(filename)
                break
    return classified, classified_files


# classified_files:
# { "类别1":["文件1","文件2",...],...}
# classified:
# {"类别1":文件总数1,"类别2":文件总数2,...}


def evaluate(test_data_path=None):
    from collections import defaultdict
    file_count = defaultdict(int)
    file_lists = defaultdict(list)
    for folder in os.listdir(test_data_path):
        path = os.path.join(test_data_path, folder)
        # print('path:', os.listdir(path))
        for train_txt in os.listdir(path):
            if not train_txt.endswith(".json"):
                file_count[folder] += 1
                file_lists[folder].append(train_txt)
    print(file_count.items())
    print(file_lists.items())
    return file_count, file_lists


# file_count:每一类的文件数量
# file_lists:{"category_name":[file1,file2,...],...}

def main():
    train_path = ".\\test_datas\\train"
    test_path = ".\\test_datas\\test"
    trained = train(train_path, given_category=False)

    print("Using trained model :", trained)
    predicted, predicted_filelist = predict(test_data_path=test_path, given_model=trained)
    '''
    准确率=分对的样本数/程序分为该类的样本数
    召回率=分对的样本数/原本属于该类的样本数
    '''
    file_count, file_lists = evaluate(test_path)
    classified_count = 0
    correct_count = 0
    origin_count = 0

    for index in get_categories(train_path):
        classified_count += predicted[index]  # 分为该类的样本数
        origin_count += file_count[index]  # 原本属于该类的样本数（应该等于文件总数D）
        for file in predicted_filelist[index]:
            if file in file_lists[index]:
                correct_count += 1
    if classified_count == 0 or origin_count == 0:
        raise Exception('No test file specified, please put them in directory ./test_datas/test in categories.')
    recall_rate = correct_count / classified_count
    precision_rate = correct_count / origin_count
    print("Recall rate:%.2f ,Precision rate:%.2f" % (recall_rate, precision_rate))


if __name__ == '__main__':
    if not os.path.exists(".\\result"):
        os.makedirs(".\\result\\train")
    main()
