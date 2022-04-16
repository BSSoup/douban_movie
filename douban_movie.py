# coding = utf-8
# vesion =1.6，对各模块用独立函数定义,下载器更改为TR下载，增加新的资源站，增加多豆瓣账号支持，对部分站点增加电影清晰度和资源大小选择偏好。
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 依赖库
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
# emby依赖
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
# transmission的依赖
import transmissionrpc
# **************************************************************************************************************
# 基础信息设置(以下信息需要在运行前手动设置）
# 设置豆瓣账号信息
users = ["user1", "user2"]  #填写豆瓣的id，多个账号请用逗号分隔
wish_time = 5 # 设置想要的检索日期天数(day)
# 设置Emby库信息
embykey = "xxxxx"   #设置emby库的key信息,如之前未设置需要去emby管理页面设置新增
emby_address="http://地址:端口"  #此处地址可以设置内网地址也可以设置外网地址，内网地址则只能在内网访问和运行
# 设置音丝范资源清晰度检索顺序,运行时候会按清晰度顺序检索,冒号后面的值表示下载时候会选取该清晰度下最接近该数字的资源大小（GB）下载
check_order = {"4K": 20, "蓝光原盘": 20, "蓝光高清": 10, "WEB-DL": 10}
# 定义tr的访问信息
tr_address = 'xxxxxx' #设置Tr的调用地址
tr_port = 9091  #设置Tr的调用端口，通常为9091，不是则改掉
tr_user = 'xxx'  #设置tr的登录用户名
tr_password = 'xxxxxx' #设置Tr的登录密码
out_path = r'/volumeUSB1/usbshare/torrents'  # 下临时种子载保存地址（已经取消种子下载方式，设置无效，可不管）
#设置微信推送端口信息
push_token="xxxxxxxxxxxx" #设置push-plus的群组或个人token
push_title="xxxxxxxxx"   #设置推送时候显示的标题名称
push_topic="xxxxxxxx"   #群组推送时需要设置，设置对应的群组名称，如果只推送给个人无需设置
# ***************************************************************************************************************
# charmdriver设置
prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': out_path}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', prefs)
# 浏览器隐式启动
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Remote("http://172.17.0.7:4444/wd/hub", options=options)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 定义豆瓣函数，打开豆瓣,返回想要的电影信息（包括电影名称）
def douban(user, wish_time):
    for user in users:
        print('开始获取 %s 的想看电影信息' % user)
        print('开始打开豆瓣电影页面')
        # 看看总共有多少页
        browser.get(
            'https://movie.douban.com/people/' + str(user) + '/wish?start=0&sort=time&rating=all&filter=all&mode=grid')
        try:
            browser.implicitly_wait(10)
            paginator = browser.find_element_by_class_name('paginator')
            page = paginator.text.split()[-2]
        except:
            page = 0
        print("页数为： ", int(page) + 1)
        titles = []
        year = []
        adddate = []
        # notice_user = []
        i = 0
        kill = 0
        for i in range(int(page) + 1):
            if kill != 1:
                print("开始检索第", i + 1, "页")
                j = 0
                url = 'https://movie.douban.com/people/' + str(user) + '/wish?start=' + str(
                    i * 15) + '&sort=time&rating=all&filter=all&mode=grid'
                browser.get(url)
                browser.implicitly_wait(10)
                # 寻找电影标题/上映年份/加入想看日期
                title = browser.find_elements_by_class_name('title')
                intros = browser.find_elements_by_class_name('intro')
                dates = browser.find_elements_by_class_name('date')
                for j in range(len(title)):
                    # 识别电影剧标题
                    x = title[j].text
                    x = x.split("/")[0]
                    x = x[:-1]
                    titles.append(x)
                    print("电影标题：%s" % titles[j])
                    # 识别电影剧上映日期
                    # y = intros[j].text
                    # y = y[0:4]
                    # if y.isdigit():
                    #    year.append(y)
                    # else:
                    #    year.append(None)
                    # print("上映日期：%s" % year[j])
                    # 识别加入想看日期
                    z = dates[j].text
                    print("加入日期%s" % z)
                    z = datetime.datetime.strptime(z, '%Y-%m-%d')
                    adddate.append(z)
                    now_time = datetime.datetime.now()
                    interval = now_time - z
                    interval = interval.days
                    print("加入想看时距今%s天" % interval)
                    if interval > wish_time:
                        kill = 1
                        print('加入想看日期已经超过设定天数，即将退出检索')
                        break
        # for i in range(len(titles)):
        #    if year[i] == None:
        #        notice_user.append(titles[i])
        #    else:
        #        notice_user.append(str(str(titles[i]) + "(" + str(year[i]) + ")"))
        # notice_douban.append(notice_user)
        notice_douban.append(titles)
    return notice_douban
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 定义emby函数，打开Emby,获取Emby上的电影和电视剧信息
def emby(embykey):
    emby = []
    # 定义电影和电视剧的api接口
    url1 = emby_address+"/emby/users/bc3b0d5386444f27b836b0617fd43428/Items?Recursive=true&IncludeItemTypes=Movie&api_key=" + embykey
    url2 = emby_address+ "/emby/users/bc3b0d5386444f27b836b0617fd43428/Items?Recursive=true&IncludeItemTypes=Episode&api_key=" + embykey
    # 读取网页内容
    html1 = urlopen(url1)
    html2 = urlopen(url2)
    bsObj1 = BeautifulSoup(html1.read(), features="html.parser")
    bsObj2 = BeautifulSoup(html2.read(), features="html.parser")
    # 难以识别只能通过格式化为text再去清洗
    a1 = bsObj1.get_text()
    a2 = bsObj2.get_text()
    emby_movie_list = []
    emby_Episode_list = []
    # 分别寻找电影/电视剧字符串中第一个和最后一个方括号（[]），再切掉方括号前后的内容，刚好可以转化为元素为字典的列表
    i = 0
    j = 0
    x = y = 2
    m1 = m2 = 0
    e1 = e2 = 0
    for i in range(len(a1)):
        if a1[i] == '[':
            m1 = i

            x = x - 1
        if a1[-i] == ']':
            m2 = i
            x = x - 1
        if x == 0:
            break
    b1 = json.loads(a1[m1:1 - m2])

    for j in range(len(a2)):
        if a2[j] == '[':
            e1 = j
            y = y - 1
        if a2[-j] == ']':
            e2 = j
            y = y - 1
        if y == 0:
            break
    b2 = json.loads(a2[e1:1 - e2])
    # 将电影和电视剧列表中字典里面的Name下的值单独抽取，组成电影和电视剧名字的列表
    for i in range(len(b1)):
        emby_movie_list.append(b1[i]["Name"])
    for j in range(len(b2)):
        if b2[j]["SeasonName"] == '独季':
            emby_Episode_list.append(b2[j]["SeriesName"])
        else:
            x = str(b2[j]["SeriesName"]) + " " + str(b2[j]["SeasonName"])
            emby_Episode_list.append(x)
    print("EMBY中电影总个数为：", len(emby_movie_list))
    print("EMBY中电视剧总个数为：", len(emby_Episode_list))
    emby.append(emby_movie_list)
    emby.append(emby_Episode_list)
    return emby
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 定义对比函数，对比豆瓣想看和emby库的电影/电视剧,对输入的两个list,返回list1中不在list2中的值
def checkinfo(douban, emby):
    search_list = []
    for i in range(0, len(users), 1):
        for j in range(0, len(douban[i]), 1):
            if (douban[i][j] not in emby[0]) & (douban[i][j] not in emby[1]):
                search_list.append(douban[i][j])
    return search_list
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
def pianyuan_cookie():
    # 打开片源网主页
    browser.get('https://pianyuan.org/')
    browser.implicitly_wait(10)
    # 清除cookie
    browser.delete_all_cookies()
    # 加载cookie
    with open('cookies.txt', 'r') as f:
        # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
        cookies_list = json.load(f)
        # 方法1 将expiry类型变为int
        for cookie in cookies_list:
            # 并不是所有cookie都含有expiry 所以要用dict的get方法来获取
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry'])
            browser.add_cookie(cookie)
        # 方法2删除该字段
        # for cookie in cookieslist:
        #     # 该字段有问题所以删除就可以
        #     if 'expiry' in cookie:
        #         del cookie['expiry']
        #     driver.add_cookie(cookie)
    # 刷新网页
    browser.get('https://pianyuan.org/')
    return None
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 定义片源网资源搜索函
def pianyuan(movie_name):
    download_result = 0
    url11 = "https://pianyuan.org/search?q=" + str(movie_name)
    browser.get(url11)
    browser.implicitly_wait(10)
    time.sleep(2)
    # 点击进入资源详情页面
    try:
        browser.find_element_by_class_name("text-danger").click()
        browser.implicitly_wait(5)
        windows = browser.window_handles
        browser.switch_to.window(windows[-1])
        # 开始列举筛选资源信息
        # 首先看看有几种清晰度可选（因为当有多种清晰度可选时候xpath地址不一样
        fa = browser.find_element_by_class_name('data')
        chi = fa.find_elements_by_class_name('nobr')
        torrinf = []
        torrinfo = []
        torrlink = []
        for i in chi:
            # print(i.text)
            torrinf.append(i.text)
        # 筛选出表示资源大小的元素
        del torrinf[0]
        del torrinf[0]
        if "集" in str(torrinf[0]):
            print('这是一个电视剧，按照电视剧逻辑筛选')
            # 看看总共有多少集
            epsinfo = browser.find_element_by_xpath('/html/body/div[2]/div/div/div/h1/small[1]')
            eps = str(epsinfo.text)
            k1 = 0
            for i in range(len(eps)):
                if eps[i] == '(':
                    k1 = i
            eps = int(eps[k1 + 2:-2])
            print('该电视剧的当前总集数为：', eps)
            epslist = []  # 创建第一清晰度有种子的剧集清单
            for i in range(0, len(torrinf), 4):
                epslist.append(torrinf[i])
            # print(epslist)
            # 筛选出第一个清晰度区域的下载链接
            links = fa.find_elements_by_class_name('ico')
            torrlink = []
            for i in links:
                torrlink.append(i.get_attribute('href'))
            # print(torrlink)
            # 如果有全集，优先下载全集资源
            if '全集' in epslist:
                torrent = torrlink[epslist.index('全集')]
                print('该资源第一清晰度有全集资源，开始下载全集资源')
                # 打开该资源下载的详情页面并切换到该页面
                browser.get(torrent)
                browser.implicitly_wait(10)
                windows = browser.window_handles
                browser.switch_to.window(windows[-1])
                torlinkfa = browser.find_element_by_class_name('tdown')
                torlinks = torlinkfa.find_elements_by_class_name('btn')
                # 种子链接参数(第一个是种子下载地址，第二个是磁力链接，第三个是字幕库字幕地址)
                torrentlink = []
                for i in torlinks:
                    torrentlink.append(i.get_attribute('href'))
                # 将资源添加到Tr下载中
                tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
                tc.add_torrent(torrent=torrentlink[1])
                notice_download_name.append(str(str(movie_name) + "全集"))
                download_result = 2
            # 如果无全集，按照每一集下载资源
            else:
                print('该资源第一清晰度无全集，开始分集下载')
                for i in range(1, eps):
                    print(i)
                    if i < 10:
                        xx = '第0' + str(i) + "集"
                        print("开始下载第：", i, "集")
                        print(xx)
                        torrent = torrlink[epslist.index(xx)]
                        # 打开该资源下载的详情页面并切换到该页面
                        browser.get(torrent)
                        browser.implicitly_wait(10)
                        windows = browser.window_handles
                        browser.switch_to.window(windows[-1])
                        torlinkfa = browser.find_element_by_class_name('tdown')
                        torlinks = torlinkfa.find_elements_by_class_name('btn')
                        # 种子链接参数(第一个是种子下载地址，第二个是磁力链接，第三个是字幕库字幕地址)
                        torrentlink = []
                        for i in torlinks:
                            torrentlink.append(i.get_attribute('href'))
                        # 将资源添加到TR下载中
                        tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user,
                                                    password=tr_password)
                        tc.add_torrent(torrent=torrentlink[1])
                        notice_download_name.append(str(str(movie_name) + str(xx)))
                    else:
                        xx = '第' + str(eps) + "集"
                        print("开始下载第s%集", i)
                        epsindex = epslist.index(xx)
                        torrent = torrlink[epsindex]
                        # 打开该资源下载的详情页面并切换到该页面
                        browser.get(torrent)
                        browser.implicitly_wait(10)
                        windows = browser.window_handles
                        browser.switch_to.window(windows[-1])
                        torlinkfa = browser.find_element_by_class_name('tdown')
                        torlinks = torlinkfa.find_elements_by_class_name('btn')
                        # 种子链接参数(第一个是种子下载地址，第二个是磁力链接，第三个是字幕库字幕地址)
                        torrentlink = []
                        for i in torlinks:
                            torrentlink.append(i.get_attribute('href'))
                        # 将资源添加到TR下载中
                        tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user,
                                                    password=tr_password)
                        tc.add_torrent(torrent=torrentlink[1])
                        notice_download_name.append(str(str(movie_name) + str(xx)))
                download_result = 1
            print('该电视剧第一清晰度下的资源下载完成,开始搜索下一部')
        else:
            print('这是一个电影，按照电影逻辑筛选')
            for i in range(len(torrinf)):
                if (i - 1) % 3 == 0:
                    torrinfo.append(torrinf[i])
            for i in range(len(torrinfo)):
                x = str(torrinfo[i])
                x = x[0:-2]
                torrinfo[i] = float(x)
            # 选出最最小的一个资源和其位置
            min_index = torrinfo.index(min(torrinfo))
            # 筛选出第一个清晰度区域的下载链接
            links = fa.find_elements_by_class_name('ico')
            for i in links:
                # print(i.get_attribute('href'))
                torrlink.append(i.get_attribute('href'))
            # print(torrlink)
            torrent = torrlink[min_index]
            # 打开该资源下载的详情页面并切换到该页面
            browser.get(torrent)
            browser.implicitly_wait(10)
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            torlinkfa = browser.find_element_by_class_name('tdown')
            torlinks = torlinkfa.find_elements_by_class_name('btn')
            # 种子链接参数(第一个是种子下载地址，第二个是磁力链接，第三个是字幕库字幕地址)
            torrentlink = []
            for i in torlinks:
                torrentlink.append(i.get_attribute('href'))
            # 将资源添加到TR下载中
            print("开始下载该资源，不再检索其他资源")
            tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
            tc.add_torrent(torrent=torrentlink[1])
            notice_download_name.append(movie_name)
            download_result = 2
            print("该电影已经下载完成")
    except:
        print("异常或无资源")
    return download_result
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 定义音丝范资源索引函数
def yinsifan(movie_name):
    # 打开音丝范搜索资源
    url = "https://www.yinfans.me/?s=" + str(movie_name)
    download_result = 0
    browser.get(url)
    try:
        # 确认搜索是否有资源
        browser.find_element_by_class_name("zoom").click()
        browser.implicitly_wait(10)
        windows = browser.window_handles
        browser.switch_to.window(windows[-1])
        try:
            browser.find_element_by_xpath('//*[@id="showall"]').click()
        except:
            print("异常或无资源")
        for key in check_order.keys():
            print("开始检索清晰度为 %s 的资源" % key)
            y = check_order[key]
            names = []
            magnets = []
            sizes = []
            xpathelement = '//*[@id="' + str(key) + '"]/td/a'
            try:
                # 进去资源网页，检索资源信息,按照检索顺序检索
                # links=browser.find_elements_by_id(check_order[0])
                links = browser.find_elements_by_xpath(xpathelement)
                for link in links:
                    size = link.find_element_by_class_name("label-warning")
                    size = str(size.text)[:-2]
                    size.replace(" ", "")
                    size = float(size)
                    size = round(size, 1)
                    sizes.append(size)
                    name = link.find_element_by_tag_name("b")
                    names.append(name.text)
                    magnets.append(link.get_attribute('href'))
                try:
                    # 选择最接近目标大小的资源
                    find_min_index = []
                    for i in sizes:
                        find_min_index.append(abs(i - y))
                    min_index = find_min_index.index(min(find_min_index))
                    # 调用Tr下载
                    tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
                    tc.add_torrent(torrent=magnets[min_index])
                    notice_download_name.append(movie_name)
                    print("清晰度为 %s 的资源存在，开始下载该资源，不再检索其他清晰度" % key)
                    print("资源成功添加下载，开始检索下一步电影")
                    download_result = 2
                    break
                except:
                    print("没有这个清晰度的资源")
            except:
                print("异常或无资源")
    except:
        print("异常或无资源")
    return download_result
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
#定义grab4k资源搜索函数
def garb4k(movie_name):
    # 打开grab4k搜索资源
    url = "https://www.grab4k.com/vod/search.html?wd=" + str(movie_name)
    download_result = 0
    magenets_4k=[]
    magenets_languang = []
    magenets_1080p = []
    sizes_4k=[]
    sizes_languang=[]
    sizes_1080p=[]
    browser.get(url)
    try:
        # 确认搜索是否有资源
        browser.find_element_by_class_name("video-serial").click()
        browser.implicitly_wait(10)
        windows = browser.window_handles
        browser.switch_to.window(windows[-1])
        time.sleep(3)
        try:
            torinfos = browser.find_elements_by_class_name('module-row-text')
            print("开始获取下载资源")
            for info in torinfos:
                x=info.get_attribute("title")
                x=x[len(movie_name)+4:-6]
                if x[:2]=="4K":
                    magenets_4k.append(info.get_attribute("data-clipboard-text"))
                    for i in range(len(str(x))):
                        if str(x)[i]=="[":
                            sizes_4k.append(float(x[i+1:]))
                elif x[:2]=="蓝光":
                    magenets_languang.append(info.get_attribute("data-clipboard-text"))
                    for i in range(len(str(x))):
                        if str(x)[i] == "[":
                            sizes_languang.append(float(x[i+1:]))
                elif x[:4]=="1080":
                    magenets_1080p.append(info.get_attribute("data-clipboard-text"))
                    for i in range(len(str(x))):
                        if str(x)[i] == "[":
                            sizes_1080p.append(float(x[i+1:]))
                else:
                    print("无资源信息")
            #清洗资源，去除网盘链接
            tempmag_4k=[]
            for x in range(len(magenets_4k)):
                if str(magenets_4k[x])[:6] != "magnet":
                    tempmag_4k.append(x)
            for x in reversed(tempmag_4k):
                del magenets_4k[x]
                del sizes_4k[x]
            tempmag_languang = []
            for y in range(len(magenets_languang)):
                if str(magenets_languang[y])[:6] != "magnet":
                    tempmag_languang.append(y)
            print(tempmag_languang)
            for y in reversed(tempmag_languang):
                del magenets_languang[y]
                del sizes_languang[y]

            print(magenets_languang,sizes_languang)
            tempmag_1080p = []
            for x in range(len(magenets_1080p)):
                if str(magenets_1080p[x])[:6] != "magnet":
                    tempmag_1080p.append(x)
            for x in reversed(tempmag_1080p):
                del magenets_1080p[x]
                del sizes_1080p[x]
            print(magenets_1080p,sizes_1080p)
            print("资源清洗完成")
            #检查资源，按照顺序下载
            print("开始下载资源，按照4K.蓝光，1080P顺序下载，4K和蓝光选择最小资源，1080P选择最大资源")
            if len(sizes_4k) != 0:
                min_size=sizes_4k.index(min(sizes_4k))
                print(magenets_4k[min_size])
                tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
                tc.add_torrent(torrent=magenets_4k[min_size])
                download_result = 2
                print("4K资源下载成功")
            elif (len(sizes_4k) == 0) & (len(sizes_languang) != 0):
                min_size = sizes_languang.index(min(sizes_languang))
                tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
                tc.add_torrent(torrent=magenets_languang[min_size])
                download_result = 2
                print("蓝光资源下载成功")
            elif (len(sizes_4k) == 0) & (len(sizes_languang) == 0) & (len(sizes_1080p) != 0):
                max_size = sizes_1080p.index(max(sizes_1080p))
                tc = transmissionrpc.Client(address=tr_address, port=tr_port, user=tr_user, password=tr_password)
                tc.add_torrent(torrent=magenets_1080p[max_size])
                download_result = 2
                print("1080P资源下载成功")
        except:
            print("异常或无资源")
    except:
        pass
    return download_result
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 对searchlist的电影/电视剧 进行资源搜索,并将检索到的资源加入TR下载
def downloader(search_list):
    for i in range(len(search_list)):
        movie_name=search_list[i]
        print("开始检索电影/电视：", movie_name)
        if pianyuan(movie_name) == 0:
            print("片源网没找到资源")
            if yinsifan(movie_name)==0:
                print("音丝范没找到资源")
                if garb4k(movie_name) ==0:
                    print("grab4k没有找到资源")
                else:
                    continue
            else:
                continue
        else:
            continue
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 消息推送函数
def notice_push(douban, emby, checklist):
    # 推送下载情况到手机端
    # 豆瓣新加入信息
    str_notice_douban = ""
    for i in range(0, len(users), 1):
        str_notice_douban = str_notice_douban + str(users[i]) + "新加入豆瓣想看的电影/电视剧： " + "\n"
        for j in range(0, len(douban[i]), 1):
            str_notice_douban = str_notice_douban + str(douban[i][j]) + "\n"
    # 不在本地库的信息
    str_notice_notin_emby_name = ''
    for i in range(0, len(checklist), 1):
        str_notice_notin_emby_name = str_notice_notin_emby_name + str(checklist[i]) + "\n"
    # 下载成功信息
    str_notice_download_name = ""
    for i in range(0, len(notice_download_name), 1):
        str_notice_download_name = str_notice_download_name + str(notice_download_name[i]) + "\n"
    cont = "最近" + str(
        wish_time) + "天:" + "\n" + str_notice_douban + "\n" + "其中不在EMBY库的有:" + "\n" + str_notice_notin_emby_name + "\n" + "此次检索下载成功的有：" + "\n" + str_notice_download_name
    content = {cont}
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": push_token,
        "title": push_title,
        "content": content,
        "topic": push_topic,
        "template": "json"
    }
    requests.post(url, data=data)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 主函数
notice_download_name = []
notice_douban = []
douban = douban(users, wish_time)
emby = emby(embykey)
checklist = checkinfo(douban, emby)
print("待检索的清单如下：", checklist)
pianyuan_cookie()
downloader(checklist)
notice_push(douban, emby, checklist)
print('本次运行结束，等待下次运行')
browser.quit()