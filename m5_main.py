from m5stack import *
from m5stack_ui import *
from uiflow import *
from IoTcloud.AWS import AWS
import time
import json


screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0x000000)


profit = None
overall = None


label0 = M5Label('0', x=144, y=54, color=0xffa100, font=FONT_MONT_48, parent=None)
label1 = M5Label('Today:', x=129, y=27, color=0xffb700, font=FONT_MONT_20, parent=None)
Overall = M5Label('Overall:', x=123, y=140, color=0x0093eb, font=FONT_MONT_20, parent=None)
label2 = M5Label('656', x=122, y=162, color=0x0093eb, font=FONT_MONT_42, parent=None)
line0 = M5Line(x1=-1, y1=118, x2=347, y2=119, color=0xf500ff, width=2, parent=None)


# Describe this function...
def set_today():
  global profit, overall
  if profit == '0':
    rgb.setColorAll(0xcc0000)
  else:
    rgb.setColorAll(0x33ff33)


def fun_topic_accept_(topic_data):
  global profit, overall
  profit = (json.loads(topic_data))['today']
  overall = (json.loads(topic_data))['overall']
  label0.set_text(str(profit))
  label2.set_text(str(overall))
  screen.set_screen_brightness(70)
  power.setVibrationIntensity(50)
  rgb.setBrightness(80)
  set_today()
  wait(3)
  power.setVibrationIntensity(0)
  rgb.setBrightness(0)
  wait(30)
  screen.set_screen_brightness(0)
  pass

def buttonB_pressFor():
  global profit, overall
  screen.set_screen_brightness(0)
  pass
btnB.pressFor(0.8, buttonB_pressFor)

def buttonB_wasPressed():
  global profit, overall
  screen.set_screen_brightness(50)
  wait(30)
  screen.set_screen_brightness(0)
  pass
btnB.wasPressed(buttonB_wasPressed)


power.setVibrationEnable(False)
aws = AWS(things_name='cube', host='deleted-ats.iot.eu-central-1.amazonaws.com', port=8883, keepalive=4000, cert_file_path="/flash/res/cert-pem.crt", private_key_path="/flash/res/private-pem.key")
aws.subscribe(str('topic/accept'), fun_topic_accept_)
aws.start()
