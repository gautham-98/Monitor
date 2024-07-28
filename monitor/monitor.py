import threading
import time
import weakref

class Monitor:

    """
    A singleton class that creates a single instance per class it tracks.
    """
    
    _instances = {}

    def __new__(cls, monitored_cls, interval):
        """
        instantiate _instance of Class Monitor which tracks a single cls monitored_cls
        """
        if monitored_cls not in cls._instances:
            cls._instances[monitored_cls] = super().__new__(cls)
            _instance = cls._instances[monitored_cls]
            _instance.monitored_cls = monitored_cls
            _instance.monitored_instances = weakref.WeakSet()
            _instance.lock = threading.Lock()
            _instance._stop_event = threading.Event()
            _instance.thread = threading.Thread(target=_instance._monitor_instances, args=(interval,))
            _instance.thread.daemon = True
            _instance.thread.start() 
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
    
    def _get_instance_attr(self, instance):
        return vars(instance)
    
    def _monitor_instances(self, interval):
        while not self._stop_event.is_set():
            with self.lock:
                for instance in self.monitored_instances:
                    attributes = self._get_instance_attr(instance)
                    attributes_str = ", ".join(f"{key}={value}" for key, value in attributes.items())
                    print(f"Class {self.monitored_cls} Instance {id(instance)} attributes: {attributes_str}")
            time.sleep(interval)

        


def monitor(cls):

    """
    A decorator for the monitored class, goes into the init method of the class and registers an instance of it.
    """
    
    class MonitorWrapped(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            monitor = Monitor(cls, interval=1)
            monitor.register(self)
            weakref.finalize(self, monitor.deregister, self)
    
    return MonitorWrapped