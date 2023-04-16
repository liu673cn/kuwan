#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import base64
import math
import json
import requests
import urllib
from urllib import request, parse
import urllib.request
import re

class Spider(Spider):
	def getName(self):
		return "喝茶影视"
	def init(self,extend=""):
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电影": "1",
			"电视剧": "2",
			"综艺": "3",
			"动漫": "4"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name': k,
				'type_id': cateManual[k]
			})

		result['class'] = classes
		if (filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		rsp = self.fetch('http://www.dgdeyue.com/')
		htmlTxt = rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'class="myui-vodlist__thumb lazyload"\shref="(?P<url>.+?)"\stitle="(?P<title>.+?)"\sdata-original="(?P<img>.+?)"')
		result = {
			'list': videos
		}
		return result

	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		url = 'http://www.dgdeyue.com/xfenlei{0}-/page/{1}.html'.format(tid,pg)
		rsp = self.fetch(url)
		htmlTxt=rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'class="myui-vodlist__thumb lazyload"\shref="(?P<url>.+?)"\stitle="(?P<title>.+?)"\sdata-original="(?P<img>.+?)"')
		pag=self.get_RegexGetText(Text=htmlTxt,RegexText=r'href="/fenlei\d*?-(\d+?).html">尾页</a>',Index=1)
		if pag=="":
			pag=999
		numvL = len(videos)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pag
		result['limit'] = numvL
		result['total'] = numvL
		return result

	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		url='http://www.dgdeyue.com{0}'.format(idUrl)
		rsp = self.fetch(url)
		htmlTxt = rsp.text
		line=self.get_RegexGetTextLine(Text=htmlTxt,RegexText=r'href="#playlist\d"\sdata-toggle="tab">(.+?)</a>',Index=1)
		if len(line)<1:
			return  {'list': []}
		playFrom = []
		videoList=[]
		vodItems = []
		circuit=self.get_lineList(Txt=htmlTxt,mark=r'<ul class="myui-content__list sort-list clearfix',after='</ul>')
		playFrom=[t for t in line]
		pattern = re.compile(r'href="(.+?)">(.+?)</a>')
		for v in circuit:
			ListRe=pattern.findall(v)
			vodItems = []
			for value in ListRe:
				vodItems.append(value[1]+"$"+value[0])
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)

		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)
		typeName=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<span class="text-muted">分类：(.*?)地区：',Index=1)
		year=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<a rel="nofollow" href="/xfenlei\d-\d{4}.html">(\d{4})</a>',Index=1)
		area=self.get_RegexGetText(Text=htmlTxt,RegexText=r'地区：(.*?)年份',Index=1)
		act=self.get_RegexGetText(Text=htmlTxt,RegexText=r'主演：(.*?)</p>',Index=1)
		dir=self.get_RegexGetText(Text=htmlTxt,RegexText=r'导演：(.*?)</p>',Index=1)
		cont=self.get_RegexGetText(Text=htmlTxt,RegexText=r'简介：(.*?)</p>',Index=1)
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.removeHtml(txt=typeName),
			"vod_year": self.removeHtml(txt=year),
			"vod_area": self.removeHtml(txt=area),
			"vod_remarks": '',
			"vod_actor":  self.removeHtml(txt=act),
			"vod_director": self.removeHtml(txt=dir),
			"vod_content": self.removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		return result

	def verifyCode(self):
		pass

	def searchContent(self,key,quick):
		Url='http://www.dgdeyue.com/vodsearch{0}.html'.format(urllib.parse.quote(key))
		rsp = self.fetch(Url)
		htmlTxt = rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'class="myui-vodlist__thumb.+?"\shref="(?P<url>.+?)"\stitle="(?P<title>.+?)"\sdata-original="(?P<img>.+?)">')
		result = {
				'list': videos
			}
		return result

	def playerContent(self,flag,id,vipFlags):
		result = {}
		parse=1
		Url='http://www.dgdeyue.com{0}'.format(id)
		rsp = self.fetch(Url)
		htmlTxt = rsp.text
		m3u8Line=self.get_RegexGetTextLine(Text=htmlTxt,RegexText=r'url":"(\w+?)",',Index=1)
		if len(m3u8Line)>0:
			Url=m3u8Line[0].replace("/","")
			Url=str(base64.b64decode(Url),'utf-8')
			Url=urllib.parse.unquote(Url)
		if Url.find('.m3u8')<1:
			parse=0
			Url='http://www.dgdeyue.com{0}'.format(id)
		result["parse"] = parse
		result["playUrl"] = ''
		result["url"] = Url
		result["header"] = ''
		return result
	def get_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.I)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	def get_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def get_playlist(self,Text,headStr,endStr):
		circuit=""
		origin=Text.find(headStr)
		if origin>8:
			end=Text.find(endStr,origin)
			circuit=Text[origin:end]
		return circuit
	def removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	
	def get_list(self,html,patternTxt):
		ListRe=re.finditer(patternTxt, html, re.M|re.S)
		videos = []
		for vod in ListRe:
			url = vod.group('url')
			title =vod.group('title')
			img =vod.group('img')
			if len(url) == 0:
				url = '_'
			videos.append({
				"vod_id":"{0}###{1}###{2}".format(title,url,img),
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	def get_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit
	config = {
		"player": {},
		"filter": {}
	}
	header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
		'Host': 'www.dgdeyue.com'
	}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
