# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys
import hashlib

# socket.setdefaulttimeout(0.5)


class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=.01, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()
        

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class MySender(Sender):
    ACK_DATA = bytearray([1,1,1,1,1,1,1,1])
    NACK_DATA = bytearray([0,0,0,0,0,0,0,0])
    def __init__(self):
        super(MySender, self).__init__()
    
    def send(self, data):
        data_frames = [utils.add_hash(frame,i) for frame,i in zip(utils.slice_frames(data),reversed(range(utils.get_frame_size(data))))]
        for frame,i in zip(data_frames,reversed(range(len(data_frames)))):
            while True:
                try:
                    self.logger.info("sent frame {}".format(i))
                    self.simulator.u_send(frame)
                    ack = self.simulator.u_receive() # if nack, send again
                    real_ack, index = utils.get_ack_and_index(ack, self.logger)
                    ack_sum_val = sum(list(real_ack))
                    self.logger.info("ack received ACK is {} and type is {} in list format {} sum format {} and index is {}".format(real_ack,type(real_ack),list(real_ack),ack_sum_val,index))
                    
                    if ack_sum_val == 8 and index == i:
                        self.logger.info("ACK RECEIVED")
                        break
                    else:
                        self.logger.info("NACK RECEIVED")
                        continue
                    # break
                except socket.timeout:
                    self.logger.info("socket timeout")
                    pass




if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = MySender()
    sndr.send(DATA)
