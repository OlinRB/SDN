# Assignment link: http://ceskalka.w3.uvm.edu/265/sdn-assignment/

import requests
from constants import*
from dijkstar import Graph, find_path
import sys

class Node:

    def __init__(self, link_info):
        self.node = link_info
        self.src_dest = link_info[:2]
        self.node_name = link_info[0]
        self.dest_name = link_info[1]
        self.port_num = link_info[2]
        self.key = str(self.node_name) + "_" + str(self.dest_name)

    def get_set(self):
        return {self.node_name, self.dest_name}


def forwarding_table(network):
    graph = Graph()
    for node in network:
        graph.add_edge(node.node_name, node.dest_name, 1)

    # Store host links
    host_nodes = []
    entries = []
    src_dest = {}
    all_links = {}
    for node in network:
        if isinstance(node.node_name, str) or isinstance(node.dest_name, str):
            src_dest[node.node_name] = node.node
        all_links[node.key] = node

    #print(src_dest)
    hosts = ["169.254.240.121", "169.254.173.130", "169.254.20.158"]

    paths = []
    for src_node in hosts:
        for dest in hosts:
            if src_node != dest:
                src = src_dest[src_node][1]
                paths.append(find_path(graph, src, dest).nodes)
                #paths.append(find_path(graph, dest, src).nodes)

    for path in paths:
        print(path)
    print(find_path(graph, 9, "169.254.20.158").nodes)



def main():
    send_location = sys.argv[1]
    topology_action = sys.argv[2]
    topology = requests.get(("http://{}:2222/get_topology/{}".format(send_location, topology_action)))
    nodes = topology.json()['connected']

    formatted_tables = requests.post("http://www.goatgoose.com:2222/set_tables/topology1", post_data).json()
    network = []
    for node in nodes:
        network.append(Node(node))
    #print(nodes)
    fw_table = forwarding_table(network)
    print(formatted_tables)

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
