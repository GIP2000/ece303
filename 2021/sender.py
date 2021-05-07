# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys
import hashlib


class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
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
    def __init__(self):
        super(MySender, self).__init__()
        self.lastError = False
    
    def send(self, data):
        backwards_range = range(utils.get_frame_size(data))
        backwards_range.reverse()
        self.logger.info(backwards_range)
        data_frames = [utils.add_hash(frame,hashlib.md5(),i) for frame,i in zip(utils.slice_frames(data),backwards_range)]
        self.logger.info("second to last {}".format(data_frames[-2]))
        self.logger.info("last {}".format(data_frames[-1]))

        for frame in data_frames:
            if frame == data_frames[-1]:
                self.logger.info("sending last packet")
            while True:
                try:
                    if self.lastError:
                        self.logger.info("resending {}".format(frame))
                    self.logger.info("sending frame {}".format(frame))
                    self.simulator.u_send(frame)
                    ack = self.simulator.u_receive()
                    break
                except socket.timeout:
                    self.logger.info("um error {}".format(frame))
                    self.lastError = True
                    pass




if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = MySender()
    sndr.send(DATA)
