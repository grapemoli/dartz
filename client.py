########################################
# Project 3: Client.py
# Grace Nguyen & Mason Lane
########################################
from coapthon.client.helperclient import HelperClient
import threading


host = "192.168.1.210"                          # Raspberry Pi's IP.
port = 1234                                     # Configure as needed.
pathGame = "game"                               # Configure as needed.`
pathScore = "score"
pathDistance = "distance"
client = HelperClient(server=(host, port))
distance = "1"                                  # Distance in meters.

# Threading functions.
def getDistance():
    global distance
    currentDistance = client.get(pathDistance).payload

    print(currentDistance)

    if float(currentDistance) >= float(distance):
        return True
    else:
        print(f'Current Distance: {currentDistance}')



# Driver code.
def main():
    game = input("Start Game? (Y/N) ")

    while game.lower() != 'n':

        if game.lower() == 'y':
            client.delete(pathGame)

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
            currentDistance = client.get(pathDistance).payload

            while float(currentDistance) < float(distance):
                # Deadlock until the user is far enough away.
                print (f'Distance: {currentDistance} m')
                currentDistance = client.get(pathDistance).payload

            print('\nStart--')
            client.put(pathGame, distance)   # Starts game.

            score = client.get(pathScore).payload
            print (f'Score: {score}')
        else:
            print ('Invalid input, try again.')

        game = input ('Play again? (Y/N) ')


if __name__ == '__main__':
    main()

