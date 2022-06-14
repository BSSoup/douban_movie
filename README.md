# douban_movie
电影下载机器人

功能说明：本程序支持在指定系列豆瓣用户的想看电影页爬取指定加入想看的日期内的电影，然后检查个人Emby电影库中的资源，对不在电影库中的电影，到指定网站去检索，能找到资源后按照自定义顺序和选择偏好提取资源下载链接，然后用transmission软件去下载，然后通过微信的pushplus推送信息到微信上。程序当前为个人使用，基于个人环境搭建，不保证在其他环境可以运行。

使用条件：
1. 豆瓣账号；
2. Emby本地影视库，且影视库元数据信息需要准确；
3. 支持selenium的本地可调用chrome浏览器及驱动webdriver，如在群晖中运行可以在docker中安装selenium-chrome镜像；
4. python3环境及对应依赖库
5. transmission（程序是基于群晖中transmission的调用地址/端口运行）
6. push plus账号推送信息

使用方法：
（如图片不显示直接下载文件，里面有教程截图）

![iamge](https://github.com/BSSoup/douban_movie/blob/main/%E5%BC%A0%E5%A4%A7%E5%A6%88%E6%9C%AA%E8%BF%87%E5%AE%A1%E6%95%99%E7%A8%8B%E6%88%AA%E5%9B%BE.jpg)

2022-6-14更新：增加人人影视的资源（用的人人影视数据库，需要自己到人人影视网站下载和更新数据库，地址：https://yyets.dmesg.app/database ，选择的是sqlite，解压后放在代码统一文件夹运行）
