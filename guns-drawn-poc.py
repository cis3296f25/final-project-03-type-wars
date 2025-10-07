import time

word = ""
letter = ''

word_to_guess = "happy"


print("Welcome to Guns Drawn (Proof of Concept)")
print("The rules are as follows. Write down the given word, letter by letter.")

str = input("Would you like to play? (y or n) ")

if(str == 'y'):
    print("Good! Ready yourself.")

print("The first word is...")
print("happy")
print("GUNS DRAWN!")

start = time.time()

for i in word_to_guess:
    input(" ")

end = time.time()
length = end - start
length = round(length, 2)

print("It took you", length, "seconds to type! Nice try!")


# def countdown():

#     countdown = 5

#     while(countdown != 0):
#         print(countdown)
#         time.delay(1)
#         countdown = countdown - 1




