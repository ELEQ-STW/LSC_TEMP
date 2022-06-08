# Standard micropython libraries
import sys
sys.path.reverse()

# Third party libraries
"""
IMPORTING THIRD PARTY LIBRARIES:
# Use REPL on the ESP32 device with the PuTTY-tool and enter the following:
>>> import upip
>>> upip.cleanup()
>>> upip.get_install_path()
>>> upip.install("micropython-umqtt.simple2")
>>> upip.install("micropython-umqtt.robust2")

No PuTTY on your machine? You can download and install it here:
https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
"""
from umqtt import robust2

# Local modules and variables
# None

# See simple2 source code: https://www.github.com/fizista/micropython-umqtt.simple2/blob/master/src/umqtt/simple2.py
# See robust2 source code: https://www.github.com/fizista/micropython-umqtt.robust2/blob/master/src/umqtt/robust2.py

class Connector(robust2.MQTTClient):
    def __init__(self, *args, **kwargs) -> None:
        """
        Default constructor, initializes MQTTClient object.
        - arguments:
            - client_id: `str`.  Unique MQTT ID attached to client.
            - server: `str`. MQTT host address.
        - keyword arguments:
            - port: `int`. MQTT Port, typically 1883. If unset, the port \
                number will default to 1883 of 8883 base on ssl.
            - user: `str`. Username if your server requires it.
            - password: `str`. Password if your server requires it.
            - keepalive: `int`. The Keep Alive is a time interval measured \
                in seconds since the last correct control packet was received.
            - ssl: `bool`. Require SSL for the connection.
            - ssl_params: `dict`. Required SSL parameters.
            - socket_timeout: `int`. The time in seconds after which the \
                socket interrupts the connection to the server when no data \
                exchange takes place. None - socket blocking, positive \
                number - seconds to wait.
            - message_timeout: `int`. The time in seconds after which the \
                library recognizes that a message with QoS=1 or topic \
                subscription has not been received by the server.
        """
        super().__init__(*args, **kwargs)

    def is_keepalive(self) -> bool:
        """
        It checks if the connection is active. If the connection is not \
            active at the specified time,
        saves an error message and returns False.
        
        returns: `bool`. If the connection is not active at the specified \
            time returns False otherwise True.
        """
        return super().is_keepalive()
    
    def set_callback_status(self, status: int) -> None:
        """
        Set the callback for information about whether the sent packet (QoS=1)
        or subscription was received or not by the server.
        - status: `int`. callable(pid, status). Where:
            - status = `0` - timeout
            - status = `1` - successfully delivered
            - status = `2` - Unknown PID. It is also possible that the \
                PID is outdated, i.e. it came out of the message timeout.
        """
        super().set_callback_status(status)

    def cbstat(self, pid: int, stat: int) -> None:
        """
        Captured message statuses affect the queue here.
        - stat == 0 - the message goes back to the message queue to be sent.
        - stat == 1 or 2 - the message is removed from the queue.
        """
        super().cbstat(pid, stat)
    
    def connect(self, clean_session: bool=True) -> bool:
        """
        Establishes connection with the MQTT server.
        If `clean_session==True`, then the queues are cleared.
        - clean_session: `bool`. Starts new session on true, resumes \
            past session if false.
        - returns: `bool`. Existing persistent session of the client from \
            previous interactions.

        Connection problems are captured and handled by `is_conn_issue()`
        """
        return super().connect(clean_session)
    
    def log(self) -> None:
        super().log()
    
    def reconnect(self) -> bool | None:
        """
        The function tries to resume the connection.

        Connection problems are captured and handled by `is_conn_issue()`
        """
        return super().reconnect()
    
    def resubscribe(self) -> None:
        """
        Function from previously registered subscriptions, sends them again \
            to the server.
        """
        super().resubscribe()
    
    def add_msg_to_send(self, data: bytes) -> None:
        """
        By overwriting this method, you can control the amount of stored \
            data in the queue.
        This is important because we do not have an infinite amount of \
            memory in the devices.

        Currently, this method limits the queue length to MSG_QUEUE_MAX \
            messages.
        The number of active messages is the sum of messages to be sent \
            with messages awaiting confirmation.
        """
        super().add_msg_to_send(data)
    
    def disconnect(self) -> None:
        """
        Disconnects from the MQTT server.
        """
        return super().disconnect()
    
    def ping(self) -> None:
        """
        Pings the MQTT server.
        """
        super().ping()
    
    def publish(self, topic: bytes, msg: bytes, retain: bool=False,
                qos: int=0) -> None | int:
        """
        Publishes a message to a specified topic.
        - arguments:
            - topic: `bytes`. Topic you wish to publish to. Takes the form \
                "path/to/topic"
            - msg: `bytes`. Message to publish to topic.
        - keyword arguments:
            - retain: `bool`. Have the MQTT broker retain the message.
            - qos: `int`. Sets quality of service level. Accepts values \
                0 to 2. PLEASE NOTE qos=2 is not actually supported.
        - returns:
            - None or PID for QoS==1 (only if the message is sent \
            immediately, otherwise it returns None)
        
        The function tries to send a message. If it fails, the message goes \
            to the message queue for sending.
        When we have messages with the retain flag set, only one last \
            message with that flag is sent!
        Connection problems are captured and handled by `is_conn_issue()`
        """
        assert 0 <= qos <= 1, "QoS level 2 is not supported. Choose 1 or 0."
        return super().publish(topic, msg, retain, qos)
    
    def subscribe(self, topic: bytes, qos: int=0,
                  resubscribe: bool=True) -> int:
        """
        Subscribes to a given topic.
        - arguments:
            - topic: `bytes`. Topic you wish to publish to. Takes the \
                form "path/to/topic"
        - keyword arguments
            - qos: `int`. Sets quality of service level. Accepts values \
                0 to 1. This gives the maximum QoS level at which the Server \
                can send Application Messages to the Client.

        The function tries to subscribe to the topic. If it fails,
        the topic subscription goes into the subscription queue.
        Connection problems are captured and handled by `is_conn_issue()`
        """
        assert 0 <= qos <= 1, "QoS level 2 is not supported. Choose 1 or 0."
        return super().subscribe(topic, qos, resubscribe)
    
    def send_queue(self) -> bool:
        """
        The function tries to send all messages and subscribe to all topics \
            that are in the queue to send.
        - returns: `bool`. True if the queue's empty.
        """
        return super().send_queue()
    
    def is_conn_issue(self):
        """
        With this function we can check if there is any connection problem.
        It is best to use this function with the reconnect() method to \
            resume the connection when it is broken.
        You can also check the result of methods such as this:
        - `connect()`
        - `publish()`
        - `subscribe()`
        - `reconnect()`
        - `send_queue()`
        - `disconnect()`
        - `ping()`
        - `wait_msg()`
        - `check_msg()`
        - `is_keepalive()`

        The value of the last error is stored in `self.conn_issue`.
        - returns: `bool`. Connection problem
        """
        return super().is_conn_issue()
    
    def check_msg(self) -> None:
        """
        Checks whether a pending message from server is available.
        If `socket_timeout=None`, this is the socket lock mode. That is, it \
            waits until the data can be read.
        Otherwise it will return `None`, after the time set in the \
            `socket_timeout`.
        It processes such messages:
        - response to PING
        - messages from subscribed topics that are processed by functions \
            set by the `set_callback` method.
        - reply from the server that he received a `QoS=1` message or \
            subscribed to a topic
        
        returns: None
        """
        return super().check_msg()
    
    def wait_msg(self) -> None:
        """
        This method waits for a message from the server.
        Compatibility with previous versions.

        It is recommended not to use this method. Set socket_time=None \
            instead.

        returns: None
        """
        return super().wait_msg()
