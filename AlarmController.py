from Button import Button
from SecurityMeansController import SecurityMeansController
from Sensors import DigitalSensor
from StopWatch import Stopwatch
from Buzzer import PassiveBuzzer
from Lights import Light
from Motors import Servo
from Displays import LCDDisplay
from StateModel import StateModel



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
TIME_SLEEP = 8


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
        self._model = StateModel(8, self, debug=True)

        self._model.addCustomEvent("pir_press")
        self._model.addCustomEvent("correct_password")
        self._model.addCustomEvent("incorrect_password")
        self._model.addCustomEvent("deactivate_incorrect_password")
        self._model.addCustomEvent("close_door")
        self._model.addCustomEvent("no_close_door")
        self._model.addCustomEvent("close_door_after_alarm")
        self._model.addCustomEvent("time_sleep")

        self._model.addTransition(0, ["pir_press"], 1)
        self._model.addTransition(1, ["correct_password"], 2)
        self._model.addTransition(1, ["incorrect_password"], 3)
        self._model.addTransition(3, ["deactivate_incorrect_password"], 0)
        self._model.addTransition(2, ["close_door"], 5)
        self._model.addTransition(2, ["no_close_door"], 4)
        self._model.addTransition(4, ["close_door_after_alarm"], 5)
        self._model.addTransition(5, ["time_sleep"], 0)

        self.keypad.create_user_with_password("A111111","Leidy")
        self.keypad.create_user_with_password("A121212","Mauricio")
        self.keypad.create_user_with_password("A131313","Isabela")
        self.keypad.create_user_with_password("A141414","Eshwar")
        self.keypad.create_user_with_password("A151515","Martin")

        self.lcd.showText("Door locked")
    

    def verify_movement(self):
        if not self.start_system:
            if self.pir_motion.tripped():
                self._model.gotoState(1)
    
    def close_door(self):
        self.servo.setAngle(90)
        self.opened_door = False
        self.user_authenticated_name = None
    
    def authentication_validation(self):
        self.keypad.scan_key_pad()
        if not self.keypad.password_encode:
            self.lcd.clear(line=1)
        self.lcd.showText(self.keypad.password_encode, row=1)
        self.user_authenticated_name = self.keypad.user_authenticated()
        if self.user_authenticated_name:
            return True
    

    def stateEntered(self, state):
        """
        stateEntered - is the handler for performing entry actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        """

        if state == 0:
            self.pir_motion = DigitalSensor(pin=SENSOR_PIN , name='pir-motion-sensor', lowActive = False)
            self.close_door()
            self.buzzer.stop()
            self.user_authenticated_name = None
            self.start_system = False
            self.yellow_led.off()
            self.green_led.on()
            self.red_led.off()
            self.blue_led.off()
            self.stop_watch.reset()
            self.time_served = False
        
        if state == 1:
            self.lcd.clear()
            self.lcd.showText("Identify yourself")
            self.start_system = True
            self.stop_watch.start()
            self.green_led.off()
            self.yellow_led.on()
        
        if state == 2:
            self.servo.setAngle(0)
            self.lcd.clear()
            self.lcd.showText(f"Hi {self.user_authenticated_name}, close the door")
            self.blue_led.on()
            self.stop_watch.start()
        
        if state == 3:
            self.buzzer.setVolume(10)
            self.buzzer.play(tone=100)
            self.red_led.on()
        
        if state == 4:
            self.buzzer.setVolume(3)
            self.buzzer.play(tone=500)
        
        if state == 5:
            self.stop_watch.start()
            self.buzzer.stop()
            self.blue_led.off()
            self.green_led.on()
            self.lcd.clear()
            self.lcd.showText("Door locked")
        


    
    def stateLeft(self, state):
        """
        stateLeft - is the handler for performing exit/actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        
        This is just like stateEntered, perform only exit/actions here
        """

        if state == 0:
            self.green_led.off()
        
        elif state == 1:
            self.yellow_led.off()
            self.keypad.clear()
            self.stop_watch.reset()
        
        elif state == 2:
            self.stop_watch.reset()
            self.close_door()
        
        elif state == 3:
            self.buzzer.stop()
            self.keypad.clear()
            self.red_led.off()
            self.lcd.clear()
            self.lcd.showText("Door locked")
    

    def stateDo(self, state):
        """
        stateDo - the method that handles the do/actions for each state
        """
        #Log.d(f'Paso por aqui')
        # Now if you want to do different things for each state that has do actions
        # Start Project
        if state == 0:            
            self.verify_movement()

        elif state == 1:
            if self.stop_watch.is_less_than(TIME_TO_LOGIN):
                if self.authentication_validation():
                    self._model.gotoState(2)
            else:
                self._model.gotoState(3)
        
        elif state == 2:
            if self.stop_watch.is_less_than(TIME_CLOSE_DOOR):
                if self.close_button.isPressed():
                    self._model.gotoState(5)
            else:
                self._model.gotoState(4)
        
        elif state == 3:
            if not self.user_authenticated_name:
                if self.authentication_validation():
                    self._model.gotoState(0)
        
        elif state == 4:
            if self.close_button.isPressed():
                self._model.gotoState(5)
        
        elif state == 5:
            if not self.stop_watch.is_less_than(TIME_SLEEP):
                self._model.gotoState(0)

