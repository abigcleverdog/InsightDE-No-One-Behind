"""Stream feeder

This script allows the user to launch a feeder that governizes a certain number of video streams. It is assumed that the videos are in mp4 format.
"""

from params import *

# validate the number of video streams to initiate
try:
    num_providers = int(sys.argv[1])
except:
    sys.stderr.write("Usage: %s [No. of feeders]\n" % sys.argv[0])
    sys.exit(1)

print('\n\n')
print('Start providing {} streams ... ...'.format(num_providers))

# prepare the video streams
videos_path = '/home/ubuntu/Downloads/videos'
videos = [f for f in os.listdir(videos_path) if f.split('.')[-1] == 'mp4']

files = random.sample(videos, k=num_providers)

cameras = {file: cv2.VideoCapture(os.path.join(videos_path, file)) for file in files}


def processImg(thid, file, results, image):
    """ Process a image and analyze it using a pretrained ML model """
    # convert image to greyscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply the pretrained model 
    faceCascade = cv2.CascadeClassifier(CASC_FILE)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the first face found
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        break
        
    # # save the processed image as a jpg file
    # fn = str(int(time.time()*1000)) + '.jpg'
    # cv2.imwrite(fn, image)
        
    # # serilize the image
    # retval, buffer = cv2.imencode('.jpg', image)
    # jpg_as_text = base64.b64encode(buffer)
    
    # register the result, the processed image can be included as needed
    key = "{}_{}".format(thid, file)
    results[key] = len(faces) > 0 # (len(faces) > 0, image)


try:
    # establish RabbitMQ connection
    connection = rb_connect(SERVERS)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_DATA, durable=True)
    
    iframe = 0
    while True:
        # adjust FPS to mimic stream video
        time.sleep(.05)
        t0 = time.time()
        iframe += 1
        
        # sampling frames to be analyzed, high sampling rate provide high accuaracy, low sampling rate provide high performance
        if iframe % FRAME_EX_RATE:
            continue

        # stop the stream
        if iframe>290:
            break
            
        # Extracting frame from each camera
        frames = []
        sizebefore = 0
        for file, camera in cameras.items():
            # read a frame of the stream
            _, frame = camera.read()
            
            if not _:
                if VID_ROLLING:
                    # reload the video
                    camera = cv2.VideoCapture(os.path.join(videos_path, file))
                    _, frame = camera.read()
                else:
                    break
            
            sizebefore += sys.getsizeof(frame)
            height, width, channels = frame.shape
            
            # compress the frame before processing
            if (height,height) != VID_THROUGHPUT_SIZE:
                frame = cv2.resize(frame, VID_THROUGHPUT_SIZE) 
                
            frames.append([file, frame])

        print(" {} ---***--- {} frames extracted. size before preprocessing: {}; after preprocessing {}".format( time.ctime(), len(frames), sizebefore, sys.getsizeof(frames)  ))
            
        # parallel process the frames
        results = {}
        thread_list = []
        thid = threading.current_thread().ident%10000
        for file, frame in frames:
            # initiate a thread to process an individual frame
            t = Thread(target=processImg, args=(thid, file, results, frame))
            thread_list.append(t)
            t.start()
        # wait for all frames are processed
        for t in thread_list:
            t.join()
        
        print(iframe, ' parallel processing done. lose frames? ', len(results) != len(frames), " results size ", sys.getsizeof(results))
        
        # send results to rabbitmq
        message = {
            'id': thid, 
            'timestamp_0': t0,
            'timestamp_1': time.time(),
            'num_cam': num_providers,
            'before': sizebefore,
            'after': sys.getsizeof(frames),
            'output': results
        }
        
        message = json.dumps(message)
        
        print('message size ', sys.getsizeof(message))
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_DATA,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

except KeyboardInterrupt as e:
    print(e)
    pass

finally:
    print("feeder close connection")
    for t in thread_list:
        t.join()
        
    connection.close()