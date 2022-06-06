# file: mucast.py
#

# version: 1
# v0: erialize a tree object and send it in chunks via multicasting
# v1: create a single Multicast class
#

# usage:
#  Terminal 1: python3 mucast_v1.py --iface='10.108.34.3' --join-mcast-groups '224.1.1.2' --bind-group '224.1.1.2' --type rec
#  Terminal 2: python3 mucast_v1.py --mcast-group '224.1.1.2'

# import modules 
#
import sys
import socket
import struct
import argparse
from Tree import Tree
import pickle

class MulticastAgent:

    # constructor
    #
    def __init__(self, groups, port, iface=None, bind_group=None, mcast_group=None):
        
        # set class data
        #
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.groups = groups
        self.port = port
        self.iface = iface
        self.bind_group = bind_group
        self.mcast_group = mcast_group
        self.tree=None
    
    #
    # end constructor

    # method: recv
    #
    def recv(self):
        
        # allow reuse of socket 
        #
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind to groups
        #
        self.sock.bind(('' if self.bind_group is None else self.bind_group, self.port))
        for group in self.groups:
            mreq = struct.pack(
                '4sl' if self.iface is None else '4s4s',
                socket.inet_aton(group),
                socket.INADDR_ANY if self.iface is None else socket.inet_aton(self.iface))

            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # recieve data
        #
        while True:
            data = self.sock.recv(10240)
            print(data)

    #
    # end method: recv

    # method: send
    #
    def send(self, data):

        # bind to group
        #
        MULTICAST_TTL = 20
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

        # send the data
        #
        self.sock.sendto(b'from multicast_send.py: ' + f'group: {self.bind_group}, port: {self.port},  msg: {data}'.encode(), (self.mcast_group, self.port))

    #
    # end method: send

    # method: close
    #
    def close(self):

        # close the socket
        #
        self.sock.close()

    #
    # end method: close

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
        while True:
            try:

                # generate a tree with the proper number of nodes
                #
                user_input = int(input("Enter the number of nodes in the tree: "))
                tree = Tree()
                for i in range(user_input-1):
                    tree.insertNewUser()
                print(tree)

                # test the send method
                #
                mca.send("Number of nodes in tree: {0}".format(user_input))

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
