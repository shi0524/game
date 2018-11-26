# -*- coding: utf-8 –*-


import msgpack
import cPickle as pickle
import settings


def data_encode(data):
    """用 msgpack 对数据进行编码、压缩
       msgpack 不能对集合(set)进行压缩
    """
    s = msgpack.dumps(data)
    if settings.ZIP_COMPRESS_SWITCH and len(s) >= settings.MIN_COMPRESS > 0:
        s = "\x01\x02" + s.encode('zip')
    else:
        s = "\x01\x01" + s
    return s


def data_encode_by_pickle(data, protocol=pickle.HIGHEST_PROTOCOL):
    """用pickle对数据编码、压缩
    """
    s = pickle.dumps(data, protocol=protocol)
    if settings.ZIP_COMPRESS_SWITCH and len(s) >= settings.MIN_COMPRESS > 0:
        s = "\x01" + s.encode('zip')
    return s


def data_decode(data):
    """对数据进行解压
    """
    if not data:
        return data
    protocol = data[:2]
    if protocol == '\x01\x01':
        return msgpack.loads(data[2:], encoding='utf-8')
    elif protocol == '\x01\x02':
        decode_data = data[2:].decode('zip')
        return msgpack.loads(decode_data, encoding='utf-8')
    elif data[0] == '\x01':
        decode_data = data[1:].decode('zip')
        return pickle.loads(decode_data)
    else:
        return pickle.loads(data)


def data_decode_by_pickle(data):
    """用 pickle 对数据解压
    """
    if not data:
        return data
    if data[0] == '\x01':
        decode_data = data[1:].decode("zip")
        return pickle.loads(decode_data)
    else:
        return pickle.loads(data)




