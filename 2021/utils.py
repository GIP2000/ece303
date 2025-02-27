import datetime
import logging
import hashlib
import struct 


class Logger(object):

    def __init__(self, name, debug_level):
        now = datetime.datetime.now()
        logging.basicConfig(filename='{}_{}.log'.format(name, datetime.datetime.strftime(now, "%Y_%m_%dT%H%M%S")),
                            level=debug_level)

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def debug(message):
        logging.debug(message)

def add_index(frame, i,logger=False):
    if logger:
        logger.info("frame {}".format(frame))
    new_frame = frame + struct.pack('>i',i)
    return new_frame


def get_ack_and_index(data, logger):
    l = len(data)
    if l > 12:
        return bytearray([0,0,0,0,0,0,0,0]),0
    # if logger:
    logger.info("data: {}   length: {}".format(data,l))

    real_data = data[0:8]
    index = data[8:l]
    # if logger:
    logger.info("real_data: {} index: {}".format(real_data,index))
    index = struct.unpack('>i',bytes(index))[0]

    return real_data,index

def add_hash(frame,m,i,logger=False):
    """
    takes a frame of size 1008 and adds a hase of size 16
    """
    m.update(frame)
    hsh = m.digest()
    new_frame = frame + struct.pack('>i',i) + hsh
    if(logger):
        real_data,isError,ev_hsh,index = check_checksum(new_frame)
        logger.info("real_data == frame ->{} hsh == ev_hsh ->{} isError->{} real_index == index -> {}".format(real_data == frame, hsh == ev_hsh, isError,index==i))
        # logging.info("hsh ->{} ev_hsh->{}".format(hsh,ev_hsh))
    return new_frame 


def get_frame_size(data_bytes):
    l = len(data_bytes) / 1004
    return l+1 if len(data_bytes) % 1004 else l

def slice_frames(data_bytes):
    """
    Slice input into BUFFER_SIZE frames
    :param data_bytes: input bytes
    :return: list of frames of size BUFFER_SIZE
    """
    frames = list()
    num_bytes = len(data_bytes)
    extra = 1 if num_bytes % 1004 else 0

    for i in xrange(num_bytes / 1004 + extra):
        # split data into 1024 byte frames
        frames.append(
            data_bytes[
                i * 1004:
                i * 1004 + 1004 
            ]
        )
           
    return frames


def get_data_and_hash_and_index(data,logger=False):
    l = len(data)
    hsh = data[l-16:l]
    real_data = data[0:l-16]
    l = len(real_data)
    index = real_data[l-4:l]
    real_data = real_data[0:l-4]
    if logger:
        logger.info(index)
    index = struct.unpack('>i',bytes(index))[0]
    if logger:
        logger.info(index)
    return real_data,hsh,index


def check_checksum(data,logger=False):
    real_data,hsh,index = get_data_and_hash_and_index(data,logger)
    m = hashlib.md5()
    m.update(real_data)
    my_hsh = m.digest()
    return real_data,hsh != my_hsh,hsh,index

