########################################
# Project 3: Client.py
# Grace Nguyen & Mason Lane
########################################
from coapthon.client.helperclient import HelperClient
import threading
import sys
from PyQt6.QtWidgets import *



####################################
# Global variables.
####################################
host = "192.168.1.210"                          # Raspberry Pi's IP, configure as needed.
port = 1234                                     # Configure as needed.
pathGame = "game"
pathScore = "score"
pathDistance = "distance"
client = HelperClient (server= (host, port))
distance = "1"                                  # Throwing distance in meters, configured by players.



####################################
# Threading functions.
####################################
def getDistance ():
    global distance
    currentDistance = client.get(pathDistance).payload

    print(currentDistance)

    if float(currentDistance) >= float(distance):
        return True
    else:
        print(f'Current Distance: {currentDistance}')



####################################
# Class: Client.
# The GUI.
####################################
class Client (QMainWindow):
    print ("hello world")



####################################
# Function: cli
# The CLI showing of the game interface for the user.
####################################
def cli ():
    game = input("Start Game? (Y/N) ")

    while game.lower() != 'n':

        if game.lower() == 'y':
            client.delete (pathGame)

            # Get distance to throw at from 0.5 meters to 4 meters.
            global distance
            distance = input("Throwing distance in meters: ")
            distance = float(distance)

            while 0 >= distance > 4:
                # Deadlock until the user inputs a valid distance.
                distance = input("Range must be between 0-4 meters. \nThrowing distance in meters: ")
                distance = float(distance)

            # Check that the user is far-enough away.
            distance = str(distance)
            client.put(pathDistance, distance)
            currentDistance = client.get(pathDistance).payload
            count = 0

            # Deadlocks until the user is a good-enough distance away.
            # The user must be at least the throwing distance away, and must be within 0.1m of it.
            while count < 3:
                print (f'Distance: {currentDistance} m')
                currentDistance = client.get(pathDistance).payload

                if float (distance) < float (currentDistance) <= float (distance) + 1:
                    count += 1
                else:
                    count = 0


            print('\nStart--')
            client.put(pathGame, distance)   # Starts game.

            score = client.get(pathScore).payload
            print (f'Score: {score}')
        else:
            print ('Invalid input, try again.')

        game = input ('Play again? (Y/N) ')



####################################
# Driver code.
####################################
def main ():
    app = QApplication (sys.argv)

    window = Client ()
    window.start ()
    window.show ()

    sys.exit (app.exec ())

if __name__ == '__main__':
    cli ()

