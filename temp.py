import random as rand 

pw = rand.randint(0, 99999)
num = 0

while True:
    attempt = rand.randint(0, 99999)
    
    if attempt == pw:
        print("matched")
        print(attempt)
        print(num)
        break
    if num == 1000000:
        print("Attempt timeout")
        break
    
    else:
        num = num + 1