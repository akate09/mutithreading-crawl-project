# mutithreading-crawl-project
此项目是基于多线程来写的爬虫框架，主要是提供一个思路，细节有很多可以完善的地方
基本思路如下：

等待爬取的页面队列pageQueue--->爬页面的线程Crawlthread(1,2,3…)--->将爬到的页面传入到等待解析队列dataQueue--->parsethread（1，2，3……）解析页面并保存
