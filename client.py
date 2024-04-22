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
count = 3                                       # The user must be at the throwing distance for 3 readings to start.


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
# Class: Worker
# Used to let the GUI update while a thread runs in the background.
####################################
class Worker (QObject):
    finished = pyqtSignal ()

    def run (self):
        global count

        while count != 0:
            pass

        self.finished.emit ()


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
        self.distance = "1"             # The distance is a string because of CoAP payload.
        self.currentPlayer = 1
        self.playerScores = [0]
        self.score = 0
        self.currentDistance = "-"
        self.count = 3                  # Makes sure the user is at the throwing distance for 3 readings.

        # Thread Events.
        self.GameSetEvent = threading.Event ()

        self.worker = Worker()
        self.thread = QThread()
        self.worker.moveToThread (self.thread)
        self.thread.started.connect (self.worker.run)
        self.worker.finished.connect (self.startGame)
        self.worker.finished.connect (self.thread.quit)

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
        self.distanceLabel = QLabel (f"<font size='4'>Current Distance: - meters</font>")
        self.distanceScreenLayout.addWidget (self.distanceLabel)

        # Generic Back button. Can be applied to any page.
        self.backButton = QPushButton ("Back")
        self.backButton.clicked.connect (self.backButton_clicked)
        self.distanceScreenLayout.addWidget (self.backButton)

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
        self.inGameLabel = QLabel (f"<font size='7'>✨Player {self.currentPlayer} Is Throwing! ✨</font>")
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

        # Winner label.
        self.winnerLabel = QLabel (f"<font size='5'>You won!</font>")
        self.winnerLabel.setAlignment (Qt.AlignmentFlag.AlignCenter)
        self.endGameLayout.addWidget (self.winnerLabel)

        # Prompt the user to end the game (back to the menu).
        self.endGameButton = QPushButton ("End Game")
        self.endGameButton.setCheckable (True)
        self.endGameButton.clicked.connect (self.endGameButton_clicked)
        self.endGameLayout.addWidget (self.endGameButton)

        self.stack.addWidget (self.endGameWidget)

        # Final displays, setting ups.
        self.display (0)


    # Threading Functions.
    def setGame (self):
        global client
        global pathDistance
        global pathGame

        client.delete (pathGame)
        client.put (pathDistance, self.distance)

        self.GameSetEvent.set ()

    def getDistance (self):
        global client
        global pathDistance
        global count

        self.currentDistance = client.get(pathDistance).payload

        # Deadlocks until the user is a good-enough distance away.
        # The user must be at least the throwing distance away, and must be within 0.1m of it.
        while count > 0:
            self.distanceLabel.setText (f"<font size='4'>Current Distance: {self.currentDistance} meters</font>")

            if float (self.distance) < float (self.currentDistance) <= float (self.distance) + 0.1:
                count = count - 1
            else:
                count = 3

            self.currentDistance = client.get (pathDistance).payload


    def game (self):
        global client
        global pathGame
        global pathScore
        global score

        # Start the game by calling on the CoAP server to start the game.
        client.put (pathGame, self.distance)



    # Page / Window Handlers.
    # Also takes care of state that is dependent on the current window.
    def display (self, index):
        # For switching between different UIs with only one window, we simply
        # change to the UI's corresponding index in self.stack.

        # Cleanse certain elements depending on the page we're at.
        if index == 0:
            # Start window.
            self.playerScores = [0]
            self.players = 1
            self.currentPlayer = 1
            self.distance = 0.5
            self.startButton.setText ("Start Game")
            self.startButton.setEnabled (True)

            self.stack.setCurrentIndex (index)

        elif index == 1:
            global count
            count = 3
            self.GameSetEvent.clear ()
            self.currentDistance = "-"
            self.distancePrompt.setText (f"<font size='5'>Player {self.currentPlayer},  Line Up To Start</font>")
            self.distanceLabel.setText (f"<font size='4'>Current Distance: {self.currentDistance} meters</font>")

            # Hide the back button if it's not the first player.
            if self.currentPlayer != 1:
                self.backButton.hide ()
            else:
                self.backButton.show ()

            self.stack.setCurrentIndex (index)

            # Thread to read the user's distance.
            DistanceThread = threading.Thread (target=self.getDistance)
            DistanceThread.start ()

            self.thread.start ()

        elif index == 2:
            # Pre-Game Countdown window. Countdown from 3 seconds down, changing
            # the countdown text while doing so.
            self.startGameCountdown = 3
            self.startGameCountdownLabel.setText  (f"<font size='7'>🥳 Throwing in {self.startGameCountdown} 🎯</font>")
            self.startGameCountdownTimer.start (1000)

            self.stack.setCurrentIndex (index)

        elif index == 3:
            # In-Game Countdown window. Countdown from 15 seconds down, changing
            # the countdown text while doing so.

            self.inGameLabel.setText (f"<font size='7'>✨Player {self.currentPlayer} Is Throwing! ✨</font>")
            self.inGameCountdown = 15
            self.inGameCountdownLabel.setText (f"<font size='7'>🚦 15 🚦</font>")

            self.inGameCountdownTimer.start (1000)

            self.stack.setCurrentIndex (index)

        elif index == 4:
            # Save the score in the playerScores array.
            self.score = client.get (pathScore).payload
            self.playerScores.append( int(self.score))

            self.winnerLabel.setText ('')
            self.endGameButton.setEnabled (True)
            self.GameSetEvent.clear ()
            self.scoreLabel.setText (f"<font size='7'>Player {self.currentPlayer}'s Score: {self.score}</font>")

            if self.currentPlayer == self.players:
                self.endGameButton.setText ('End Game')

                # Print the winner if there are multiple players playing.
                if self.players > 1:
                    winner = self.playerScores.index (max( self.playerScores))
                    self.winnerLabel.setText (f"<font size='5'>Player {winner} Won!</font>")
            else:
                self.endGameButton.setText (f"Player {self.currentPlayer + 1}'s Turn")

            self.stack.setCurrentIndex (index)
        else:
            self.stack.setCurrentIndex (index)


    # Event Handlers / Slots.
    def startButton_clicked (self):
        # We 'turn off' the button, as there is setup to the CoAP server that
        # may cause a lag time.
        self.startButton.setText ("Starting game...")
        self.startButton.setEnabled (False)

        # Set the settings configured by the user.
        self.players = self.numberOfPlayersWidget.value ()
        self.distance = str (self.throwingDistanceWidget.value ())

        # This may take a little time, particularly the former...
        ClientThread = threading.Thread (target=self.setGame)
        ClientThread.start ()

        self.GameSetEvent.wait (timeout=5)

        # Show the next screen, the "Line Up" screen.
        if self.GameSetEvent.is_set():
            self.display (1)


    def backButton_clicked (self):
        self.display (self.stack.currentIndex() - 1)

    def nextButton_clicked (self):
        self.display (self.stack.currentIndex() + 1)

    def startGameCountdown_update (self):
        # Change the pre-countdown label based on the time remaining.
        self.startGameCountdown = self.startGameCountdown - 1
        self.startGameCountdownLabel.setText  (f"<font size='7'>🥳 Throwing in {self.startGameCountdown} 🎯</font>")

        if self.startGameCountdown == 0:
            self.startGameCountdownTimer.stop ()
            time.sleep (1)
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
            # More players to come.
            self.currentPlayer = self.currentPlayer + 1
            self.endGameButton.setEnabled (False)

            # Reset the game state, THEN allow the next player to start
            # playing.
            ResetGameThread = threading.Thread (target=self.setGame)
            ResetGameThread.start ()
            self.GameSetEvent.wait (timeout=5)

            if self.GameSetEvent.is_set ():
                self.display (1)

    def startGame (self):
        # Starting the game consists of (1) changing the display, and (2) calling the
        # CoAP server to start the game.
        self.display (2)

        GameThread = threading.Thread (target=self.game)
        GameThread.start ()



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

                if float (distance) < float (currentDistance) <= float (distance) + 0.1:
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

