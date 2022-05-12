from email.policy import default
from socket import timeout
from unittest import result
from urllib.request import Request
from warnings import catch_warnings
from xml.dom.minidom import TypeInfo
from flask import Flask, request
from flask_cors import CORS
import json, pymysql, serial, datetime, ast

#设置初始时间
Time = datetime.datetime.now()
beginTime = datetime.datetime.now()
print(beginTime)

#打开串口
portx = "COM11"
bps = 115200
timex = 5
ser1 = serial.Serial(portx, bps, timeout = timex)

portx = "COM12"
bps = 115200
timex = 5
ser2 = serial.Serial(portx, bps, timeout = timex)

portx = "COM15"
bps = 115200
timex = 5
ser3 = serial.Serial(portx, bps, timeout = timex)

portx = "COM16"
bps = 115200
timex = 5
ser4 = serial.Serial(portx, bps, timeout = timex)

#连接数据库
db = pymysql.connect(host='localhost',
                     user='root',
                     password='111111',
                     database='test')

cursor = db.cursor()
#执行sql，如果表存在则删除
cursor.execute("DROP TABLE IF EXISTS data")
#使用预处理语句创建表
sql = """CREATE TABLE data (
    time  datetime NOT NULL,
    location varchar(255))"""
cursor.execute(sql)
cursor.close()

#数据库插入
def sqlInsert(res):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
 
    # SQL 插入语句
    sql = "INSERT INTO data(time, \
       location) \
       VALUES ('%s', '%s')" % \
       (datetime.datetime.now(), res)
    try:
        db.ping(reconnect = True)
        # 执行sql语句
        cursor.execute(sql)
        # 执行sql语句
        db.commit()
        cursor.close()
    except:
        # 发生错误时回滚
        db.rollback()
        print("wrong")

#数据库查找
def sqlSelect(Time):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
    
    # SQL 查询语句
    sql = "SELECT * FROM data"
    try:
        db.ping(reconnect = True)
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            if row[0].minute - Time.minute == 0 or row[0].minute - Time.minute == 1:
                if row[0].second - Time.second == 0 or row[0].second - Time.second == 1:
                    cursor.close()
                    return row[1]
    except:
        print ("Error: unable to fetch data")

#数据封装发送
def dataFix(data):
    global Time
    data = ast.literal_eval(data)
    now = datetime.datetime.now()
    if(isinstance(data, list) == True):
        sqlInsert(str(data))
        Time = now
        print("mysql load sucess at ")
        print(Time)
        print(sqlSelect(Time))
        res = '{ "data": '+ str(sqlSelect(Time)) +' }'
        return json.loads(res)
    else:
        print("data is wrong")
        print(data)
        return '{ "data": "-1" }'

#数据发送
def dataSend(cursor, sql):
    try:
        print("Im trying")
        db.ping(reconnect = True)
        # 执行sql语句
        cursor.execute(sql)
        print("sql commit sucess")
        results = cursor.fetchall()
        if(results):
            print("fetchall sucess!")
            myList = []
            for row in results:
                myList.append(row[1])
            res = {"data": myList}
            cursor.close()
            return json.dumps(res)
        else:
            print("Error:We can't find your data under your time")
            return '{ "data": "-1" }'
    except:
        print("Error:Unexpected wrong")
        return '{ "data": "-2" }'

app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/*')

#实时数据传输
@app.route('/')
def data():
    global Time
    serial.Serial.flushInput(ser1)
    serial.Serial.flushInput(ser2)
    serial.Serial.flushInput(ser3)
    serial.Serial.flushInput(ser4)

    data1 = ser1.readline().decode().replace("\r\n", "")
    data2 = ser2.readline().decode().replace("\r\n", "")
    data3 = ser3.readline().decode().replace("\r\n", "")
    data4 = ser4.readline().decode().replace("\r\n", "")

    if(data1 != "-1" and data1 != ""):
        print("------------------------")
        print("It's ser1 data")
        return dataFix(data1)
    if(data2 != "-1" and data2 != ""):
        print("------------------------")
        print("It's ser2 data")
        return dataFix(data2)
    if(data3 != "-1" and data3 != ""):
        print("------------------------")
        print("It's ser3 data")
        return dataFix(data3)
    if(data4 != "-1" and data4 != ""):
        print("------------------------")
        print("It's ser4 data")
        return dataFix(data4)
    else:
        print("cammer is not open")
        return '{ "data": "-1" }'

#相应数据取出
@app.route("/find/<num>") 
def find(num):
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    if(num == '1'):
        print("Im in 1 sql!")
        sql = "SELECT * FROM DATA \
            WHERE TIME > '%s' and TIME < '%s'"%\
            (beginTime.strftime('%Y-%m-%d %H:%M:%S'), (beginTime + datetime.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'))
        return dataSend(cursor, sql)

    if(num == "2"):
        print("Im in 2 sql!")
        sql = "SELECT * FROM DATA \
            WHERE TIME > '%s' and TIME < '%s'"%\
            ((beginTime + datetime.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'), (beginTime + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'))
        return dataSend(cursor, sql)
    
    if(num == "3"):
        print("Im in 3 sql!")
        sql = "SELECT * FROM DATA \
            WHERE TIME > '%s' and TIME < '%s'"%\
            ((beginTime + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'), (beginTime + datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'))
        return dataSend(cursor, sql)

    else:
        return '{ "data": "-1" }'

#时间段数据选择
@app.route("/find/<beginTime>/<endTime>")
def findMytime(beginTime, endTime):
    if(beginTime > endTime):
        print("wrong input!")
        return '{ "data": "-3" }'
    #时间格式整理
    year = str(datetime.datetime.now().year)
    month = str(datetime.datetime.now().month)
    day = str(datetime.datetime.now().day)
    beginTime = year + '-' + month + '-' + day + ' ' + beginTime + ':00'
    endTime = year + '-' + month + '-' + day + ' ' + endTime + ':00'
    begin = datetime.datetime.strptime(beginTime, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    print("Im in 4 sql!")
    sql = "SELECT * FROM DATA \
        WHERE TIME > '%s' and TIME < '%s'"%\
        (begin, end)
    return dataSend(cursor, sql)

if __name__ == '__main__':
   app.run()
