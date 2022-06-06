# file: mucast.py
#

# version: 1
# v0: serialize a tree object and send it in chunks via multicasting
# v1: create a single Multicast class
# v2: organize files and try to send an RSA key using DH scheme
#

# usage:
#  Terminal 1: python3 mucast_v2.py --iface='10.108.34.3' --join-mcast-groups '224.1.1.2' --bind-group '224.1.1.2' --type rec
#  Terminal 2: python3 mucast_v2.py --mcast-group '224.1.1.2'

# import modules 
#
import sys
import argparse
from MulticastAgent import MulticastAgent
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Padding
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits
from hashlib import sha256
from Crypto.Random.random import randint
from Crypto.Util import number

# function: generateRSAkeys()
#
def generateRSAkeys():
    key = RSA.generate(2048)
    pem = key.export_key(format='PEM', passphrase='dees')
    f = open('private.pem', 'wb')
    f.write(pem)
    f.close()
    pub = key.publickey()
    pub_pem = pub.export_key(format='PEM')
    f = open('public.pem', 'wb')
    f.write(pub_pem)
    f.close()

#
# end function: generateRSAkeys()

# function: main
#
def main(argv):

    # command line parsing 
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=19900)
    parser.add_argument('--join-mcast-groups', default=[], nargs='*',
                        help='multicast groups (ip addrs) to listen to join')
    parser.add_argument(
        '--iface', default=None,
        help='local interface to use for listening to multicast data; '
        'if unspecified, any interface would be chosen')
    parser.add_argument(
        '--bind-group', default=None,
        help='multicast groups (ip addrs) to bind to for the udp socket; '
        'should be one of the multicast groups joined globally '
        '(not necessarily joined in this python program) '
        'in the interface specified by --iface. '
        'If unspecified, bind to 0.0.0.0 '
        '(all addresses (all multicast addresses) of that interface)')
    parser.add_argument('--mcast-group', default='224.1.1.1')
    parser.add_argument('--type', default='send')
    args = parser.parse_args()

    # instantiate a multicast object
    #
    mca = MulticastAgent(groups=args.join_mcast_groups, port=args.port, iface=args.iface, bind_group=args.bind_group, mcast_group=args.mcast_group)

    # determine whether this node is a sender or reciever
    #
    if args.type == 'rec':
        
        # recieve the messages
        #
        try:
            print("Recieving messages multicast to group {0}".format(args.bind_group))
            mca.recv()
        except KeyboardInterrupt:

            # exit gracefully
            #
            print("\nClosing ports and exiting...")    
            mca.close()
            sys.exit(0)

    elif args.type == 'send':

        # take input from the command line 
        #
        X = 1
        while X:
            try:

                # send an RSA public key
                #
                generateRSAkeys()
                publicKey = open('public.pem').read()

                # test the send method
                #
                mca.send(publicKey.encode())

                X = 0

                # serialize the tree
                #
                #serial_data = pickle.dumps(tree)
                #print(serial_data)
            except KeyboardInterrupt:

                # exit gracefully
                #
                print("\nClosing ports and exiting...")  
                mca.close()
                sys.exit(0)
        
    else:

        # print error message
        #
        print("Invalid node type input. Program terminated.")

#
# end function: main
        
# begin gracefully
#
if __name__ == "__main__":
    main(sys.argv)

#
# end of file
