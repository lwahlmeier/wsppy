import os, wsp, time, unittest

DIRNAME = os.path.dirname(__file__)

class TestWSPPY(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test1_small_unmasked(self):
    fp = open("{}/wsTest-unmask-small".format(DIRNAME), "rb")
    DATA = fp.read()
    fp.close()
    self.assertTrue(wsp.is_frame_complete(DATA))
    self.assertEqual(2, wsp.find_frame_length(DATA))
    wsf = wsp.WebsocketFrame(DATA)
    self.assertEqual(2, wsf.frame_length())
    wsf = wsp.WebsocketFrame(DATA)
    self.assertEqual(9, wsf.data_length())
    self.assertEqual(b"SmallText", DATA[wsf.frame_length():])
    self.assertTrue(wsf.has_finished())
    self.assertFalse(wsf.has_rsv1())
    self.assertFalse(wsf.has_rsv2())
    self.assertFalse(wsf.has_rsv3())
    self.assertEqual(wsp.OpCode.Text, wsf.opcode())
    
