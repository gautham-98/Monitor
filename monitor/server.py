import socket
import threading

class MonitorServer:
    _instance = None
    
    def __new__(cls, host="localhost", port=8080):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.server_addr = (host, port)
            
            # threading
            cls._instance.lock = threading.Lock()
            cls._instance._stop_event = threading.Event()
            
            # and some attributes
            cls._instance.clients = []
            cls._instance.client_threads = []
        return cls._instance              
    
    def start(self):
        # sockets
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_addr)
        self.server_socket.listen() 
        
        # thread
        self.accept_thread = threading.Thread(target=self.accept_clients)
        self.accept_thread.start()
        
    
    def stop(self):
        with self.lock:
            # server shutdown
            self._stop_event.set()
            self.accept_thread.join()
            self.server_socket.close()
            
            # client shutdown
            for (client_socket,_), client_thread in zip(self.clients, self.client_threads):
                client_socket.close()
                client_thread.join()
            
            # cleanup the lists
            self.clients = []
            self.client_threads = []

    def accept_clients(self):
        while not self._stop_event.is_set():
            try:
                client_socket, client_address = self.server_socket.accept()
                with self.lock:
                    self.clients.append((client_socket, client_address))
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))    
                    client_thread.start()
                    self.client_threads.append(client_thread)
            except Exception as e:
                print(f"Server error : {e}")
    
    def handle_client(self, client_socket, client_address):
        try:
            while not self._stop_event.is_set():
                data = client_socket.recv(1024)
                print(data)
                if not data:
                    break
                #process data here
        except Exception as e:
            print(f"Server error : {e}")
        finally:
            with self.lock:
                if (client_socket, client_address) in self.clients:
                    self.clients.remove((client_socket, client_address))
                client_socket.close()
            

if __name__=="__main__":
    server=MonitorServer("localhost", 8080)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()