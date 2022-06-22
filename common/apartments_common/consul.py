import logging
import socket
import os

import consul


def __get_connection__():
    return consul.Consul(host="consul", port=8500)


def get_hostname():
    return os.uname()[1]


def get_ip_address():   # See https://stackoverflow.com/a/28950776
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def register(svc_type):
    __get_connection__().agent.service.register(name=svc_type,
                                                service_id=get_hostname(),
                                                address=get_ip_address(),
                                                port=5000)
    logging.info(f"Registring {svc_type} to Consul")


def find_services(svc_type):
    _, services = __get_connection__().health.service(service=svc_type,
                                                      wait="5s",
                                                      passing=True)

    found_services = [{"address": service["Service"]["Address"], "port": service["Service"]["Port"]} for service in services]
    logging.info(f"Found {len(found_services)} for type {svc_type}")

    return found_services


def deregister():
    __get_connection__().agent.service.deregister(get_hostname())
