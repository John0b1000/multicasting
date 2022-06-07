# file: mucast_v2.py
#

# version: 2
# v0: serialize a tree object and send it in chunks via multicasting
# v1: create a single Multicast class
# v2: organize files
#

# usage:
#  Terminal 1: python3 mucast_v2.py --iface='10.150.0.73' --join-mcast-groups '224.1.1.2' --bind-group '224.1.1.2' --type rec
#  Terminal 2: python3 mucast_v2.py --mcast-group '224.1.1.2'

# import modules 
#
import sys
import argparse
from MulticastAgent import MulticastAgent

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
                
                # send a message
                #
                user_input = input("Enter your message here: ")
                mca.send(user_input)
                
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
