import threading
import time
import weakref
import socket

from rich import inspect

class Monitor:

    """
    A singleton class that creates a single instance per class it tracks.
    """
    
    _instances = {}

    def __new__(cls, monitored_cls, interval, server_addr=("localhost", 8080)):
        """
        instantiate _instance of Class Monitor which tracks a single cls monitored_cls
        """
        if monitored_cls not in cls._instances:
            cls._instances[monitored_cls] = super().__new__(cls)
            _instance = cls._instances[monitored_cls]
            _instance.monitored_instances = weakref.WeakSet()
            
            # thread stuff
            _instance.lock = threading.Lock()
            _instance._stop_event = threading.Event()
            _instance.thread = threading.Thread(target=_instance._monitor_instances, args=(interval,))
            _instance.thread.start() 
            
            # socket stuff
            # _instance.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # _instance.client_socket.connect(server_addr)
        return cls._instances[monitored_cls]
    
    def register(self, monitored_instance):
        """
        The function `register` adds a monitored instance to a set within a thread-safe context.
        
        :param monitored_instance: The `monitored_instance` parameter in the `register` method is the
        instance that you want to add to the set of monitored instances within the class. This parameter
        represents the object or entity that you want to monitor for some specific behavior or
        characteristics
        """
        with self.lock:
            self.monitored_instances.add(monitored_instance)
    
    def deregister(self, monitored_instance):
        with self.lock:
            self.monitored_instances.discard(monitored_instance)
            if not self.monitored_instances:
                self._stop_event.set()
                self.thread.join()
    
    def _get_instance_attr(self, instance):
        return vars(instance)
    
    def _monitor_instances(self, interval):
        while not self._stop_event.is_set():
            with self.lock:
                for instance in self.monitored_instances:
                    #attributes = self._get_instance_attr(instance)
                    #attributes_str = f"Class {self.monitored_cls.__name__} Instance {id(instance)}" + ", ".join(f"{key}={value}" for key, value in attributes.items()) 
                    # print(f"Class {self.monitored_cls.__name__} Instance {id(instance)} attributes: {attributes_str}")
                    inspect(instance, private=True, dunder=True)
                    # send stuff
                    # try:
                    #     self.client_socket.sendall()
                    # except Exception as e:
                    #     print(f"Client error : {e}")
                    #     self._stop_event.set()
                    #     self.client_socket.close()

            time.sleep(interval)

        


# def monitor(cls):

#     """
#     A decorator for the monitored class, goes into the init method of the class and registers an instance of it.
#     """
    
#     class MonitorWrapped(cls):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.class_name = cls.__name__
#             self.instance_name = id(self)
#             monitor = Monitor(weakref.ref(cls), interval=1)
#             monitor.register(self)
#             weakref.finalize(self, monitor.deregister, self)
    
#     return MonitorWrapped

def monitor(cls):

    """
    A decorator for the monitored class, injects monitoring logic into the `__init__` method directly.
    """
    original_init = cls.__init__
    def monitor_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)  # Call the original __init__ method
        self.class_name = cls.__name__
        self.instance_name = id(self)
        monitor_instance = Monitor(weakref.ref(cls), interval=1)  # Create the Monitor for the class
        monitor_instance.register(self)  # Register the instance
        weakref.finalize(self, monitor_instance.deregister, self)  # Ensure cleanup when the object is garbage collected

    cls.__init__ = monitor_init  # Replace the __init__ method
    return cls