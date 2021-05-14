# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
# socket.setdefaulttimeout(0.5)

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=.01, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive()  # receive data
                 self.logger.info("Got data from socket: {}".format(data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                 sys.stdout.write(data)
                 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()

class MyReceiver(Receiver):
    # ACK_DATA = b'11111111'
    # NACK_DATA = b'00000000'
    ACK_DATA = bytearray([1,1,1,1,1,1,1,1])
    NACK_DATA = bytearray([0,0,0,0,0,0,0,0])

    def __init__(self):
        super(MyReceiver, self).__init__()
        self.index = 0
        self.first = True
        self.last = False
    
    def receive(self):
        #self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                if self.index < 0 or self.last:
                   self.logger.info("Stopping now") 
                #    sys.stdout.write(self.fullData)
                   sys.exit()
                   break
                data = self.simulator.u_receive()  # receive data
                real_data,isError,hsh,index = utils.check_checksum(data)
                self.logger.info("reciving frame {} current index is {}".format(index,self.index))
                if self.first and (not isError):
                    self.logger.info("first has run")
                    self.index = index
                    self.first = False 
                if isError or (index != self.index):
                    if index != self.index and not isError:
                        # self.logger.info("ACK being sent {}".format(utils.add_index(MyReceiver.ACK_DATA, index,self.logger)))
                        myAck = utils.add_index(MyReceiver.ACK_DATA, index)
                        self.logger.info("ack value being sent from error {}".format(myAck))
                        self.simulator.u_send(myAck)
                    else:
                        # self.logger.info("ACK being sent {}".format(utils.add_index(MyReceiver.NACK_DATA, index,self.logger)))
                        myNACK = utils.add_index(MyReceiver.NACK_DATA,index)
                        self.logger.info("nack value being sent {}".format(myNACK))
                        self.simulator.u_send(myNACK)
                    # else send nack
                    continue
                if self.index == 0:
                    self.logger.info("setting last to true")
                    self.last = True
                self.index -= 1 
                sys.stdout.write(real_data)
                # self.fullData += real_data
                # self.logger.info("ACK being sent {}".format(utils.add_index(MyReceiver.ACK_DATA, index,self.logger)))
                myAck = utils.add_index(MyReceiver.ACK_DATA, index)
                self.logger.info("ACK value being sent {}".format(myAck))
                self.simulator.u_send(myAck)  # send ACK
            except socket.timeout:
                pass
        

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = MyReceiver()
    rcvr.receive()
