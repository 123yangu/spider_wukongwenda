# Copyright 2019 ccy Individual. All Rights Reserved.
import sqlite3  # 数据模块
import re  # 正则
import time, datetime
import time  # 时间模块
from bs4 import BeautifulSoup  # 解析网址模块
from selenium import webdriver  # 浏览器模块


def create_tb():  ##创建一个函数
    sql = (
        "create table if not exists tb_wukong("
        "id integer primary key autoincrement, "
        "url varchar(100), "      #问题地址
        "channels varchar(100), "  # 关键词
        "question varchar(100), "  # 问题标题
        "answer varchar(100), "  # 回答数量
        "follow varchar(100), "  # 收藏数量
        "like varchar(100), "  # 点赞数量
        "spider_time varchar(100), "  # 爬取时间
        "review varchar(100))"  # 评论数量
    )

    with sqlite3.connect(R"C:\Users\Administrator\Desktop\db_wukong.db") as conn:  ##链接数据库
        cursor = conn.cursor()  ##获得游标
        cursor.execute(sql)  ##执行命令
        conn.commit()  ##


def create_wukong_answer_tb():  ##创建一个函数
    sql = (
        "create table if not exists wukong_answer("
        "id integer primary key autoincrement, "
        "url varchar(100), "  # 详情链接
        "channels varchar(100), "  # 关键词
        "answer_content TEXT, "    #回复内容
        "like_num varchar(100), "  # 点赞数量
        "spider_time varchar(100), "  # 爬取时间
        "answer_comment_num varchar(100))"  # 评论数量
    )

    with sqlite3.connect(R"C:\Users\Administrator\Desktop\db_wukong.db") as conn:  ##链接数据库
        cursor = conn.cursor()  ##获得游标
        cursor.execute(sql)  ##执行命令
        conn.commit()  ##


create_tb()
create_wukong_answer_tb()

word = input()  # 手动输入关键词，如果你有固定的关键词可以替换成‘word='keyword'’
urls = 'https://www.wukong.com/search/?keyword={}'.format(word)  # 关键词对应的网址
driv = webdriver.Chrome()  ##启动谷歌浏览器
driv.get(urls)  # 在谷歌浏览器中打开网址
driv.set_page_load_timeout(30)  # 设定时间，然后捕获timeout异常


# 创建一个模拟滚动条滚动到页面底部函数
def scroll(driv):
    driv.execute_script("""   
    (function () {   
        var y = document.body.scrollTop;   
        var step = 100;   
        window.scroll(0, y);   


        function f() {   
            if (y < document.body.scrollHeight) {   
                y += step;   
                window.scroll(0, y);   
                setTimeout(f, 50);   
            }  
            else {   
                window.scroll(0, y);   
                document.title += "scroll-done";   
            }   
        }   


        setTimeout(f, 1000);   
    })();   
    """)


print("开始模拟鼠标拉到文章底部")
b = 0
c = 0
while b < 63:  # 设置循环，可替换这里值来选择你要滚动的次数，滚动1次大概8篇内容左右
    scroll(driv)  # 滚动一次
    b = b + 1
    print('拉动{}次'.format(b))
    c = c + 3
    time.sleep(c)  # 休息c秒的时间\
    soup_is_more = BeautifulSoup(driv.page_source, "html.parser")  # 解析当前网页
    is_more_content = soup_is_more.find('div', class_="w-feed-loadmore").find('span', class_="w-feed-loadmore-w").text  # 获得最后滚动的加载文字是否为“没有更多内容”
    # print(is_more_content)
    if is_more_content == '没有更多内容':#如果没有下一页直接结束拉动滑条
        break

# 这个时候页面滚动了多次，是你最终需要解析的网页了
soup = BeautifulSoup(driv.page_source, "html.parser")  # 解析当前网页
a = 1

def question_answer_content(url, channels):
    driv_answer_content = webdriver.Chrome()  ##启动谷歌浏览器
    # 获取详情url回答数据
    driv_answer_content.get(url)  # 在谷歌浏览器中打开网址
    driv_answer_content.set_page_load_timeout(30)  # 设定时间，然后捕获timeout异常
    soup_answer_html = BeautifulSoup(driv_answer_content.page_source, "html.parser")  # 解析当前网页
    for li_answer_node in soup_answer_html.find_all('div', class_="answer-item sticky-item req_1"):
        answer_content = li_answer_node.find('div', class_="answer-text-full rich-text").text  # 回答内容
        like_num = li_answer_node.find('span', class_="like-num").text  # 回答
        try:  # 捕获异常
            answer_comment_num = re.findall("\d+", li_answer_node.find('a', class_="show-comment").text)[0]  # 检验语句
        except BaseException:  # 异常类型
            answer_comment_num = 0  # 如果检验语句有异常，那么执行这一句
        else:  # 如果没有异常，那么执行下一句
            answer_comment_num = re.findall("\d+", li_answer_node.find('a', class_="show-comment").text)[0]  # 评论

        print("文章回答内容：" + answer_content)
        wukong_answer_data = (None, url, answer_content, like_num, answer_comment_num, int(time.time()), channels)
        with sqlite3.connect(R"C:\Users\Administrator\Desktop\db_wukong.db") as conn:
            wukong_answer_data_sql = (
                "insert into wukong_answer"
                "(id,url,answer_content,like_num,answer_comment_num,spider_time,channels)"
                "values ( ?,?, ?,?,?,?,?)")
            cursor = conn.cursor()
            cursor.execute(wukong_answer_data_sql, wukong_answer_data)
            conn.commit()
    driv_answer_content.quit();


for li in soup.find_all('div', class_="question-v3"):
    channels = word
    url = 'www.wukong.com' + li.a['href']  # 每个文章的地址
    question_answer_content('http://' + url, channels);
    question = li.find('a', target="_blank").text

    try:  # 捕获异常
        answer = re.findall("\d+", li.find('span', class_="question-answer-num").text)[0]  # 回答
    except BaseException:  # 异常类型
        answer = 0  # 如果检验语句有异常，那么执行这一句
    else:  # 如果没有异常，那么执行下一句
        answer = re.findall("\d+", li.find('span', class_="question-answer-num").text)[0]  # 回答

    try:  # 捕获异常
        follow = re.findall("\d+", li.find('span', class_="question-follow-num").text)[0]  # 收藏
    except BaseException:  # 异常类型
        follow = 0  # 如果检验语句有异常，那么执行这一句
    else:  # 如果没有异常，那么执行下一句
        follow = re.findall("\d+", li.find('span', class_="question-follow-num").text)[0]  # 收藏

    try:  # 捕获异常
        like = li.find('span', class_="like-num").text  # 检验语句
    except BaseException:  # 异常类型
        like = 0  # 如果检验语句有异常，那么执行这一句
    else:  # 如果没有异常，那么执行下一句
        like = li.find('span', class_="like-num").text  #
    try:  # 同上
        review = li.find('span', class_="comment-count").text  # 评论总数量
    except BaseException:
        review = 0
    else:
        review = li.find('span', class_="comment-count").text

    one = (None, url, channels, question, answer, follow, like, review, int(time.time()))

    if follow == '暂无收藏':  # 如果问题没人收藏，那么跳过该问题
        continue
    elif question == '':  # 如果问题没有文字，跳过该问题
        continue
    elif int(like) == 0:  # 如果点赞人数为0，那么跳过该问题，在这里可以设置
        continue
    elif int(review) == 0:
        continue
    elif a < 500:  # 这里可以你需要爬取的问题的个数，如果已经爬取小于50个问题，那么爬下这个问题。
        print("正在爬取第{}篇文章".format(a))
        with sqlite3.connect(R"C:\Users\Administrator\Desktop\db_wukong.db") as conn:
            sql = (
                "insert into tb_wukong"
                "(id,url,channels,question,answer,follow,like,review,spider_time)"
                "values ( ?,?, ?,?,?,?, ?, ?,?)")
            cursor = conn.cursor()
            cursor.execute(sql, one)
            conn.commit()
            a = a + 1
        continue

    else:  # 如果不满足以上条件，直接跳出循环，停止爬虫
        break

print("抓完咯")
print("关闭浏览器")
driv.quit()
