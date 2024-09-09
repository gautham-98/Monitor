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
            self.string = ["we", "testing", "this", "shit", "now"]
        
        def __call__(self,):
            self.go_through_stuff()
        
        def go_through_stuff(self,):
            sleep(1)
            self.str += (self.string[self.i]+" ")
            self.bool = not(self.bool)
            if self.string[self.i]=="now":
                sleep(1)
                self.i=0
                self.str = ""
            else:
                self.i+=1
                
    test = Test()
    test.instance_name = "test"
    test_1 = Test()
    test_1.instance_name = "test_1"
    while True:
        test()
        test_1()
        
if __name__ == "__main__":
    main()