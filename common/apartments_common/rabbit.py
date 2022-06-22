import logging
import threading

import pika


subscribe_conn = {"connection": None, "channel": None}


def init_publish(exchange):
    logging.info(f"Creating exchange {exchange}")

    connection = __connect__()
    channel = __get_channel__(connection)

    __declare_exchange__(channel, exchange)
    disconnect({"connection": connection, "channel": channel})


def publish(exchange, key, body):
    logging.debug(f"Sending {body} to exchange {exchange}#{key}")

    connection = __connect__()
    channel = __get_channel__(connection)

    channel.basic_publish(exchange=exchange, routing_key=key, body=body)
    disconnect({"connection": connection, "channel": channel})


def init_subscribe(queues_list, callback):
    logging.info(f"Subscribing to queues {queues_list}")
    subscribe_conn["connection"] = __connect__()
    subscribe_conn["channel"] = __get_channel__(subscribe_conn["connection"])
    channel = subscribe_conn["channel"]

    queue_name = __declare_queue__(channel, "")

    for queue in queues_list:
        for key in queue["routing_keys"]:
            channel.queue_bind(exchange=queue["name"], queue=queue_name, routing_key=key)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    threading.Thread(target=thread_runner,
                     args=(channel,),
                     daemon=True).start()

    logging.info("Background rabbit thread started")


def thread_runner(channel):
    channel.start_consuming()


def __connect__():
    logging.info("Connecting to Rabbit")
    return pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))


def __get_channel__(connection):
    logging.info("Connected to Rabbit")
    return connection.channel()


def __declare_exchange__(channel, exchange):
    channel.exchange_declare(exchange=exchange, exchange_type="direct")


def __declare_queue__(channel, name):
    result = channel.queue_declare(queue=name, exclusive=True)
    return result.method.queue


def disconnect(conn_dict=subscribe_conn):
    if conn_dict["channel"] is not None:
        conn_dict["channel"].close()
    if conn_dict["connection"] is not None:
        conn_dict["connection"].close()
