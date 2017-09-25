#coding=utf-8

import urllib2,threading,json,time
from Queue import Queue
from lxml import etree

#设置编码环境
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class CrawlPageThread(threading.Thread):
    def __init__(self,pageQueue,dataQueue):
        #必须继承父类方法
        threading.Thread.__init__(self)
        self.count_list = []
        self.q1 = pageQueue
    def run(self):
        while True:
            if self.q1.empty():
                break
            else:
                page = self.q1.get()
                print self.name + '正在访问第%d页'%page
                url = 'http://www.qiushibaike.com/8hr/page/'
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'}
                new_url = url + str(page)
                request = urllib2.Request(new_url,headers = headers)
                response = urllib2.urlopen(request)
                html = response.read()
                #此处要注意，放入解析队列的页面不是按照page顺序排列的，为了记录放入页面的顺序，单独创建一个列表来记录获取的顺序
                dataQueue.put({str(page):html})
                print self.name + '第%d页页面已获取'%page
                time.sleep(0.5)

class ParsePageThread(threading.Thread):
    def __init__(self,dataQueue):
        threading.Thread.__init__(self)
        self.data = dataQueue
        print self.name + '创建完'
    def run(self):
        while True:
            if self.data.empty():
                break
            else:
                page_dict =dataQueue.get()
                #保存的页面格式为{页数：内容}
                for k,v in page_dict.items():
                    print self.name + '正在解析第%d页面'%int(k)
                    html = etree.HTML(v)
                    result = html.xpath('//div[contains(@id,"qiushi_tag")]')
                    #解析该页面下用户的信息，并单个写入json文件中
                    for site in result:
                        try:
                            imgUrl = site.xpath('./div/a/img/@src')[0].encode('utf-8')
                        except:
                            imgUrl = '没有头像'
                        username = site.xpath('.//h2')[0].text.strip()
                        content = site.xpath('.//div[@class="content"]/span')[0].text.strip().encode('utf-8')
                        vote = site.xpath('.//i')[0].text
                        comments = site.xpath('.//i')[1].text
                        dict_str = {'头像地址':imgUrl,'用户名':username,'内容':content,'点赞数':vote,'评论数':comments}
                        json_dict = json.dumps(dict_str,ensure_ascii=False)
                        #因为是在单个线程内写入文件，所以没有必要引入互斥锁
                        #如果所有线程写入同一个文件，则要引入互斥锁
                        with open ('第%s页的数据.json'%k,'a') as f :
                            f.write(json_dict+'\n')
                    print self.name + '第%s页已解析完'%k

#数据队列必须为全局变量，为了在采集页面后能够写入
dataQueue = Queue()

def main():
    #第一步，创建页面与网页源码队列，供各线程去爬取
    pageQueue = Queue()
    crawllist = []
    parselist = []
    for i in range(1,5):
        pageQueue.put(i)
    #第二步，创建三个爬取页面的进程，执行start去获取网页
    for i in range(3):
        crawlthread = CrawlPageThread(pageQueue,dataQueue)
        crawlthread.start()
        #向创建的空列表添加每个线程，为了让每个线程调用join方法执行完再退出，下同
        crawllist.append(crawlthread)
    for i in crawllist:
        i.join()
    #第三步，创建解析界面的thread，并将结果写入文件
    for i in range(3):
        parsethread = ParsePageThread(dataQueue)
        parsethread.start()
        parselist.append(parsethread)
    for i in parselist:
        i.join()

if __name__ == '__main__':
    main()

