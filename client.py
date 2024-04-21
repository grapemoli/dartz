########################################
# Project 3: Client.py
# Grace Nguyen & Mason Lane
########################################
from coapthon.client.helperclient import HelperClient
import threading
import sys
import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *



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
        self.players = 1
        self.distance = 1
        self.currentPlayer = 1
        self.score = 0

        # Timers for the game state.
        self.startGameCountdownTimer = QTimer ()
        self.startGameCountdownTimer.timeout.connect (self.startGameCountdown_update)
        self.startGameCountdown = 3

        self.inGameCountdownTimer = QTimer ()
        self.inGameCountdownTimer.timeout.connect (self.gameCountdownTimer_update)
        self.inGameCountdown = 15

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
        self.distancePrompt = QLabel (f"<font size='5'>Player {self.currentPlayer},  Line Up To Start</font>")
        self.distancePrompt.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.distanceScreenLayout.addWidget (self.distancePrompt)

        # Show the user's current distance from the CoAP server.
        self.distanceLabel = QLabel (f"<font size='4'>Current Distance: {self.distance} meters</font>")
        self.distanceScreenLayout.addWidget (self.distanceLabel)

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
        self.startGameCountdownLabel = QLabel (f"<font size='7'>🚦 3 🚦</font>")
        self.startGameCountdownLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.countdownScreenLayout.addWidget (self.startGameCountdownLabel)

        self.stack.addWidget (self.countdownScreenWidget)

        # DISPLAY#4: Play / Timer Screen w/ Player# Header.
        self.inGameCountdownWidget = QWidget ()
        self.inGameCountdownLayout = QVBoxLayout ()
        self.inGameCountdownWidget.setLayout (self.inGameCountdownLayout)

        # Some label.
        self.inGameLabel = QLabel (f"<font size='7'>✨Player {self.currentPlayer}, Keep Throwing until Time's Up! ✨</font>")
        self.inGameLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.inGameCountdownLayout.addWidget (self.inGameLabel)

        # Countdown label (dynamic).
        self.inGameCountdownLabel = QLabel (f"<font size='7'>🚦 15 🚦</font>")
        self.inGameCountdownLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.inGameCountdownLayout.addWidget (self.inGameCountdownLabel)

        self.stack.addWidget (self.inGameCountdownWidget)


        # DISPLAY#5: End Game / Next Player Screen.
        self.endGameWidget = QWidget ()
        self.endGameLayout = QVBoxLayout ()
        self.endGameWidget.setLayout (self.endGameLayout)

        # Score label.
        self.scoreLabel = QLabel (f"<font size='6'>Player {self.currentPlayer}'s Score: {self.score}</font>")
        self.scoreLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.endGameLayout.addWidget (self.scoreLabel)

        # Prompt the user to end the game (back to the menu).
        self.endGameButton = QPushButton ("End Game")
        self.endGameButton.clicked.connect (self.endGameButton_clicked)
        self.endGameLayout.addWidget (self.endGameButton)

        self.stack.addWidget (self.endGameWidget)



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
            self.players = 1
            self.currentPlayer = 1
            self.distance = 0.5
            self.startButton.setText ("Start Game")
            self.startButton.setEnabled (True)

        elif index == 1:
            self.distancePrompt.setText (f"<font size='5'>Player {self.currentPlayer},  Line Up To Start</font>")
            self.distanceLabel = QLabel (f"<font size='4'>Current Distance: {self.distance} meters</font>")

        # Hide the back button if it's not the first player.
            if self.currentPlayer != 1:
                self.backButton.hide ()
            else:
                self.backButton.show ()

        elif index == 2:
            # Pre-Game Countdown window. Countdown from 3 seconds down, changing
            # the countdown text while doing so.
            self.startGameCountdown = 3
            self.startGameCountdownLabel.setText  (f"<font size='7'>🚦 {self.startGameCountdown} 🚦</font>")
            self.startGameCountdownTimer.start (1000)
        elif index == 3:
            # In-Game Countdown window. Countdown from 15 seconds down, changing
            # the countdown text while doing so.
            self.inGameLabel.setText (f"<font size='7'>✨Player {self.currentPlayer}, Keep Throwing until Time's Up! ✨</font>")
            self.inGameCountdown = 15
            self.inGameCountdownLabel.setText (f"<font size='7'>🚦 15 🚦</font>")
            self.inGameCountdownTimer.start (1000)
        elif index == 4:
            self.scoreLabel.setText (f"<font size='7'>Player {self.currentPlayer}'s Score: {self.score}</font>")

            if self.currentPlayer == self.players:
                self.endGameButton.setText ('End Game')
            else:
                self.endGameButton.setText (f"Player {self.currentPlayer + 1}'s Turn")

        self.stack.setCurrentIndex (index)


    # Event Handlers / Slots.
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

    def startGameCountdown_update (self):
        # Change the pre-countdown label based on the time remaining.
        self.startGameCountdown = self.startGameCountdown - 1

        if self.startGameCountdown != 0:
            self.startGameCountdownLabel.setText  (f"<font size='7'>🚦 {self.startGameCountdown} 🚦</font>")
        else:
            self.startGameCountdownLabel.setText  (f"<font size='7'>🥳 Start Throwing! 🎯</font>")
            self.startGameCountdownTimer.stop ()
            self.display (3)


    def gameCountdownTimer_update (self):
        self.inGameCountdown = self.inGameCountdown - 1

        if self.inGameCountdown != 0:
            self.inGameCountdownLabel.setText (f"<font size='7'>🚦 {self.inGameCountdown} 🚦</font>")
        else:
            self.inGameCountdownLabel.setText (f"<font size='7'>❌ Time is Up~ ❌</font>")
            self.inGameCountdownTimer.stop ()
            self.display (4)

    def endGameButton_clicked (self):
        # If the current player is the last player, then end the game.
        if self.currentPlayer == self.players:
            self.display (0)
        else:
            self.currentPlayer = self.currentPlayer + 1
            self.display (1)


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

