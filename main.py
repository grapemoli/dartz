########################################
# Project 3: Main.py
# Grace Nguyen & Mason Lane
########################################
import RPi.GPIO as GPIO
import time
import threading
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource



### VARIABLES
# GPIO Pins. Change as needed.
GPIO_FORCE = 21

# CoAP Server Variables. Change as needed.
# Change these as needed.
PORT = 1234

# Variables for game state.
score = 0                       # Resets every game.
start_time = time.time ()       # Set before every game.
TIME = 15                   

# Thread Events.
TimeUpEvent = threading.Event ()



### THREAD FUNCTIONS (these functions only run in seperate threads)
# Timer that returns true when pass-args seconds has elapsed.
# Note, it is up to the client to update the start time outside of this function.
def timer (t):
    global start_time
    global TIME
    
    while True:
        now = time.time ()

        print( f'Time Left: {TIME - (now - start_time)}')   
                        
        if (now - start_time) >= t:
            TimeUpEvent.set ()
            break

    
    
### FUNCTIONS
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
    finally:
        GPIO.cleanup ()



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


class GameResource (Resource):
    def __init__ (self, name='GameResource', coap_server=None):
        super (GameResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = '0'     # True if the game is started, False if not started.
        
        
    def render_GET (self, request):
        return self   
        
    def render_PUT (self, request):
        # Sets the game status to whatever the payload is. If True / 
        # game is on, start the force sensor, etc.
        # This PUT request is made to start the game, so the payload should be 1.
        self.payload = request.payload
        
        if (self.payload == '1'):
            
            # Create thread for timer, and start game.
            global start_time
            start_time = time.time ()
            TimerThread = threading.Thread (target=timer, args= (TIME, ))
            TimerThread.start ()
            forceSensor ()
            
            if TimeUpEvent.is_set ():
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
        return self
                


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('score/', ScoreResource ())
        self.add_resource('game/', GameResource ())





### DRIVER CODE.
def main ():
    server = CoAPServer('0.0.0.0', PORT)
        
    try:
        server.listen (10)
    except KeyboardInterrupt:
        print ('Server Shutdown')
        server.close()
        print ('Exiting...')
        

### GUARD.
if __name__ == '__main__':
    print ('++ Server Up ++')
    main ()
