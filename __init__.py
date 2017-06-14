import time

from modules import cbpi
from modules.core.props import Property
from modules.core.hardware import ActorBase

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print e
    pass

@cbpi.actor       
class InvertPWM(ActorBase):

    gpio = Property.Select("GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
    duty_cylce = Property.Number("Frequency", configurable=True)

    power = 0
    p = None
    stopped = True

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 1)

    def on(self, power=None):
        self.stopped = False
        if self.p is None:
            if self.duty_cylce is None:
                self.duty_cylce = 60
            self.p = GPIO.PWM(int(self.gpio), int(self.duty_cylce))
            self.p.start(int(self.power))
        self.p.ChangeDutyCycle(int(self.power))

    def set_power(self, power):
        if power is not None:
            self.power = (100-power)
        if self.stopped is False:
            self.p.ChangeDutyCycle(int(self.power))

    def off(self):
        self.stopped = True
        self.p.ChangeDutyCycle(100)
