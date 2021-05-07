# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
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
    ACK_DATA = bytearray(1)
    def __init__(self):
        super(MyReceiver, self).__init__()
        self.index = 0
        self.first = True
    
    def receive(self):
        #self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                self.logger.info("index = {}".format(self.index))
                if self.index < 0:
                   self.logger.info("Stopping now") 
                   sys.exit()
                   break
                data = self.simulator.u_receive()  # receive data
                self.counter = 0
                real_data,isError,hsh,index = utils.check_checksum(data,self.logger)
                self.logger.info("rcver index = {}".format(index))
                self.logger.info("rcvd frame {}".format(data))
                if self.first and not isError:
                    self.index = index
                    self.first = False 
                if isError or index != self.index:
                    if index != self.index and not isError:
                        self.simulator.u_send(MyReceiver.ACK_DATA)
                    self.logger.info("um error data = {} hash = {} emb_index = {} our index = {}".format(real_data,hsh,index,self.index))
                    continue
                self.index -= 1 
                sys.stdout.write(real_data)
                self.simulator.u_send(MyReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                pass
        

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = MyReceiver()
    rcvr.receive()
