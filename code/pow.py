import random
import string
import hashlib
import time
import matplotlib.pyplot as plt
import psutil #Used to mesure consumption, my cpu: amd ryzen 5 2600, 6 cores -> 370 watts

watt = 370.0 # It is only right for my cpu -> used to estimate the approximated electricity consumption

## Proof of work inhibit spam and DDos attack, a computer make request on the serveur, we present him a computational problem/challenge to resolve.
## Take significant cpu power to solve the power but a miniscule amount to validate the given answer.

def generateRandomString(size):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for ch in range(size)).encode("utf-8")

default_size = 32   # 32 * 8 = 256 bits (ASCII encoding), contain: the root hash of the merkle tree containing hash of transactions, previous block hash and other block info.
default_challenge = generateRandomString(default_size) # Challenge is the hash for a block in the blockchain which contain a number of transaction. (In fact challenge has all the info of the block exept the nonce
                                                       # If one tried to change a transaction amount by even 0.000001 bitcoin, the resultant hash would be unrecognizable

def generateAttempt(challenge = default_challenge):
    answer = generateRandomString(4) #Proof response of 4 byte (Nonce for bitcoin)
    attempt = challenge + answer
    return attempt,answer

# the lower the target, the smaller is the set of valid hashes,
# and the harder it is to generate one. In practice, this means a hash that starts with a very long string of zeros.
# -> Prove that they have engaged a significal computational effort

## Proof of work was initially created as a proposed solution to the growing problem of spam email.
def solveChallenge(difficulty):
    print("-----START DIFFICULTY: ",difficulty,"-----")
    condition = "".join("0" for zero in range(difficulty))  ## the zero number is the level of difficulty.
    start = time.time()                                     ## to turn the process into "work", the more this value is big the more the desiered answer is small
    solved = False
    count = 0
    while not solved:
        sha256 = hashlib.sha256()
        attempt, answer = generateAttempt(generateRandomString(default_size))
        sha256.update(attempt)
        digest = sha256.hexdigest() #64 digit
        count += 1
        if digest.startswith(condition):
            elapsedTime = (time.time() - start)

            cpu_use = psutil.cpu_percent()/100 # it return the current use of my cpu not only the part used by python so better if only run this python file -> not exact just an approximation
            energyConsumption = watt * cpu_use * elapsedTime   #In joules.
            elapsedTime = "{:.6f}".format(elapsedTime)
            energyConsumption = "{:.6f}".format(energyConsumption)

            print("Solution Found: ", digest)
            print("Elapsed Time: ", elapsedTime)
            print("Challenge: ",default_challenge.decode("utf-8"))
            print("Answer: ", answer.decode("utf-8")) ## The answer sent to the server which is simply verified by computing the hash of challenge+answer
            print("Attempt: ", attempt.decode("utf-8"))
            print("Number of generation: ", count)
            print("Used Energy: ", energyConsumption, "J")
            solved = True
            print("-----END DIFFICULTY: ", difficulty, "-----")
            print(" ")

    return elapsedTime,count,energyConsumption

##  RUN EXAMPLE

#solveChallenge(4)



## ------ Plot and runs ----

times = []
counts = []
energies = []
difficulty = 5 # max difficulty value


difficulties = [i for i in range(1,difficulty+1)]

for i in range(1,difficulty+1):
    timer,count,energie = solveChallenge(i)
    times.append(timer)
    counts.append(count)
    energies.append(energie)


plt.plot(difficulties,times)
plt.xlabel("Level of difficulty")
plt.ylabel("Time in second")
plt.title("Times Evolutions")
plt.show()

plt.plot(difficulties,counts)
plt.xlabel("Level of difficulty")
plt.ylabel("Number of attempt")
plt.title("Evolutions of the numbers of attempt")
plt.show()

plt.plot(difficulties,energies)
plt.xlabel("Level of difficulty")
plt.ylabel("Energie in Joule")
plt.title("Evolutions of the estimated consumption")
plt.show()

print("Times at each difficulty: ",times)
print("Attempt Number at each difficulty: ",counts)
print("Energie at each difficulty: ",energies)



## Proof of work -> add block to blockchain -> need to find a hash lower than a target hash for a block hash.
## The first to find this target hash will be the one who add the block and win coin


