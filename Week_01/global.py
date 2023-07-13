x = 0

def adjust_x():
    global x
    x = 2
    print("Inside Function:", x)

adjust_x()
print("Outside Function:", x)