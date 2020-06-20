"""Main

This script allows the user to launch a receiver that accumulates messages from feeders, caches the accumulated messages and writes to the MySQL database
"""
from params import *
from receiver import Stream_receiver, g_queue, lock
from xzmysql import DB_handler

# validate the threshold was input
try:
    threshold = int(sys.argv[1])
except:
    sys.stderr.write("Usage: %s [No. of threshold]\n" % sys.argv[0])
    sys.exit(1)

print('\n\n\n')
print("*"*30)
print("*************  Starting testing on thread id {} ...".format(threading.current_thread().ident))
print("*"*30)

# interval of fetching results from the receiver thread
COLLECTOR_INTERVAL = 2

# cache to buffer the messages before writing to database
cache = []

# database table name to be determined
TABLE_NAME = ['']

# establish the connection to database
db_handler = DB_handler()

def store_in_sql(cache, db_handler, TABLE_NAME):
    """ write the cached messages to the database """
    if len(cache) == 0 and len(cache[0]) == 0:
        return

    # create new table for new streaming event
    if TABLE_NAME[0] == '':
        TABLE_NAME[0] = db_handler.create_table(cache[0])
    
    # write message to database
    for message in cache:
        db_handler.insert_entry(message)


try:
    # Initiate Stream_receiver with threshold
    receiver = Stream_receiver(threshold)
    receiver.start()
    
    while True:
        # wait receiver to accumulate messages
        time.sleep(COLLECTOR_INTERVAL)
        
        # cache accumulated messages
        with lock:
            print('#'*50, ' dumping to cache', TABLE_NAME)
            while g_queue:
                cache.append(g_queue.popleft())
        
        # write cache to database
        try:        
            store_in_sql( cache, db_handler, TABLE_NAME )
        except:
            pass
        
        # release cache
        cache = []
            

except KeyboardInterrupt as e:
    print(e)
    pass


finally:
    print("collector close connections")
    db_handler.close()
    receiver.stop()
    receiver.join()

