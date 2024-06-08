import zmq

class IPC:
    def __init__(self):
        self.context = zmq.Context()
        self.sockets = {}

    def init_publisher(self, address):
        """
        Initialize the publisher.
        :param address: The address to bind to.
        """
        self.sockets['pub'] = self.context.socket(zmq.PUB)
        self.sockets['pub'].bind(address)

    def init_subscriber(self, address, topic=''):
        """
        Initialize the subscriber.
        :param address: The address to connect to.
        :param topic: The topic to subscribe to (default is all topics).
        """
        self.sockets['sub'] = self.context.socket(zmq.SUB)
        self.sockets['sub'].connect(address)
        self.sockets['sub'].setsockopt_string(zmq.SUBSCRIBE, topic)

    def publish(self, message, topic=None):
        """
        Send a message.
        :param message: The message to send.
        :param topic: The topic for PUB mode (optional).
        """
        if 'pub' in self.sockets and topic is not None:
            self.sockets['pub'].send_string(f"{topic} {message}")
        elif 'pub' in self.sockets:
            self.sockets['pub'].send_string(message)
        else:
            raise ValueError("Publisher socket is not initialized.")

    def receive_published(self, timeout=500):
        """
        Receive a message with a timeout.
        :param timeout: Timeout in milliseconds to wait for a message.
        :return: The received message or None if no message is received within the timeout.
        """
        if 'sub' in self.sockets:
            socket = self.sockets['sub']
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            socks = dict(poller.poll(timeout))

            if socks.get(socket) == zmq.POLLIN:
                return socket.recv_string()
            else:
                return None
        else:
            raise ValueError("Subscriber socket is not initialized.")


    def close(self):
        """
        Close all sockets and terminate the context.
        """
        for socket in self.sockets.values():
            socket.close()
        self.context.term()

