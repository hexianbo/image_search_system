#import这些库
from gensim.models import KeyedVectors
import numpy as np
from string import punctuation
from zhon import hanzi
import re
import pkuseg
import json

seg = pkuseg.pkuseg()           # 以默认配置加载模型
url_header = 'http://121.199.50.208:8080/static/img/'
path = '/root/program/text1/static/'

file = 'txt/100000-small.txt'
wv_from_text = KeyedVectors.load_word2vec_format(path + file, binary=False)
wv_from_text.init_sims(replace=True)
vec_shape = wv_from_text.wv.syn0[0].shape[0]         #词向量的维度
with open(path + 'txt/stopwords.txt', encoding ='utf-8') as f:
    stopwords = [line.strip() for line in f.readlines()]

json_files = ['任意表情包', '小人', '小黄脸', '小黄鸡', '熊猫头', '猫和老鼠']
json_files_dict = {'任意表情包':0, '小人':1, '小黄脸':2, '小黄鸡':3, '熊猫头':4, '猫和老鼠':5}
list_json = []
list_cut_json = []
for json_file in json_files:
    with open(path + 'json/' + json_file + '.json') as f:
        data = json.load(f)
        tmp_list = []
        for x in data:
            tmp = np.array(data[x])
            tmp_list.append(tmp)
        tmp_list = np.array(tmp_list)
        list_json.append(tmp_list)
    with open(path + 'json/' + json_file + 'cut.json') as f:
        data = json.load(f)
        list_cut_json.append(data)


def separate(content):
    text = seg.cut(content)  # 进行分词
    return text

punc = punctuation + hanzi.punctuation + u'0123456789'
def remove_digits_and_punctuation(input):
    punc = punctuation + hanzi.punctuation + u'0123456789'
    res = re.sub(r'[{}]+'.format(punc), '', input)
    return res


def compute_ngrams(word, min_n, max_n):
    word_temp =  word
    ngrams = []
    for ngram_length in range(min_n, min(len(word_temp), max_n) + 1):
        for i in range(0, len(word_temp) - ngram_length + 1):
            ngrams.append(word_temp[i:i + ngram_length])
    return list(set(ngrams))

def wordVec(word, wv_from_text, min_n = 1, max_n = 3):      #词转向量函数
    '''
    ngrams_single/ngrams_more,主要是为了当出现oov的情况下,最好先不考虑单字词向量
    '''
    # 确认词向量维度
    word_size = wv_from_text.wv.syn0[0].shape[0]
    # 计算word的ngrams词组
    ngrams = compute_ngrams(word,min_n = min_n, max_n = max_n)
    # 如果在词典之中，直接返回词向量
    if word in wv_from_text.wv.vocab.keys():
        return wv_from_text[word]
    else:
        # 不在词典的情况下
        word_vec = np.zeros(word_size, dtype=np.float32)
        ngrams_found = 0
        ngrams_single = [ng for ng in ngrams if len(ng) == 1]
        ngrams_more = [ng for ng in ngrams if len(ng) > 1]
        # 先只接受2个单词长度以上的词向量
        for ngram in ngrams_more:
            if ngram in wv_from_text.wv.vocab.keys():
                word_vec += wv_from_text[ngram]
                ngrams_found += 1
                #print(ngram)
        # 如果，没有匹配到，那么最后是考虑单个词向量
        if ngrams_found == 0:
            for ngram in ngrams_single:
                word_vec += wv_from_text[ngram]
                ngrams_found += 1
        if word_vec.any():
            return word_vec / max(1, ngrams_found)
        else:
            raise KeyError('all ngrams for word %s absent from model' % word)

#余弦相似度公式
def compute_cosine_sim(vector):
    dict = {}
    for i in range(6):
        tmp = np.dot(vector, list_json[i].T)
        a = np.linalg.norm(vector)
        b = np.linalg.norm(list_json[i], axis=1)
        tmp = tmp / (a*b)
        index = np.argwhere(tmp > 0.6)
        x, y = index.shape
        for j in range(x):
            dict[url_header + json_files[i]+'/' + str(index[j][0]+1)+'.jpg'] = tmp[index[j][0]]
    return sorted(dict, key=dict.__getitem__, reverse=True)


#计算句子向量（输入字符串）
def compute_sentence_vec(sentence):
    cut_res1 = seg.cut(sentence)
    outword1 = []
    for i in cut_res1:
        if i not in stopwords and remove_digits_and_punctuation(i):
        #if remove_digits_and_punctuation(i):
            outword1.append(i)
    sum1 = np.zeros(vec_shape)
    for i in outword1:
        sum1 += wordVec(i,wv_from_text)

    vec1 = sum1/len(outword1)
    return vec1


# 计算语句的相似度
def compute_sentence_sim(str1, str2):
    cut_res1 = seg.cut(str1)
    cut_res2 = seg.cut(str2)
    outword1 = []
    outword2 = []

    for i in cut_res1:
        if i not in stopwords and remove_digits_and_punctuation(i):
            # if remove_digits_and_punctuation(i):
            outword1.append(i)

    for i in cut_res2:
        if i not in stopwords and remove_digits_and_punctuation(i):
            # if remove_digits_and_punctuation(i):
            outword2.append(i)
    sum1 = np.zeros(vec_shape)
    sum2 = np.zeros(vec_shape)
    print(outword1)
    print(outword2)
    for i in outword1:
            sum1 += wordVec(i, wv_from_text)
    for i in outword2:
        sum2 += wordVec(i, wv_from_text)
    vec1 = sum1 / len(outword1)
    vec2 = sum2 / len(outword2)
    print(compute_cosine_sim(vec1, vec2))
    return compute_cosine_sim(vec1, vec2)