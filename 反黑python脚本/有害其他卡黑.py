import requests
import rsa
import time
import re
import random
import urllib3
import base64
from urllib.parse import quote
from binascii import b2a_hex
urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)  # 获取13位时间戳

class WeiBo():
    def __init__(self,username,password,link,posttime):
        self.username = username
        self.password = password
        self.session = requests.session() #登录用session
        self.link=link
        self.posttime=posttime
        self.session.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        self.session.verify = False  # 取消证书验证
    
    def prelogin(self):
        '''预登录，获取一些必须的参数'''
        self.su = base64.b64encode(self.username.encode())  #阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(quote(self.su),get_timestamp()) #注意su要进行quote转码
        response = self.session.get(url).content.decode()
        # print(response)
        self.nonce = re.findall(r'"nonce":"(.*?)"',response)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"',response)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"',response)[0]
        self.servertime = re.findall(r'"servertime":(.*?),',response)[0]
        return self.nonce,self.pubkey,self.rsakv,self.servertime

    def get_sp(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey,16),int('10001',16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = rsa.encrypt(message.encode(),publickey)
        return b2a_hex(self.sp)

    def login(self):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
        'entry': 'weibo',
        'gateway': '1',
        'from':'',
        'savestate': '7',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
        'vsnf': '1',
        'su': self.su,
        'service': 'miniblog',
        'servertime': str(int(self.servertime)+random.randint(1,20)),
        'nonce': self.nonce,
        'pwencode': 'rsa2',
        'rsakv': self.rsakv,
        'sp': self.get_sp(),
        'sr': '1536 * 864',
        'encoding': 'UTF - 8',
        'prelt': '35',
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        }
        response = self.session.post(url,data=data,allow_redirects=False).text # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);',response)[0] # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url,allow_redirects=False).text  # 请求跳转页面
        ticket,ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"',result)[0] #获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(ticket,ssosavestate,get_timestamp())
        data = self.session.get(uid_url).text #请求获取uid
        uid = re.findall(r'"uniqueid":"(.*?)"',data)[0]
        print(uid)
        return uid
    def getlink(self):
        
        html = self.session.get(self.link)
        f=open("list.html","wb")
        f.write(html.text.encode())
        f.close()
        f=open("list.html","rb")
        data=f.read()
        f.close()
        pattern='\"text\": \".*?,'
        data=re.compile(pattern).findall(str(data))
        
        pattern="href=.*?data"
        data=re.compile(pattern).findall(str(data))

        link=[]
        for i in data:
            pattern='https://.*?\"'
            url=re.compile(pattern).findall(i)
            link+=url
        return link
    def complain(self,link,uid,time):
        url="https://service.account.weibo.com/aj/reportspamobile?__rnd=1565336262384"
        for i in link:

            try:
                html = self.session.get(i)
                f=open("complainindex.html","wb")
                f.write(html.text.encode())
                f.close()
                f=open("complainindex.html","rb")
                data=f.read()
                f.close()
                pattern="rid.*?&"
                rid=re.compile(pattern).findall(i)[0]
                rid=rid.replace("&","")
                rid=rid.replace("rid=","")
            
                pattern="r_uid.*?&"
                r_uid=re.compile(pattern).findall(str(data))[0]
                r_uid=r_uid.replace("&","")
                r_uid=r_uid.replace("r_uid=","")
            

            
                data={
                    "category": "8",
                    "tag_id": "804",
                    "url":"" ,
                    "type": "1",
                    "rid": rid,
                    "uid": uid,
                    "r_uid": r_uid,
                    "from": "20000",
                    "getrid": rid,
                    "appGet": "0",
                    "weiboGet": "0",
                    "blackUser": "0",
                    "_t": "0",
                }
                response = self.session.post(url,data=data,allow_redirects=False)

                print(response)
                time.sleep(time)
        

            except:
                pass

    def main(self):
        self.prelogin()
        self.get_sp()
        uid=self.login()
        link=self.getlink()
        self.complain(link,uid,posttime)
if __name__ == '__main__':
    username = str(input("请输入你的账号："))
    password = str(input("请输入你的密码：")) # 微博密码
    
    while True:
        try:
          link=str(input("请输入待卡黑链接，或输入quit退出:"))
          if link=="quit":
                break
          posttime=str(input("请输入时间间隔(控制举报提交速度，防止被关)："))

          weibo = WeiBo(username,password,link,int(posttime))
          weibo.main()
        except requests.exceptions.MissingSchema as linkerror:
            print("链接异常，需要http请求头")
        except ValueError as timeError:
            print("时间请输入一个整数")
        except IndexError as usererror:
            print ("账号异常，请重新运行脚本")
            break