from Button import Button
from SecurityMeansController import SecurityMeansController
from Sensors import DigitalSensor
from StopWatch import Stopwatch
from Buzzer import PassiveBuzzer
from Lights import Light
from Motors import Servo
from Displays import LCDDisplay


ROW_PINS = [26, 22, 21, 20]
COL_PINS = [19, 18, 17, 16]
PIR_PIN = 27
BUZZER_PIN = 28
YELLOW_LED_PIN = 2
GREEN_LED_PIN = 3
RED_LED_PIN = 4
BLUE_LED_PIN = 5
SERVO_PIN = 10
CLOSE_BUTTON_PIN = 6
SENSOR_PIN = 27
TIME_TO_LOGIN = 15
TIME_CLOSE_DOOR = 10


class AlarmController:
    def __init__(self):
        self.start_system = False
        self.active_alarm = False
        self.opened_door = False
        self.user_authenticated_name = None
        self.stop_watch = Stopwatch()
        self.buzzer = PassiveBuzzer(BUZZER_PIN)
        self.yellow_led = Light(pin=YELLOW_LED_PIN, name="yellow led")
        self.green_led = Light(pin=GREEN_LED_PIN, name="green led")
        self.red_led = Light(pin=RED_LED_PIN, name="green led")
        self.blue_led = Light(pin=BLUE_LED_PIN, name="green led")
        self.servo = Servo(pin=SERVO_PIN)
        self.close_button = Button(pin=CLOSE_BUTTON_PIN, name="CLOSE", lowActive=True)
        self.lcd = LCDDisplay(sda=0, scl=1)
        self.keypad = SecurityMeansController(row_pins=ROW_PINS, col_pins=COL_PINS)
    
    def open_door(self):
        self.servo.setAngle(0)
        self.opened_door = True
        self.yellow_led.off()
        self.blue_led.on()
        self.lcd.clear()
        self.lcd.showText(f"Hi {self.user_authenticated_name}, close the door")
    
    def close_door(self):
        self.servo.setAngle(90)
        self.opened_door = False
        self.user_authenticated_name = None

    def verify_movement(self):
        if not self.start_system:
            if self.pir_motion.tripped():
                self.start_system = True
                self.stop_watch.start()
                self.green_led.off()
                self.yellow_led.on()
                self.lcd.clear()
                self.lcd.showText("Identify yourself")
    
    def activate_alarm(self):
        if not self.active_alarm:
            self.yellow_led.off()
            self.blue_led.off()
            self.red_led.on()
            self.active_alarm = True
            if not self.opened_door:
                self.lcd.clear()
                self.lcd.showText("Unauthorized")
                self.buzzer.setVolume(10)
                self.buzzer.play(tone=100)
            else:
                self.buzzer.setVolume(3)
                self.buzzer.play(tone=500)
        else:
            if self.opened_door:
                if self.close_button.isPressed():
                    self.initial_config()
            else:
                self.keypad.scan_key_pad()
                if not self.keypad.password_encode:
                    self.lcd.clear(line=1)    
                self.lcd.showText(self.keypad.password_encode, row=1)
                self.user_authenticated_name = self.keypad.user_authenticated()
                if self.user_authenticated_name:
                    self.keypad.clear()
                    self.initial_config()
    
    def authentication_validation(self):
        if self.stop_watch.is_less_than(TIME_TO_LOGIN):
            self.keypad.scan_key_pad()
            if not self.keypad.password_encode:
                self.lcd.clear(line=1)    
            self.lcd.showText(self.keypad.password_encode, row=1)
            self.user_authenticated_name = self.keypad.user_authenticated()
            if self.user_authenticated_name:
                self.keypad.clear()
                self.stop_watch.reset()
                self.stop_watch.start()
        else:
            self.activate_alarm()
    
    def initial_config(self):
        self.pir_motion = DigitalSensor(pin=SENSOR_PIN , name='pir-motion-sensor', lowActive = False)
        self.close_door()
        self.buzzer.stop()
        self.user_authenticated_name = None
        self.start_system = False
        self.yellow_led.off()
        self.green_led.on()
        self.red_led.off()
        self.blue_led.off()
        self.lcd.clear()
        self.lcd.showText("Door locked")
        self.stop_watch.reset()
    
    def create_users(self):
        self.keypad.create_user_with_password("A111111","Leidy")
        self.keypad.create_user_with_password("A121212","Mauricio")
        self.keypad.create_user_with_password("A131313","Isabela")
        self.keypad.create_user_with_password("A141414","Eshwar")
        self.keypad.create_user_with_password("A151515","Martin")

    def run(self):
        self.create_users()
        self.initial_config()
        while True:
            self.verify_movement()
            if self.start_system:
                if not self.user_authenticated_name:
                    self.authentication_validation()
                else:
                    if not self.opened_door:
                        self.open_door()
                    else:                        
                        if self.stop_watch.is_less_than(TIME_CLOSE_DOOR):
                            if self.close_button.isPressed():
                                self.initial_config()
                        else:
                            self.activate_alarm()


    

alarma = AlarmController()
alarma.run()

