import threading
import time

def loop(x):
    for i in range(1,x+1):
        time.sleep(1)
        print(i)

threading.Thread(target=loop(10)).start()