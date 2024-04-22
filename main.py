########################################
# Project 3: Main.py, also the Server for CoAP
# Grace Nguyen & Mason Lane
########################################
from gpiozero import Buzzer, DistanceSensor, RGBLED
import RPi.GPIO as GPIO
import time
import threading
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource



### VARIABLES
# GPIO Pins. Change as needed.
GPIO_FORCE = 21
GPIO_BUZZER = 20
GPIO_US_ECHO = 16
GPIO_US_TRIGGER = 12
GPIO_RED = 26
GPIO_BLUE = 6
GPIO_GREEN = 19

# CoAP Server Variables. Change as needed.
# Change these as needed.
PORT = 1234

# Sensors / Actuators.
buzzer = Buzzer (GPIO_BUZZER)
LED = RGBLED (red=GPIO_RED, green=GPIO_GREEN, blue=GPIO_BLUE)

# Variables for game state.
score = 0                       # Resets every game.
start_time = time.time ()       # Set before every game.
TIME = 15  
distance = 1                 

# Thread Events.
TimeUpEvent = threading.Event ()
SongEndEvent = threading.Event ()



### THREAD FUNCTIONS (these functions only run in seperate threads)
# Timer that returns true when passed-args seconds has elapsed.
# Note, it is up to the client to update the start time outside of this function.
def timer (t):
    global start_time
    global TIME
    
    while True:
        now = time.time ()

        #print( f'Time Left: {TIME - (now - start_time)}')   
                        
        if (now - start_time) >= t:
            TimeUpEvent.set ()
            break
            

# Threading for playing RGB sequences. Encompanies the Buzzer jingles.
def playBeginRGB ():
    # Red.
    LED.red = 1
    LED.blue = 0
    LED.green = 0
    time.sleep (1)

    # Orange.
    LED.red = 1
    LED.blue = 0
    LED.green = 0.01
    time.sleep (1)
 
    # Yellow.
    LED.red = 1
    LED.blue = 0
    LED.green = 0.1
    time.sleep (1)

    # Green.
    LED.red = 0
    LED.blue = 0
    LED.green = 0.75
    time.sleep (1.1)

    # Off.
    LED.color = (0, 0, 0) 
       
            
def playEndRGB ():
    # White.
    LED.red = 1
    LED.blue = 0.2
    LED.green = 0.2
    time.sleep (0.55)

    # Pink.
    LED.red = 1
    LED.blue = 0.01
    LED.green = 0.01
    time.sleep (0.3)

    # Red.
    LED.red = 1
    LED.blue = 0.1
    LED.green = 0
    time.sleep (0.35)

    # Purple.
    LED.red = 1
    LED.blue = 0.5
    LED.green = 0
    time.sleep (0.6)

    # Blue.
    LED.red = 0.2
    LED.blue = 0.75
    LED.green = 0
    time.sleep (0.6)

    # Blue.
    LED.red = 0
    LED.blue = 1
    LED.green = 0
    time.sleep (1.1)

    # Off.
    LED.color = (0, 0, 0) 

            
                    
# Threading for playing songs with the buzzer.
def buzz (noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2)
    waves = int (duration * noteFreq)
    
    for i in range (waves):
        GPIO.output (GPIO_BUZZER, True)
        time.sleep (halveWaveTime)
        GPIO.output (GPIO_BUZZER, False)
        time.sleep (halveWaveTime)


def playBegin ():
    try:
        GPIO.setmode (GPIO.BCM)
        GPIO.setup (GPIO_BUZZER, GPIO.OUT)
        t = 0
        notes =  [220, 220, 220, 440]  
        duration = [0.9, 0.9, 0.9, 1]
        
        for n in notes: 
            buzz (n, duration[t])
            time.sleep (duration[t] * 0.1)
            t += 1
            
            # The beeps are 3-2-1-go, with the final go beep being
            # when the user can start hitting the board.
            if n == 440:
                SongEndEvent.set ()
    except:
        pass


def playEnd ():
    try:
        GPIO.setmode (GPIO.BCM)
        GPIO.setup (GPIO_BUZZER, GPIO.OUT)
        t = 0
        notes =  [880, 698.5, 523.3, 880, 659.3, 784]    # Super Mario World Ending
        duration = [0.5, 0.25, 0.25, 0.5, 0.5, 1]
        
        for n in notes: 
            buzz (n, duration[t])
            time.sleep (duration[t] * 0.1)
            t += 1
    finally:
        SongEndEvent.set ()

    
    
### FUNCTIONS
# Read the distance sensor, sending the distance read. 
def distanceSensor ():
    global GPIO_US_ECHO
    global GPIO_US_TRIGGER
    ultrasonic = DistanceSensor (echo=GPIO_US_ECHO, trigger=GPIO_US_TRIGGER, max_distance=4)
    
    return ultrasonic.distance


# Digital reading of the Force Sensor (on/off).
def forceSensor ():
    global score
    global TIME
    
    # Setup Variables for the Force Sensor.
    GPIO.setmode (GPIO.BCM)
    GPIO.setup (GPIO_FORCE, GPIO.IN)
    prev_input = 0                  # Resets every game.
    
    try:
        print( f'~Game Started~')   
       
       # Keep reading the sensor until TimeThread signals that the time is up.
        while not TimeUpEvent.is_set ():
            input = GPIO.input (GPIO_FORCE)
    
            if ((not prev_input) and input):
                score = score + 1
                print( f'Hit! New Score: {score}')
                        
                        
            prev_input = input
                    
            # The force sensor is put to sleep ONLY if the object thrown at
            # it will have prolonged contact with it (without sleeping, the force sensor
            # would register mulitple touches per touch). 
            # Else, if the force sensor does not have prolonged contact with the thrown 
            # object, and the object thrown may have lesser force, do not time.sleep.
            #time.sleep (0.01)      
            
        print( f'~Time Up!~')
    except KeyboardInterrupt:
        pass



### COAP SERVER.
class ScoreResource (Resource):
    def __init__ (self, name='ScoreResource', coap_server=None):
        super (ScoreResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload =  'score/'
        
        
    def render_GET (self, request):
        # Return the score.
        global score
        self.payload = f'{score}'
        return self    
        
        
    def render_DELETE (self, request):
        # Resets the score to 0.
        global score
        score = 0
        self.payload = 0            
        return self


class DistanceResource (Resource):
    def __init__ (self, name='DistanceResource', coap_server=None):
        super (DistanceResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = '0'          # A reading from the distance sensor.
    
    
    def render_GET (self, request):
        # Returns one distance sensor reading
        reading = distanceSensor ()
        self.payload = str (reading)
        
        # The user uses this when the game starts, so we adjust the RGB LED based on
        # the distance the reading is from the throwing distance.
        gb_value = 0.2
        
        # We change the green-blue value of the RGB based on the reading-distance away.
        # The closer the reading is to the throwing distance, the closer the gb_value approaches 0.
        
        # The user is not far enough...
        if reading < distance:
            # We scale RGB light based on the reading-distance away.
            gb_value = (distance - reading) / 4 * 0.2
        
        # The user is too far...
        elif (reading - distance) > 0.1:             # 0.1 meter leeway.
            gb_value = ((reading - distance) / 4) * 0.2
        
        # User is at the perfect distance away.
        else:
            gb_value = 0
    
        LED.red = 1
        LED.blue = gb_value
        LED.green = gb_value
                       
        return self    
        
        
    def render_PUT (self, request):
        # Sets distance to throw.
        global distance
        distance = float (request.payload)
        return self



class GameResource (Resource):
    def __init__ (self, name='GameResource', coap_server=None):
        super (GameResource, self).__init__ (name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = '0'          # Distance configured by the user for the game. 0 if the game is not started.
        
        
    def render_GET (self, request):
        return self   
        
        
    def render_PUT (self, request):
        # Sets the distance to whatever the payload is, with 0 being to not start the game, and
        # greater values being the distance to throw at.
        # This PUT request is made to start the game, so the payload should be greater than 0.
        self.payload = request.payload
        
        if (self.payload != '0'):
            # Play beginning countdown.
            RGBThread = threading.Thread (target=playBeginRGB)
            RGBThread.start ()
            
            PlayBeginThread = threading.Thread (target=playBegin)
            PlayBeginThread.start ()
            SongEndEvent.wait (timeout=5)
            
            if SongEndEvent.is_set ():
            
                # Create thread for timer, and start game.
                global start_time
                start_time = time.time ()
                TimerThread = threading.Thread (target=timer, args= (TIME, ))
                TimerThread.start ()
                forceSensor ()
                
                if TimeUpEvent.is_set ():
                    # Create a thread for the buzzer to play the ending song, so that
                    # we can send the payload as the song plays.
                    RGBThread = threading.Thread (target=playEndRGB)
                    BuzzerPlayThread = threading.Thread (target=playEnd)
                    RGBThread.start ()
                    BuzzerPlayThread.start ()
                    self.payload == '0'
                              
        return self
        
        
    def render_DELETE (self, request):
        # Turns off game, resetting variables.
        global TimeUpEvent
        TimeUpEvent.clear ()
        TimeUpEvent = threading.Event ()
        global score
        score = 0
        global prev_input
        prev_input = 0
        self.payload =  '0' 
        
        # When it comes to clearing the Buzzer/Song event, it is wholly possible
        # that that thread is still playing a song while this request is called;
        # therefore, we wait for the event to be set before clearing the event.
        # Since songs are no more than 5 seconds, we set the timeout to 5.
        global SongEndEvent
        SongEndEvent.wait (timeout=2)
        SongEndEvent.clear ()
        SongEndEvent = threading.Event ()
        
        # Turn off the lights.
        LED.red = 0
        LED.blue = 0
        LED.green = 0
        return self
                


class CoAPServer (CoAP):
    def __init__ (self, host, port):
        CoAP.__init__ (self, (host, port))
        self.add_resource ('score/', ScoreResource ())
        self.add_resource ('game/', GameResource ())
        self.add_resource ('distance/', DistanceResource ())



### DRIVER CODE.
def main ():
    server = CoAPServer ('0.0.0.0', PORT)
        
    try:
        server.listen (10)
    except KeyboardInterrupt:
        print ('Server Shutdown')
        server.close()
        print ('Exiting...')
    finally:
        GPIO.cleanup ()
        

### GUARD.
if __name__ == '__main__':
    print ('++ Server Up ++')
    main ()
