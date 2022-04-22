from unittest import result
from urllib.request import Request
from flask import Flask, escape, request, url_for
from flask_cors import CORS
import json, pymysql, serial, datetime, ast


Time = datetime.datetime.now()
beginTime = datetime.datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")#传输开始时间

portx = "COM7"
bps = 115200
timex = 5
ser = serial.Serial(portx, bps, timeout = timex)

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

db.close()

def sqlInsert(db, res):
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
    except:
        # 发生错误时回滚
        db.rollback()
        print("wrong")
beginTime.minute
def sqlSelect(db, Time):
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
                    return row[1]
    except:
        print ("Error: unable to fetch data")

app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/*')

@app.route('/')
def data():
    global Time
    serial.Serial.flushInput(ser)
    data = ser.readline().decode().replace("\r\n", "")
    if(data):
        if(data != "-1" and data != ""):
            data = ast.literal_eval(data)
            now = datetime.datetime.now()
            print(data, type(data))
            if(isinstance(data, list) == True):
                res = '{ "data": '+ str(data) +' }'
                if((now - Time).seconds % 2 == 0):
                    sqlInsert(db, res)
                    Time = now
                    print("mysql load sucess at ")
                    print(Time)
                    print(sqlSelect(db, Time))
                    print(json.loads(sqlSelect(db, Time)))
                    return json.loads(sqlSelect(db, Time))
                else:
                    return '{ "data": "-1" }'
            else:
                return '{ "data": "-1" }'
        else:
            print("your data is trash")
            return '{ "data": "-1" }'
    else:
        print("ser is not open")
        return '{ "data": "-1" }'

@app.route("/find/<num>")
def find(num):
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    if(num == '1'):
        print("Im in 1 sql!")
        sql = "SELECT * FROM DATA \
            WHERE TIME > '%s' and TIME < '%s'"%\
            (beginTime.strftime('%Y-%m-%d %H:%M:%S'), (beginTime + datetime.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'))
        try:
            print("Im trying")
            db.ping(reconnect = True)
            # 执行sql语句
            cursor.execute(sql)
            print("sql commit sucess")
            results = cursor.fetchall()
            print("fetchall sucess!")
            print(results)
            # mylist =[]
            # for row in results:
            #     mylist.append(row[1])
            # print(mylist)
            print(json.dumps(results))
            return json.dumps(results)
        except:
            print("Error:unable to fetch data")
    return '{ "data": "-1" }'

if __name__ == '__main__':
   app.run()

ser.close()