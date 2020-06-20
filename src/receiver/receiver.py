from params import *

# global lock and queue to pass accumulated results to main thread
lock = threading.Lock()
g_queue = deque()

class Stream_receiver( Thread ):
    """
    A class used to start and end a stream receiver.

    Attributes
    ----------
    tid : int
        the thread id of receiver
    stop_event : Event
        The flag to terminate the receiver
    connection : pika.BlockingConnection
        the connection to RabbitMQ server
    channel : Channel
        the channel for message queue
    threshold : Int
        the trigger to trig dumps to the main thread
    dict : Dictionary
        the repository to accumulate incoming messages
    count : Int
        the number of repeated results received
    off_set : Float
        time of receiving the first message in current repository, used to timeout the pooling
    beginning : Float
        time of the first frame was extracted from stream, used to calculate the delay

    Methods
    -------
    stop()
        set the Event flag to stop the thread
        
    run()
        Initiate a receiver, which subscribes to the RabbitMQ, accumulates incoming results, dumps to the global queue,
    """
    def __init__(self, threshold):
        """
        Parameters
        ----------
        tid : int
            the thread id of receiver
        stop_event : Event
            The flag to terminate the receiver
        connection : pika.BlockingConnection
            the connection to RabbitMQ server
        channel : Channel
            the channel for message queue
        threshold : Int
            the trigger to trig dumps to the main thread
        dict : Dictionary
            the repository to accumulate incoming messages
        count : Int
            the number of repeated results received
        off_set : Float
            time of receiving the first message in current repository, used to timeout the pooling
        beginning : Float
            time of the first frame was extracted from stream, used to calculate the delay
        """
        
        super().__init__()
        self._tid = None
        self.stop_event = Event()
        
        self.connection = rb_connect(SERVERS)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=QUEUE_DATA, durable=True)
        
        self.threshold = threshold
        self.dict = {}
        self.count = 0
        self.off_set = -1.0
        self.beginning = -1.0
        
    def stop(self):
        """ Stop the thread """
        self.stop_event.set()
        
    def run(self):
        """ Initiate a receiver """
        def _processData(message):
           """ Accumulate incoming results till threshold or off_set is triggered """
            self.count += 1
            t0 = message.get('timestamp_0')
            t1 = message.get('timestamp_1')
            t2 = time.time()
            
            self.dict = {**self.dict, **message.get('output')}
            print(' [Receiver] {}/{} frames/dict size, time lapse {}, process time {}, transfer time {}'.format(
                message.get('num_cam'), len(self.dict), t2-t0, t1-t0, t2-t1))
            
            
            if self.off_set < 0:
                self.off_set = t2
                
            if self.beginning < 0:
                self.beginning = t0
            
            if self.count > self.threshold or t2 - self.off_set > 10:
                
                dict = self.dict.copy()
                
                global g_queue, lock
                
                with lock:
                    g_queue.append( (t2, t2-self.beginning, dict) )
                    # print(*g_queue, sep='\n\n')
                
                self.count = 0
                self.off_set = -1.0
                self.beginning = -1.0
                self.dict = {}
                
        def _callback(ch, method, properties, body):
            """ Decode and process the incoming message """
            t = time.time()
            message = json.loads(body)
            
            print(" [Receiver] {} [x] Received {} bytes @ {}. Delay {}".format(
                message.get('id'), len(body), t, t-message['timestamp_1']))
            
            _processData(message)
            
            if self.stop_event.is_set():
                self.channel.connection.process_data_events(time_limit=1)
                self.channel.stop_consuming(QUEUE_DATA)

        try:
            print('\n\n')
            print(" [Receiver] Starting collect streaming data on thread id {} ...".format(threading.current_thread().ident))
            self._tid = threading.current_thread().ident
            
            channel = self.channel
            
            while not self.stop_event.is_set():
                print(' [*Receiver*] Waiting for messages. To exit press CTRL+C')

                # comsume and ackownledge incoming message
                channel.basic_consume(queue=QUEUE_DATA, on_message_callback=_callback, auto_ack=True)

                channel.start_consuming()
                
        except KeyboardInterrupt as e:
            print(e)
            pass

        finally:
            print("receiver close connection to queue")
            self.connection.close()
