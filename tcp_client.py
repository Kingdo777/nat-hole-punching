#!/usr/bin/env python
import os
import sys
import logging
from util import *
from hole_punch import *

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def main(host='54.187.46.146', port=5005):
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname()

    send_msg(sa, addr_to_msg(priv_addr))
    data = recv_msg(sa)
    logger.info("client %s %s - received data: %s", priv_addr[0], priv_addr[1], data)
    pub_addr = msg_to_addr(data)
    send_msg(sa, addr_to_msg(pub_addr))

    data = recv_msg(sa)
    pubdata, privdata = data.split(b'|')
    client_pub_addr = msg_to_addr(pubdata)
    client_priv_addr = msg_to_addr(privdata)
    logger.info(
        "client public is %s and private is %s, peer public is %s private is %s",
        pub_addr, priv_addr, client_pub_addr, client_priv_addr,
    )

    con = hole_punch(pub_addr, priv_addr, client_pub_addr, client_priv_addr)[0]

    print(con)

    if os.fork() != 0:
        while True:
            data = input()
            con.send(data.encode('utf-8'))
    else:
        while True:
            data = con.recv(1024).decode('utf-8')
            if data == 'quit' or data is None:
                break
            elif data:
                print("received data:", data)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, message='%(asctime)s %(message)s')
    main(*addr_from_args(sys.argv))
