from time import sleep
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from monitor.monitor import monitor

def main():
    @monitor
    class Test:
        def __init__(self,):
            self.i = 0
            self.bool = True
            self.str = ""
        
        def __call__(self, ):
            self.go_through_stuff()
        
        def go_through_stuff(self,):
            string = ["we", "testing", "this", "shit", "now"]
            i=0
            while True:
                sleep(1)
                self.str += (string[i]+" ")
                self.i += 1
                self.bool = not(self.bool)
                
                if string[i]=="now":
                    sleep(1)
                    i=0
                    self.str = ""
                else:
                    i+=1
    test = Test()
    test()

if __name__ == "__main__":
    main()