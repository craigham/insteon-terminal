#-------------------------------------------------------------------------------
#
# Insteon IO linc 2450
#

import iofun
import message

from device import Device
from switch import Switch
from querier import Querier
from querier import MsgHandler
from threading import Timer
from linkdb import *
from device import LinkRecordAdder
from dbbuilder import GenericDBBuilder
from linkdb import LightDBRecordFormatter

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)
def outchars(msg = ""):
	iofun.outchars(msg)


class ContactStatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l

	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		iofun.out(self.label + " = " + ('OPEN' if tmp else 'CLOSED'))
		return 1

class RelayStatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l

	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		iofun.out(self.label + " = " + ('ON' if tmp else 'OFF'))
		return 1

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		iofun.out(self.label + " got msg: " + msg.toString())
		return 1

class IOLinc2450(Device):
	"""==============  Insteon I/O Linc 2450 ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01)

	def getContactStatus(self):
		self.querier.setMsgHandler(ContactStatusMsgHandler("contact state"))
		self.querier.querysd(0x19, 0x1)

	def getRelayStatus(self):
		self.querier.setMsgHandler(RelayStatusMsgHandler('Relay state'))
		self.querier.querysd(0x19, 0x0)

	def on(self, level=0xFF):
		"""on(level)
        switch on to given light level"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x11, level, -1))

#
# somebody should figure out how this thing works ... why not YOU?
#


