import time

from modules import cbpi
from modules.core.props import Property
from modules.core.hardware import ActorBase
from modules.core.controller import KettleController

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    
except Exception as e:
    print e
    pass


@cbpi.controller
class InvertLogic(KettleController):


    TempDiff = Property.Number("Degrees from target to start Reduction", True, 2)
    PowDiff = Property.Number("Percent of power deduction", True, 50)
    RampUp = Property.Number("Ramp up time", True, 2)

    def stop(self):
        
        super(KettleController, self).stop()
        self.heater_off()


    def run(self):
        x=InvertPWM()

        if self.TempDiff is None:
            self.TempDiff = 2
        if self.PowDiff is None:
            self.PowDiff = 50
        
        while self.is_running():
         
            if self.get_temp() >= self.get_target_temp():
                self.heater_off()
            elif self.get_temp() < self.get_target_temp()-int(self.TempDiff):
                self.heater_on(int(100-x.power))
            else:
                self.heater_on(int(100-(x.power + ((100-x.power) * int(self.PowDiff)/100))))
            self.sleep(1)
            self.heater_off()



@cbpi.actor       
class InvertPWM(ActorBase):

    gpio = Property.Select("GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
    frequency = Property.Number("Cycles Per Second", configurable=True)
    
    power = 0
    p = None
    stopped = True
    
    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 1)

    def on(self, power):
        self.stopped = False
        if self.p is None:
            if self.frequency is None:
                self.frequency = 50
            self.p = GPIO.PWM(int(self.gpio), int(self.frequency))
            self.p.start(int(InvertPWM.power))
        if power is not None:
            self.p.ChangeDutyCycle(int(100-power))
        else:
            self.p.ChangeDutyCycle(int(InvertPWM.power))

    def get_power():
        return 100-InvertPWM.power
            
    
    def set_power(self, power):
        if power is not None:
            InvertPWM.power = (100 - power)
        if self.stopped is False:
            self.p.ChangeDutyCycle(int(InvertPWM.power))

    def off(self):
        self.stopped = True
        self.p.ChangeDutyCycle(100)
