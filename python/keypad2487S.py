import commands

from device import Device
from commands import insteon
from threading import Timer
from linkdb import *

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	insteon.out().println(msg)

class DBBuilder(MsgListener):
        addr   = None
        timer  = None
        db = {};
        def __init__(self, addr):
                self.addr = addr
        def start(self):
                insteon.addListener(self)
                msg = commands.createExtendedMsg(InsteonAddress(self.addr), 0x2f, 0, 0, 0, 0)
                msg.setByte("userData1", 0);
                msg.setByte("userData2", 0);
                msg.setByte("userData3", 0);
                msg.setByte("userData4", 0);
                msg.setByte("userData5", 0);
                commands.writeMsg(msg)
                out("sent query msg ... ")
                self.timer = Timer(20.0, self.giveUp)
                self.timer.start()

        def restartTimer(self):
                if self.timer:
                        self.timer.cancel()
                self.timer = Timer(20.0, self.giveUp)
                self.timer.start()

        def giveUp(self):
                out("did not get full database, giving up!")
                insteon.removeListener(self)
                self.timer.cancel()

        def done(self):
                insteon.removeListener(self)
                if self.timer:
                        self.timer.cancel()
                dumpDB(self.db)
                out("database complete!")
                
        def msgReceived(self, msg):
                self.restartTimer()
                if msg.isPureNack():
                        out("got pure NACK")
                        return
                if msg.getByte("Cmd") == 0x62:
                        out("query msg acked!")
                elif msg.getByte("Cmd") == 0x51:
                        off   = (msg.getByte("userData3") & 0xFF) << 8 | (msg.getByte("userData4") & 0xFF)
                        rb    = msg.getBytes("userData6", 8); # ctrl + group + [data1,data2,data3] + whatever
                        ltype = rb[0] & 0xFF
                        group = rb[1] & 0xFF
                        data  = rb[2:4]
                        addr  = InsteonAddress("00.00.00")
                        if (ltype & 0x02 == 0):
                                self.done()
                                return
                        rec   = {"offset" : off, "addr": addr, "type" : ltype, "group" : group, "data" : data}
                        addRecord(self.db, rec)
                        dumpRecord(rec)
                else:
                        out("got unexpected msg: " + msg.toString())


class keypad2487S(Device):
    dbbuilder = None
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder(addr)
    def getdb(self):
        self.dbbuilder.start()
