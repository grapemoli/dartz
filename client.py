########################################
# Project 3: Client.py
# Grace Nguyen & Mason Lane
########################################
from coapthon.client.helperclient import HelperClient
import threading
import sys
import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt



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

    # Constructor.
    def __init__(self):
        super().__init__()

        self.setWindowTitle ("Dartz")
        self.setMinimumSize (QSize (800, 600))

        # Game State variables.
        self.players = 0
        self.distance = 1
        self.currentPlayer = 0

        # Because we toggle through multiple windows, we use self.stack to hold
        # all the "windows," which will be further managed and toggled by display ().
        self.mainWindow = QWidget ()
        self.stack = QStackedLayout ()
        self.mainWindow.setLayout (self.stack)
        self.setCentralWidget (self.mainWindow)

        # DISPLAY#1: Start Screen.
        self.startScreenWidget = QWidget ()
        self.startScreenLayout = QVBoxLayout ()
        self.startScreenWidget.setLayout (self.startScreenLayout)

        # Title.
        self.title = QLabel ("<font size='6'>Dartz 🎯</font>")
        self.title.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.startScreenLayout.addWidget (self.title)

        # Toggling the game settings: number of players.
        self.numberOfPlayersLayout = QHBoxLayout ()
        self.numberOfPlayersLabel = QLabel ("<font size='4'>Number of Players</font>")
        self.numberOfPlayersWidget = QSpinBox ()
        self.numberOfPlayersWidget.setMinimum (1)
        self.numberOfPlayersLayout.addWidget (self.numberOfPlayersLabel)
        self.numberOfPlayersLayout.addWidget (self.numberOfPlayersWidget)
        self.startScreenLayout.addLayout (self.numberOfPlayersLayout)

        # Toggling the game settings: throwing distance.
        self.throwingDistanceLayout = QHBoxLayout ()
        self.throwingDistanceLabel = QLabel ("<font size='4'>Throwing Distance</font>")
        self.throwingDistanceWidget = QDoubleSpinBox ()
        self.throwingDistanceWidget.setRange (0.5, 4)
        self.throwingDistanceWidget.setSingleStep (0.5)
        self.throwingDistanceWidget.setSuffix (" m")
        self.throwingDistanceLayout.addWidget (self.throwingDistanceLabel)
        self.throwingDistanceLayout.addWidget (self.throwingDistanceWidget)
        self.startScreenLayout.addLayout (self.throwingDistanceLayout)

        # Start game button.
        self.startButton = QPushButton ("Start Game")
        self.startButton.setCheckable (True)
        self.startButton.clicked.connect (self.startButton_clicked)
        self.startScreenLayout.addWidget (self.startButton)

        self.stack.addWidget (self.startScreenWidget)

        # DISPLAY#2: Lining the user to the right distance screen.
        self.distanceScreenWidget = QWidget ()
        self.distanceScreenLayout = QVBoxLayout ()
        self.distanceScreenWidget.setLayout (self.distanceScreenLayout)

        # Prompt the user to line up {x} meters away.
        distancePrompt = QLabel (f"<font size='5'>Line Up To Start</font>")
        distancePrompt.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.distanceScreenLayout.addWidget (distancePrompt)

        # Show the user's current distance from the CoAP server.
        distancePrompt = QLabel (f"<font size='4'>Current Distance: {100} meters</font>")
        self.distanceScreenLayout.addWidget (distancePrompt)

        # Generic Back button. Can be applied to any page.
        self.backButton = QPushButton ("Back")
        self.backButton.clicked.connect (self.backButton_clicked)
        self.distanceScreenLayout.addWidget (self.backButton)

        # TODO remove, this next button is for testing. Can be applied to any page.
        self.nextButton = QPushButton ("Next")
        self.nextButton.clicked.connect (self.nextButton_clicked)
        self.distanceScreenLayout.addWidget (self.nextButton)

        self.stack.addWidget (self.distanceScreenWidget)

        # DISPLAY#3: Countdown Screen.
        self.countdownScreenWidget = QWidget ()
        self.countdownScreenLayout = QVBoxLayout ()
        self.countdownScreenWidget.setLayout (self.countdownScreenLayout)

        # Countdown label (dynamic).
        self.countdownLabel = QLabel (f"<font size='7'>🚦 3 🚦</font>")
        self.countdownLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.countdownScreenLayout.addWidget (self.countdownLabel)

        # Generic Back button. Can be applied to any page.
        self.backButton1 = QPushButton ("Back")
        self.backButton1.clicked.connect (self.backButton_clicked)
        self.countdownScreenLayout.addWidget (self.backButton1)

        # TODO remove, this next button is for testing. Can be applied to any page.
        self.nextButton1 = QPushButton ("Next")
        self.nextButton1.clicked.connect (self.nextButton_clicked)
        self.countdownScreenLayout.addWidget (self.nextButton1)

        self.stack.addWidget (self.countdownScreenWidget)

        # DISPLAY#4: Play / Timer Screen w/ Player# Header.

        # DISPLAY#5: End Game / Next Player Screen.


        # Final displays, setting ups.
        self.display (0)


    # Page / Window Handlers.
    # Also takes care of state that is dependent on the current window.
    def display (self, index):
        # For switching between different UIs with only one window, we simply
        # change to the UI's corresponding index in self.stack.

        # Cleanse certain elements depending on the page we're at.
        if index == 0:
            # Start window.
            self.players = 0
            self.currentPlayer = 0
            self.distance = 0.5
            self.startButton.setText ("Start Game")
            self.startButton.setEnabled (True)
        elif index == 2:
            # Coundown window. Countdown from 3 seconds down, changing
            # the countdown text while doing so.
            self.countdownLabel.setText  (f"<font size='7'>🚦 {3} 🚦</font>")

            time.sleep (1)

            self.countdownLabel.setText  (f"<font size='7'>🚦 {2} 🚦</font>")

            time.sleep (1)

            self.countdownLabel.setText  (f"<font size='7'>🚦 {1} 🚦</font>")

            time.sleep (1)

            self.countdownLabel.setText  (f"<font size='7'>🥳 Start Throwing! 🎯</font>")



        self.stack.setCurrentIndex (index)


    # Event Handlers
    def startButton_clicked (self):
        # We 'turn off' the button, as there is setup to the CoAP server that
        # mayy cause a lag time.
        self.startButton.setText ("Starting game...")
        self.startButton.setEnabled (False)

        # Set the settings configured by the user.
        self.players = self.numberOfPlayersWidget.value ()
        self.distance = self.throwingDistanceWidget.value ()

        # Show the next screen, the "Line Up" screen.
        self.display (1)

    def backButton_clicked (self):
        self.display (self.stack.currentIndex() - 1)

    def nextButton_clicked (self):
        self.display (self.stack.currentIndex() + 1)





####################################
# Function: cli
# The CLI showing of the game interface for the user.
# The CLI version explicitly shows the steps happening in the GUI,
# which gets convoluted with GUI elements.
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
    window.show ()

    sys.exit (app.exec ())

if __name__ == '__main__':
    main ()

