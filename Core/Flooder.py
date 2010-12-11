from multiprocessing import Queue
from Events import *
from main import *
from UDPWorkerThread import *
from TCPWorkerThread import *
from SYNWorkerThread import *
import synmod

class Flooder:

    def __init__(self, host, port, timeout, method, threads, subsite, message, Random, wait, srchost, srcport):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.method = method
        self.threadsAmount = threads
        self.__processes = []
        self.wait = wait
        self.speed = speed
        self.subsite = subsite
        self.message = message
        self.random = random
        self.threadId = 0
        self.byteCount = Queue.Queue()
        self.srchost = srchost
        self.srcport = srcport

        if method == TCP_METHOD or method == UDP_METHOD:
            if message == None and random == False:
                print "Message missing, not starting."
                return
        elif method == SYN_METHOD:
            synmod.init(srchost, srcport, host, port)
        if method == HTTP_METHOD:
            print "Not yet implemented, not starting."
            return

    def start(self):
        if len(self.__processes) > 0:
            return

        for x in range(self.threadsAmount):
            p = None
            if self.method == TCP_METHOD:
	            p = TCPWorkerThread(self, self.threadId)
            elif self.method == UDP_METHOD:
	            p = UDPWorkerThread(self, self.threadId)
            elif self.method == SYN_METHOD:
	            p = SYNWorkerThread(self, self.threadId)
            self.threadId += 1
            self.__processes.append(p)
            p.start()

    def stop(self):
        while len(self.__processes) > 0:
            p = self.__processes.pop()
            p.stop()
            p.terminate() #This will leave some defunct threads, but they will be reaped upon starting automatically.

        byteCount = 0
        #print "len:", self.byteCount.qsize()
        while 1:
            try:
                b = self.byteCount.get(True, 2)
                byteCount += b
                #print "b:", b
            except:
                #print "failed to get"
                break

        print "final byteCount:", byteCount

