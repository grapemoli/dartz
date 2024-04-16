########################################
# Project 3: Client.py
# Grace Nguyen & Mason Lane
########################################
from coapthon.client.helperclient import HelperClient


host = "192.168.1.210"                          # Raspberry Pi's IP.
port = 1234                                     # Configure as needed.
pathGame = "game"                               # Configure as needed.`
pathScore = "score"
client = HelperClient(server=(host, port))

# Driver code.
def main():
    game = input("Start Game? (Y/N)")

    while game.lower() != 'n':

        if game.lower() == 'y':
            print('Start--')
            client.delete(pathGame)
            client.put(pathGame, '1')   # Starts game.

            score = client.get(pathScore).payload
            print (f'Score: {score}')
        else:
            print ('Invalid input, try again.')

        game = input ('Play again? (Y/N) ')


if __name__ == '__main__':
    main()

