"""
    This program listens for work messages continuously. 
    Start multiple versions to add more workers.  

    Author: Brett Neely
    Date: May 26th, 2024

"""

import pika
import sys
import time
from collections import deque
import re

# Define the deques outside of functions so they can be appended to
smoker_deque = deque(maxlen=5)
brisket_deque = deque(maxlen=20)
ribs_deque = deque(maxlen=20)

# Define a file-level variable to store the unicode degree sign
# This variable can be called to print the degree symbol after temperature readings
degree_sign = u'\N{DEGREE SIGN}'

# Define a callback function to be called when a message is received
def smoker_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")
    # simulate work by sleeping for the number of dots in the message
    time.sleep(body.count(b"."))
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Clean the body of the message to find the temperature
    body_decode = body.decode('utf-8')
    temps = re.findall(r'BBQ Smoker is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    smoker_deque.append(temps_float)

    # We want to know if the smoker temperature decreases by more than 15 degrees F in 2.5 minutes (smoker alert!)
    if len(smoker_deque) == smoker_deque.maxlen:
        if smoker_deque[0] - temps_float > 15:
            smoker_change = smoker_deque[0] - temps_float
            print(f'''
####################### SMOKER ALERT #######################
BBQ Smoker temperature has decreased by {smoker_change}{degree_sign} in 2.5 minutes!
############################################################
            ''')

def brisket_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")    
    # simulate work by sleeping for the number of dots in the message
    time.sleep(body.count(b"."))
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Clean the body of the message to find the temperature
    body_decode = body.decode('utf-8')
    temps = re.findall(r'Brisket temp is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    brisket_deque.append(temps_float)

    # We want to know if any food temperature changes less than 1 degree F in 10 minutes (food stall!)
    if len(brisket_deque) == brisket_deque.maxlen:
        if max(brisket_deque) - min(brisket_deque) < 1:
            brisket_change = max(brisket_deque) - min(brisket_deque)
            print(f'''
####################### BRISKET ALERT #######################
Brisket temperature has decreased by {brisket_change}{degree_sign} in 10 minutes!
#############################################################
            ''')

def ribs_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")
    # simulate work by sleeping for the number of dots in the message
    time.sleep(body.count(b"."))
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Clean the body of the message to find the temperature
    body_decode = body.decode('utf-8')
    temps = re.findall(r'Ribs temp is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    ribs_deque.append(temps_float)

    # We want to know if any food temperature changes less than 1 degree F in 10 minutes (food stall!)
    if len(ribs_deque) == ribs_deque.maxlen:
        if max(ribs_deque) - min(ribs_deque) < 1:
            ribs_change = max(ribs_deque) - min(ribs_deque)
            print(f'''
####################### RIBS ALERT #######################
Ribs temperature has decreased by {ribs_change}{degree_sign} in 10 minutes!
##########################################################
            ''')

# define a main function to run the program
def main(host: str):
    """ Continuously listen for task messages on a named queue."""
    queues = ('smoker-queue', 'brisket-queue', 'ribs-queue')
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={host}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)
    try:
        channel = connection.channel()
        for queue in queues:
            channel.queue_delete(queue=queue)
            channel.queue_declare(queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume("smoker-queue", on_message_callback=smoker_callback, auto_ack=False)
        channel.basic_consume("brisket-queue", on_message_callback=brisket_callback, auto_ack=False)
        channel.basic_consume("ribs-queue", on_message_callback=ribs_callback, auto_ack=False)
        print(" Listening Worker Status: Ready for work. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

if __name__ == "__main__":
    # call the main function with the information needed

    host = 'localhost'
    main(host)
