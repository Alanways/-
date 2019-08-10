
from urllib import request,parse
import random,time
tzkeyword=["仝卓 神奇的汉字","#仝卓 山路十八弯# ","仝卓民歌","仝卓 九儿"]
gthkeyword=["高天鹤转正","高天鹤玫瑰人生" ,"高天鹤 天天向上","高天鹤中餐厅"]
c=0
while True:
	i=random.randint(1, len(tzkeyword))
	if c%2==0:
		keyword=parse.quote(tzkeyword[i-1])
	else:
		keyword=parse.quote(gthkeyword[i-1])
	url="https://s.weibo.com/weibo?q="+keyword
	request.urlretrieve(url,"shua.html")
	print(parse.unquote(url))
	c+=1
	time.sleep(15)

