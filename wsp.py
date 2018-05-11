import struct
import random
import base64
import hashlib
from enum import Enum

class OpCode(Enum):
  Continuation = 0
  Text = 1
  Binary = 2
  Close = 8
  Ping = 9
  Pong = 10 

WS_MAGIC_UUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" 
WS_OPCODE_MASK = 0xf
WS_SMALL_LENGTH_MASK = 0x7f
WS_SHORT_SIZE = 126
WS_LONG_SIZE = 127
WS_SHORT_LENGTH = 2
WS_LONG_LENGTH = 8
WS_MASK_SIZE = 4
WS_MIN_FRAME_SIZE = 2
WS_MAX_FRAME_SIZE = 14
WS_DEFAULT_SECRET_KEY_SIZE = 20

def make_secret_key(size:int=WS_DEFAULT_SECRET_KEY_SIZE) -> str:
  ba = bytearray(random.getrandbits(8) for _ in xrange(size))
  return base64.b64encode(ba)

def make_key_response(key: str) -> str:
  return base64.b64encode(hashlib.sha1(bytes(key+WS_MAGIC_UUID)).digest())

def validate_key_response(key: str, response: str) -> bool:
  return make_key_response(key) == response

def has_mask(buf: bytes) -> bool:
  return buf[1] >> 7 == 1

def find_frame_length(buf: bytes) -> int:
  bl = len(buf)
  if bl < WS_MIN_FRAME_SIZE:
    return -1
  sl = (buf[1] & WS_SMALL_LENGTH_MASK)
  mask = 0
  if has_mask(buf):
    mask = 4
  if sl < 126:
    return WS_MIN_FRAME_SIZE + mask 
  elif sl == 126:
    return WS_SHORT_LENGTH + WS_MIN_FRAME_SIZE + mask
  elif sl == 127:
    return WS_LONG_LENGTH + WS_MIN_FRAME_SIZE + mask

def is_frame_complete(buf: bytes) -> bool:
  return find_frame_length(buf) <= len(buf)


def mask_data(buf: bytes, mask: int) -> bytes:
  if mask == 0:
    return bytes(buf)
  else:
    masked = bytearray()
    maskb = struct.pack("!I", mask)
    for i in range(len(buf)):
      masked.append(buf[i]^maskb[i%WS_MASK_SIZE]);
    return bytes(masked);

def unmask_data(buf: bytes, mask: int) -> bytes:
  return mask_data(buf, mask)


  
  

class WebsocketFrame():

  def __init__(self, buf):
    if not is_frame_complete(buf):
      raise Exception("invalid websocket frame")
    l = find_frame_length(buf)
    self.__buf = buf[0:l]

  def has_finished(self) -> bool:
    return ((self.__buf[0]) >> 7) == 1

  def has_rsv1(self) -> bool:
    return ((self.__buf[0] >> 6) &0x1) == 1

  def has_rsv2(self) -> bool:
    return ((self.__buf[0] >> 5) &0x1) == 1

  def has_rsv3(self) -> bool:
    return ((self.__buf[0] >> 4) &0x1) == 1

  def opcode(self) -> OpCode:
    v = self.__buf[0] & WS_OPCODE_MASK
    for name, member in OpCode.__members__.items():
      if member.value == v:
        return member

  def has_mask(self) -> bool:
    return self.__buf[1] >> 7 == 1

  def mask_value(self) -> int:
    if(self.has_mask()):
      pos = ws_frame_length(self.__buf)-WS_MASK_SIZE
      return struct.unpack("!I",self.__buf[pos:pos+4])[0]
    return 0;

  def mask_bytes(self) -> bytes:
    if(self.has_mask()):
      pos = ws_frame_length(self.__buf)-WS_MASK_SIZE
      return bytes(self.__buf[pos:pos+4])
    return bytes(4);

  def mask_data(self, data: bytes)-> bytes:
    return self.unmask_data(data)

  def unmask_data(self, data: bytes)-> bytes:
    if len(data) == self.data_length():
      return mask_data(data, self.get_mask_value())
    raise Exception("Not correct dataset!")

  def data_length(self) -> int:
    sl = (self.__buf[1] & WS_SMALL_LENGTH_MASK)
    if sl < 126:
      return sl
    elif sl == 126:
      return struct.unpack("!H",self.__buf[2:4])[0]
    elif sl == 127:
      return struct.unpack("!Q",self.__buf[2:10])[0]
    return -1
  
  def frame_length(self) -> int:
    return len(self.__buf)

  def raw_frame(self):
   return self.__buf
    
def make_ws_frame(size: int, opcode: OpCode, masked:bool, finished:bool=True, mask:int=random.random()) -> WebsocketFrame:
  buf = bytearray(2)
  buf[0] = 0
  buf[1] = 0
  buf[0] |= opcode.value
  if finished:
    buf[0] |= 1<<7
  if masked:
    buf[1] |= 1<<7
  if size < 126:
    buf[1] |= size
  elif size < 2**16:
    buf[1] |= 126
    sb = bytes(struct.pack("!H", size))
    buf.extend(sb)
  else:
    buf[1] |= 127
    sb = bytes(struct.pack("!Q", size))
    buf.extend(sb)
  if masked:
    sb = bytes("!I", mask)
    buf.extend(sb)
  return WebsocketFrame(bytes(buf))

