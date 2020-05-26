from flask import Flask,render_template,request,session
from flask_cors import *
from sloving_feature import compute_sentence_vec,compute_cosine_sim
from ImgFeatureExtract import compare_batch
from utils import str_map,classification
import requests
from flask_session import Session
import datetime
import os
import json
import pymysql

app = Flask(__name__)
CORS(app, resources=r'/*')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)

connect = pymysql.connect("rm-2zeapqd2umkd11de9wo.mysql.rds.aliyuncs.com", "emoji", "H984505h", "emoji2")
cursor = connect.cursor()


url_header = 'http://121.199.50.208:8080/static/'
phone_num_dict = {}

@app.route('/')
def hello_world():
    dicts1 = ['img/1.jpg', 'img/3.jpg']
    dicts2 = ['img/2.jpg', 'img/6.jpg']
    dicts1 = [url_header + x for x in dicts1]
    dicts2 = [url_header + x for x in dicts2]
    return render_template('index.html',  dicts1=dicts1, dicts2=dicts2)

@app.route('/search_py_photo')
def search_py_photo():
    dicts1 = ['img/1.jpg', 'img/3.jpg', 'img/猫和老鼠/3.jpg', 'img/小黄鸡/3.jpg']
    dicts2 = ['img/2.jpg', 'img/6.jpg', 'img/猫和老鼠/10.jpg', 'img/任意表情包/3.jpg']
    dicts1 = [url_header + x for x in dicts1]
    dicts2 = [url_header + x for x in dicts2]
    return render_template('Search_by_photo.html', dicts1=dicts1, dicts2=dicts2)

@app.route('/search_py_text')
def search_py_text():
    dicts1 = ['img/1.jpg', 'img/3.jpg', 'img/猫和老鼠/3.jpg', 'img/小黄鸡/3.jpg']
    dicts2 = ['img/2.jpg', 'img/6.jpg', 'img/猫和老鼠/10.jpg', 'img/任意表情包/3.jpg']
    dicts1 = [url_header + x for x in dicts1]
    dicts2 = [url_header + x for x in dicts2]
    place = "Search"
    return render_template('Search_by_text.html', dicts1=dicts1, dicts2=dicts2, place=place)

@app.route('/collect')
def collect():
    dicts1 = ['img/小人/1.jpg', 'img/小人/2.jpg' , 'img/小人/10.jpg']
    dicts2 = ['img/小黄鸡/1.jpg', 'img/小黄鸡/3.jpg', 'img/小黄鸡/8.jpg']
    dicts3 = ['img/熊猫头/5.jpg', 'img/熊猫头/2.jpg', 'img/熊猫头/8.jpg']
    dicts4 = ['img/猫和老鼠/3.jpg', 'img/猫和老鼠/4.jpg', 'img/猫和老鼠/5.jpg']
    dicts1 = [url_header + x for x in dicts1]
    dicts2 = [url_header + x for x in dicts2]
    dicts3 = [url_header + x for x in dicts3]
    dicts4 = [url_header + x for x in dicts4]
    return render_template('Collect.html', dicts1=dicts1, dicts2=dicts2, dicts3=dicts3, dicts4=dicts4)

@app.route('/boutique')
def boutique():
    dicts1 = ['img/小人/1.jpg', 'img/小人/2.jpg', 'img/小人/10.jpg']
    dicts2 = ['img/小黄鸡/1.jpg', 'img/小黄鸡/3.jpg', 'img/小黄鸡/8.jpg']
    dicts3 = ['img/熊猫头/5.jpg', 'img/熊猫头/2.jpg', 'img/熊猫头/8.jpg']
    dicts4 = ['img/猫和老鼠/3.jpg', 'img/猫和老鼠/4.jpg', 'img/猫和老鼠/5.jpg']
    dicts1 = [url_header + x for x in dicts1]
    dicts2 = [url_header + x for x in dicts2]
    dicts3 = [url_header + x for x in dicts3]
    dicts4 = [url_header + x for x in dicts4]
    return render_template('Boutique.html', dicts1=dicts1, dicts2=dicts2, dicts3=dicts3, dicts4=dicts4)

@app.route('/personal')
def personal():
    return render_template('personal.html')

@app.route('/search_text',methods=['GET','POST'])
def search_text():
    data = json.loads(request.form.get('data'))
    content = data['search_text']
    vec = compute_sentence_vec(content)
    dict = compute_cosine_sim(vec)
    if len(dict) > 14:
        dict = dict[:14]
    dicts1 = dict[::2]
    dicts2 = dict[1::2]
    return render_template('Search_by_text.html', dicts1=dicts1, dicts2=dicts2, place=content)

@app.route('/search_photo', methods=['POST','GET'])
def search_photo():
    url = 'http://60.205.177.131:8081/search_photo'
    nowTime = datetime.datetime.now()
    file = request.files['file']
    filename = file.filename
    dst = os.path.dirname(__file__) + '/tmp/' + str(nowTime) + '.jpg'
    file.save(dst)
    files = {'file': open(dst, 'rb')}
    r = requests.post(url, files=files)
    result = r.text
    if result == '':            # 做相似比较
        dict = compare_batch(dst)
    else:
        vec = compute_sentence_vec(result)
        dict = compute_cosine_sim(vec)
    if len(dict) > 14:
        dict = dict[:14]
    os.remove(dst)
    dicts1 = dict[::2]
    dicts2 = dict[1::2]
    return render_template('Search_by_photo.html', dicts1=dicts1, dicts2=dicts2)

@app.route('/search_comment',methods=['GET','POST'])
def search_comment():
    data = json.loads(request.form.get('data'))
    imgname = data['imgname'].split('/')
    group = str(classification(imgname))
    sql = "select comment from comment where `group`=%s and photoname=%s;"
    cursor.execute(sql, [group,imgname[-1]])
    results  = cursor.fetchall()
    if len(results) != 0:
        ret_result = ""
        for result in results:
            tmp = "<p class=\"form-control_x\">" + result + "</p>\n"
            ret_result += tmp
        return ret_result
    else:
        return "<p class=\"form-control_x\">" + "暂未有人评论" + "</p>\n"


@app.route('/sendmessage', methods=['GET', 'POST'])
def sendmessage():
    data = json.loads(request.form.get('data'))
    phonenum = data['phonenum']
    # phonenum = request.args.get('phonenum')
    import random
    content = ""
    for i in range(6):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        content += ch
    url = 'http://60.205.177.131:8082/send?phonenum='
    requests.get(url + phonenum + '&content=' + content)
    phone_num_dict[phonenum] = content
    return "OK"

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login_test', methods=['POST'])
def login():
    data = json.loads(request.form.get('data'))
    phonenum = data['phonenum']
    captcha = data['captcha']
    if phone_num_dict[phonenum] == captcha:
        session['userid'] = phonenum
        phone_num_dict.pop(phonenum, '404')
        # 数据库相关操作
        sql_1 = "select * from user where phonenum=%s;"
        sql_2 = "insert into user(phonenum, username) values (%s, %s);"
        data_1 = cursor.execute(sql_1, [phonenum])
        if not data_1:
            cursor.execute(sql_2, [phonenum, 'id_' + phonenum])
            connect.commit()
        return "http://121.199.50.208:8080/"
    else:
        return "false"

@app.route('/send_comment', methods=['POST'])
def send_comment():
    data = json.loads(request.form.get('data'))
    imgname = data['img2src'].split('/')
    comment_content = data['comment_content']
    userid = session.get('userid')
    # 先找出之前的评论
    group = str(classification(imgname))
    sql_1 = "select comment from comment where `group`=%s and photoname=%s;"
    cursor.execute(sql_1, [group, imgname[-1]])
    results = cursor.fetchall()
    # 添加评论
    sql_2 = "insert into comment(`group`, photoname, comment, phonenum) values (%s, %s, %s, %s);"
    cursor.execute(sql_2, [group, imgname[-1], comment_content, userid])
    connect.commit()
    # 新发布的评论显示在最上方
    ret_result = "<p class=\"form-control_x\">" + comment_content + "</p>\n"
    for result in results:
        tmp = "<p class=\"form-control_x\">" + result + "</p>\n"
        ret_result += tmp
    return ret_result


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
