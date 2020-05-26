import cv2
from matplotlib import pyplot as plt
import numpy as np
import os
import math


url_header = 'http://121.199.50.208:8080/static/img/'
def getMatchNum(matches):
    '''返回特征点匹配数量和匹配掩码'''
    matchDis=0
    for d in matches:
        matchDis-=d.distance
    return matchDis


def store(queryPath, feature_dict, feature_store):
    orb = cv2.ORB_create(edgeThreshold=20)
    for p in os.listdir(queryPath):
        ab_path = queryPath+p
        queryImage=cv2.imread(ab_path)
        # queryImage=cv2.resize(queryImage, (8, 8))
        kp2, des2 = orb.detectAndCompute(queryImage, None) #提取比对图片的特征
        feature_dict[p] = des2
        # print(des2)
    np.savez(feature_store, **feature_dict)

features = {}
features['小人'] = np.load('/root/program/text1/static/npz/features_小人.npz')
features['小黄脸'] = np.load('/root/program/text1/static/npz/features_小黄脸.npz')
features['小黄鸡'] = np.load('/root/program/text1/static/npz/features_小黄鸡.npz')
features['熊猫头'] = np.load('/root/program/text1/static/npz/features_熊猫头.npz')
features['猫和老鼠'] = np.load('/root/program/text1/static/npz/features_猫和老鼠.npz')
features['任意表情包'] = np.load('/root/program/text1/static/npz/features_任意表情包.npz')

def compare(path, samplePath, from_path):
    queryPath=path #图库路径
    scoreList = []
    #创建ORB特征提取器
    orb = cv2.ORB_create(edgeThreshold=20)
    bf=cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    sampleImage=cv2.imread(samplePath)
    kp1, des1 = orb.detectAndCompute(sampleImage, None) #提取样本图片的特征
    # print(des1)
    # feature_dict = {}
    # feature_store = 'features.npz'

    """
    store 函数用于储存图像特征到features.npz文件，第二次运行时可以注释掉以下这一行
    """
    # store(queryPath, feature_dict, feature_store)
    #
    # features = np.load(feature_store)
    for p in os.listdir(queryPath):
        des2 = features[from_path][p]
        matches=bf.match(des1,des2) #匹配特征点
        matchDis=getMatchNum(matches) #通过比率条件，计算出匹配程度
        scoreList.append((url_header + from_path + '/' + p, matchDis))
    scoreList.sort(key=lambda x: x[1], reverse=True)
    return scoreList


features_index = {}
features_index['小人'] = np.load('/root/program/text1/static/npz/features_小人index.npz')
features_index['小黄脸'] = np.load('/root/program/text1/static/npz/features_小黄脸index.npz')
features_index['小黄鸡'] = np.load('/root/program/text1/static/npz/features_小黄鸡index.npz')
features_index['熊猫头'] = np.load('/root/program/text1/static/npz/features_熊猫头index.npz')
features_index['猫和老鼠'] = np.load('/root/program/text1/static/npz/features_猫和老鼠index.npz')

def compare_index(path, samplePath, from_path):
    queryPath=path #图库路径
    scoreList = []
    orb = cv2.ORB_create(edgeThreshold=20)
    bf=cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    sampleImage=cv2.imread(samplePath)
    kp1, des1 = orb.detectAndCompute(sampleImage, None) #提取样本图片的特征

    for p in os.listdir(queryPath):
        des2 = features_index[from_path][p]
        matches=bf.match(des1,des2) #匹配特征点
        matchDis=getMatchNum(matches) #通过比率条件，计算出匹配程度
        scoreList.append( matchDis)
    return np.mean(scoreList)

def compare_batch(sample_path):
    feature_store = 'features_'
    files = ['小人', '小黄脸', '小黄鸡', '熊猫头', '猫和老鼠']
    file_path = '/root/program/text1/static/img/'
    list = []
    for file in files:
        tmp_list = compare_index(file_path + 'emoji_sample/'+ file + '/', sample_path, file)
        list.append((file, tmp_list))
    list.sort(key=lambda x: x[1], reverse=True)
    print(list)
    files = []
    files.append(list[0][0])
    files.append(list[1][0])
    files.append('任意表情包')
    list = []
    for file in files:
        list += compare(file_path + file + '/', sample_path, file)
    list.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in list]

# if __name__ == "__main__":
#     time0 = time.time()
#     compare_batch('/root/program/text1/static/img/小人/2.jpg')
#     print(time.time() - time0)
