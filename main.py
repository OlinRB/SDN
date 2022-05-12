# Assignment link: http://ceskalka.w3.uvm.edu/265/sdn-assignment/

import requests
from dijkstar import Graph, find_path
import sys
import os

class Node:

    def __init__(self, link_info):
        self.node = link_info
        self.src_dest = link_info[:2]
        self.node_name = link_info[0]
        self.dest_name = link_info[1]
        self.port_num = link_info[2]
        self.key = str(self.node_name) + "_" + str(self.dest_name)


def forwarding_table(network):
    # Create graph and add edges
    graph = Graph()
    for node in network:
        graph.add_edge(node.node_name, node.dest_name, 1)

    # Find host nodes and directly connected nodes
    src_dest = {}
    for node in network:
        if isinstance(node.node_name, str) or isinstance(node.dest_name, str):
            src_dest[node.node_name] = node.node

    hosts = ["169.254.240.121", "169.254.173.130", "169.254.20.158"]

    paths = []
    for src_node in hosts:
        for dest in hosts:
            if src_node != dest:
                src = src_dest[src_node][1]
                paths.append(find_path(graph, src, dest).nodes)

    # Retrun paths -> each sublist is a path in the network
    return paths


def format_data(fw_table, all_links):
    # Convert data from 2D list from forwarding_table() to REST format
    table_data = []
    for path in fw_table:
        dest = path[len(path)-1]
        while len(path) > 1:
            path_data = {}
            node = all_links[str(path[0]) + "_" + str(path[1])]
            port = node.port_num
            path = path[1:]
            path_data["switch_id"] = node.node_name
            path_data["dst_ip"] = dest
            path_data["out_port"] = port
            table_data.append(path_data)

    formatted_table = {}
    formatted_table["table_entries"] = table_data
    return formatted_table

def main():
    # Pip install library
    os.system("pip install dijkstar")

    # Get cmd line args
    send_location = sys.argv[1]
    topology_action = sys.argv[2]
    virtual = True
    if virtual:
        topology = requests.get(("http://{}:2222/get_topology/{}".format(send_location, topology_action)))
    else:
        topology = requests.get("132.198.11.11:2222/get_topology")
    nodes = topology.json()['connected']

    # Append network
    network = []
    for node in nodes:
        network.append(Node(node))

    # Get forwarding table
    fw_table = forwarding_table(network)

    # format forwarding table
    all_links = {}
    for node in network:
        all_links[node.key] = node
    formatted_table = format_data(fw_table, all_links)

    # Send formatted forwarding table
    if virtual:
        formatted_tables = requests.post("http://www.goatgoose.com:2222/set_tables/topology1", json=formatted_table)
    else:
        formatted_tables = requests.post("132.198.11.11:2222/set_tables", json=formatted_table)

    result = formatted_tables.json()["error"]
    if result == None:
        print("Successfully configured forwarding table")
        print(formatted_tables.json())

    else:
        print("Error...")
        print(formatted_tables.json())

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
