import threading
import time

def function1():
  print("Function 1 is running")
  time.sleep(1)

def function2():
  print("Function 2 is running")
  time.sleep(10)

if __name__ == "__main__":
  while True:
    t1 = threading.Thread(target=function1)
    t2 = threading.Thread(target=function2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()