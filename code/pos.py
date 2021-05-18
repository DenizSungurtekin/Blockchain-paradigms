import random
from hashlib import sha256
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


## This code is only to simulate proof of stack consensus between some participant wih coin age selection to better understand this consensus algorithm
## Very simplified version of blockchain representation.


#Global variables

blockchains = []

# The min and max range of participants money
moneyRangeMin = 32   # Validators in a PoS system commit 32 ETH to be in the game (For futur version of ethereum).
moneyRangeMax = 100000
penalityTime = 100000000 #Number of time a participant can't participate if he add a wrong block
disableTime = 50 #Number of iteration a node can't forge after being chosen

class Block:
    def __init__(self, index,validator): #validator is the participant which create the block
        self.index = index
        self.timestamp = str(datetime.now())
        self.numberOfTransaction = random.randint(500,3000) ## Random value for the number and volume of transaction in a block
        self.transactionVolume = random.randint(10000, 50000)
        self.validator = validator
        self.previousHash = sha256("0000000000".encode()).hexdigest() if not blockchains else blockchains[index-1].hashValue # Initial previous hash for the first block in the chain or the hash of the previous hash
        self.rewardFees = int(self.transactionVolume / 100) # Suppose the reward fees is 1 percent of the total transaction volume
        self.hashValue = sha256((str(self.index)+self.timestamp+str(self.previousHash)).encode()).hexdigest() # Here the hash of the block is just taking into account some invariable block attribut and string of previous hash, we are not following the merkle tree structure

class Participant:
    def __init__(self,name,adresse,idNumber):
        self.name = "Participant "+name
        self.adresse = "Adress of Participant "+adresse
        self.idNumber = idNumber
        self.stackedCoin = random.randint(moneyRangeMin,moneyRangeMax)
        self.time = 1
        self.coin_age = self.stackedCoin #Initialize with stackedCoin because time = 1
        self.selected = 0
        self.desactivated = 0 # Variable telling if the participant can be a validator (yes if 0 - no if >0 because he has been chosen too recently)

    def reset(self): # When a participant is chosen, the time is reset
        self.time = 1
        self.coin_age = self.time * self.stackedCoin

    def unable(self):
        self.desactivated = disableTime #Number of iteration a Participant is unable to forge after being chosen

    def timePass(self): # called at each iterration to reduce the time a participant is disable
        if self.desactivated > 0:
            self.desactivated -= 1

    def select(self): #Number of time a participant is selected
        self.selected += 1

    def removeMoney(self,sub): #Remove coins
        self.stackedCoin = self.stackedCoin - sub
        self.coin_age = self.time * self.stackedCoin #refresh coin_age

    def addMoney(self,add): #Add coins
        self.stackedCoin = self.stackedCoin + add
        self.coin_age = self.time * self.stackedCoin #refresh coin_age

    def increaseTime(self):
        self.time += 1
        self.coin_age = self.time * self.stackedCoin # stackedCoin * time, the time he didnt create a block, reset when he is chosen, here the time will be the number of iteration of the coin age selection

    def validateBlock(self): # Create a new block, verify it, add it to the chain to earn reward
        block = Block(len(blockchains),self)
        if self.verifyBlock(block):
            blockchains.append(block)
            self.addMoney(block.rewardFees)

    def putFalifiedBlock(self): # Create a new block but change his hash
        block = Block(len(blockchains), self)
        block.hashValue = sha256("wrongDigest".encode()).hexdigest() #Change the hash -> suppose a participant tried to change a transaction
        blockchains.append(block)

    @staticmethod
    def verifyBlock(block): # Compare block hash value to the computed one
        hash1 = block.hashValue
        hash2 = sha256((str(block.index)+block.timestamp+str(block.previousHash)).encode()).hexdigest()

        if hash1 == hash2:
            return True
        else:
            block.hashValue = hash2 # Put the good hash back
            return False

    def verifyBlocksOnTheChains(self): #function run by others participants which aren't selected to verify the integrity of the blocks (In our case just one other participant not majority voting)
        for block in blockchains:
            if (not self.verifyBlock(block)):
                print("!!!!!!")
                print(block.validator.name," Tried to falsify a block !!!!!")
                participants[block.validator.idNumber].removeMoney(participants[block.validator.idNumber].stackedCoin)
                participants[block.validator.idNumber].desactivated = penalityTime #Has a very long penality / we can even remove him from the list

                # In case we want to remove the falsifier from the participants

                # for participant in participants:
                #     if participant.idNumber > participants[block.validator.idNumber].idNumber:
                #         participant.idNumber -= 1 # Because the lenght of the list change, we need to adjust the id in case someone try to cheat again
                #
                # del participants[block.validator.idNumber]

                print(block.validator.name, " has lost all his stacked coins and his right to participate during a long period")
                print("!!!!!!")


def coinAgeSelection(participants): # Take all the coin_age to sum it and do a weighted selection
    totalCoinAge = sum([participant.coin_age for participant in participants if participant.desactivated == 0])
    probabilities = (participant.coin_age/totalCoinAge for participant in participants if participant.desactivated == 0)
    chosenOne = random.choices([participant for participant in participants if participant.desactivated == 0], weights=probabilities, k=1)[0] #Return a participant depending on a probability given by the coin_age
    chosenOne.reset() #Reset his timer
    chosenOne.unable()
    return chosenOne

def goodrun(iteration): #There is no attempt of modification, we simule a coinAge selection, add a block and verify the chains. We do it "iteration" times.
    for i in range(iteration):
        chosen = coinAgeSelection(participants)
        chosen.select()
        chosenPerson.append(chosen)
        chosen.validateBlock() # The chosen one verify and add the block to the blockchain
        randomParticipant = random.randint(0,len(participants)-1) # Choose a random participant which will verify the blockchain

        while participants[randomParticipant].idNumber == chosen.idNumber: # We dont want the chosen participant to verify the blockchain
            randomParticipant = random.randint(0, len(participants) - 1)

        participants[randomParticipant].verifyBlocksOnTheChains()

        for participant in participants: #Increase timer of other participants
            participant.timePass() # Reduce timer of being disable for each participant having desactivated > 0
            if participant.idNumber != chosen.idNumber:
                participant.increaseTime()


def badrun(): # Simulation of someone trying to modify a block
    chosen = coinAgeSelection(participants)
    chosen.select()
    chosenPerson.append(chosen)
    chosen.putFalifiedBlock() # Here the chosen modify the block and but the wrong hash in the blockchain (As if he modify a transaction)
    randomParticipant = random.randint(0, len(participants) - 1)  # Choose a random participant which will verify the blockchain

    while participants[randomParticipant].idNumber == chosen.idNumber:  # We dont want the chosen participant to verify the blockchain, normally all of the other participant verify the blocks, here one is enought to reduce computation
        randomParticipant = random.randint(0, len(participants) - 1)

    participants[randomParticipant].verifyBlocksOnTheChains() #Another participant verify the hash from blocks in the blockchain. If a wrong block is identified, his validator lose his coins and his right to participate.

    for participant in participants: #Increase timer of other participants
        participant.timePass()  # Reduce timer of being disable for each participant having desactivated > 0
        if participant.idNumber != chosen.idNumber:
            participant.increaseTime()


#Global variables
blockchains = [Block(i,Participant("Genesis","battelle",i-i)) for i in range(4)] # Initial blockchain with genesis blocks -> not mandatory for the simulation

numberOfParticipants = 100 #Number of participant
participants = [Participant(str(i),str(i),i) for i in range(numberOfParticipants)] # Initialize all the participants
chosenPerson = [] # History of the chosen participant


# Main
def main():
    print("-------Start of the Simulation---------")
    print("")
    coinsBefore = [participant.stackedCoin for participant in participants]
    wealthierBefore = participants[np.argmax(np.asarray([participant.stackedCoin for participant in participants]))]
    wealthierBeforeStack = participants[np.argmax(np.asarray([participant.stackedCoin for participant in participants]))].stackedCoin

    goodrun(2000)
    badrun()
    goodrun(2000)

    coinsAfter = [participant.stackedCoin for participant in participants]
    print("")
    print("-----End of the Simulation------")
    print("")

    print("The blockchains is now of size:",len(blockchains),".")
    print("There is",len(participants),"participant(s) with",moneyRangeMin,"to",moneyRangeMax,"coins,")
    wealthier = participants[np.argmax(np.asarray([participant.stackedCoin for participant in participants]))]
    occurences = np.asarray([chosenPerson.count(element) for element in chosenPerson])
    mostChosen = np.argmax(occurences)

    print("Before the run, the wealthier participant was", wealthierBefore.name, "with", wealthierBeforeStack, "stacked coins.")
    print("The wealthier participant is now",wealthier.name,"with",wealthier.stackedCoin,"stacked coins with",chosenPerson.count(wealthier),"participation(s).")
    print("The most chosen participant is",chosenPerson[mostChosen].name,"with",chosenPerson[mostChosen].stackedCoin,"coins and",chosenPerson.count(chosenPerson[mostChosen]),"participation(s).")


    #Plot
    x = [i+1 for i in range(len(participants))]
    selectionNumber = [participant.selected for participant in participants]
    benefice = [x2-x1 if x2-x1 >= 0 else 0 for (x1,x2) in zip(coinsBefore,coinsAfter)] #To remove the negatif value of the falsifier

    plt.title("Selection distribution")
    plt.xlabel("Participants")
    plt.ylabel("Number of selection")
    plt.bar(x, selectionNumber)
    plt.show()

    plt.title("Coins Distribution Before")
    plt.xlabel("Participants")
    plt.ylabel("Coins")
    plt.bar(x, coinsBefore)
    plt.show()

    plt.title("Coins Distribution After")
    plt.xlabel("Participants")
    plt.ylabel("Coins")
    plt.bar(x, coinsAfter)
    plt.show()

    plt.title("Benefice")
    plt.xlabel("Participants")
    plt.ylabel("Coins")
    plt.bar(x, benefice)
    plt.show()


if __name__ == '__main__':
    main()
