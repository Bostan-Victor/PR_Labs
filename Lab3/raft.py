import socket
import threading
import time
import random

FOLLOWER = "Follower"
CANDIDATE = "Candidate"
LEADER = "Leader"

class Node:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes  
        self.state = FOLLOWER
        self.term = 0
        self.votes_received = 0
        self.leader = None
        self.timeout = random.uniform(5, 10)
        self.last_heartbeat = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.nodes[self.node_id])
        self.running = True 

    def send_message(self, message, target):
        self.socket.sendto(message.encode(), target)

    def broadcast(self, message):
        for i, node in enumerate(self.nodes):
            if i != self.node_id:
                self.send_message(message, node)

    def handle_message(self, message, addr):
        if not self.running:  # Ignore messages if the node is "down"
            return
        if message.startswith("HEARTBEAT"):
            _, term, leader_id = message.split()
            term = int(term)
            if term >= self.term:
                self.state = FOLLOWER
                self.term = term
                self.leader = leader_id
                self.last_heartbeat = time.time()
                print(f"Node {self.node_id}: Received heartbeat from leader {leader_id} (term {term})")
        elif message.startswith("REQUEST_VOTE"):
            _, term, candidate_id = message.split()
            term = int(term)
            if term > self.term:
                self.term = term
                self.state = FOLLOWER
                self.last_heartbeat = time.time()
                self.send_message(f"VOTE {self.term}", addr)
                print(f"Node {self.node_id}: Voted for candidate {candidate_id} (term {term})")
        elif message.startswith("VOTE"):
            _, term = message.split()
            term = int(term)
            if self.state == CANDIDATE and term == self.term:
                self.votes_received += 1
                print(f"Node {self.node_id}: Received vote (total votes: {self.votes_received})")

    def run(self):
        threading.Thread(target=self.listen, daemon=True).start()
        while True:
            if not self.running:  # Simulate failure
                time.sleep(1)
                continue

            if self.state == FOLLOWER:
                if time.time() - self.last_heartbeat > self.timeout:
                    print(f"Node {self.node_id}: Timeout! No heartbeat received. Becoming a candidate.")
                    self.state = CANDIDATE
            elif self.state == CANDIDATE:
                self.term += 1
                self.votes_received = 1
                self.last_heartbeat = time.time()
                self.broadcast(f"REQUEST_VOTE {self.term} {self.node_id}")
                time.sleep(2)
                if self.votes_received > len(self.nodes) // 2:
                    self.state = LEADER
                    self.leader = self.node_id
                    print(f"Node {self.node_id}: Became leader (term {self.term})")
            elif self.state == LEADER:
                print(f"Node {self.node_id}: Sending heartbeat (term {self.term})")
                self.broadcast(f"HEARTBEAT {self.term} {self.node_id}")
                time.sleep(2)

    def listen(self):
        while True:
            try:
                message, addr = self.socket.recvfrom(1024)
                self.handle_message(message.decode(), addr)
            except Exception as e:
                print(f"Node {self.node_id}: Error - {e}")

    def stop(self):
        """Simulate failure by stopping the node."""
        self.running = False
        print(f"Node {self.node_id}: Simulated failure.")

    def restart(self):
        """Restart a failed node."""
        self.running = True
        self.state = FOLLOWER
        self.last_heartbeat = time.time()
        print(f"Node {self.node_id}: Restarted.")

def main():
    num_nodes = 5
    nodes = [("127.0.0.1", 5000 + i) for i in range(num_nodes)]
    node_threads = []
    node_objects = []

    for i in range(num_nodes):
        node = Node(i, nodes)
        thread = threading.Thread(target=node.run, daemon=True)
        node_threads.append(thread)
        node_objects.append(node)
        thread.start()

    # Simulate a leader failure after 20 seconds
    time.sleep(20)
    for node in node_objects:
        if node.state == LEADER:
            node.stop()
            break

    # Restart the failed node after 15 seconds
    time.sleep(15)
    for node in node_objects:
        if not node.running:
            node.restart()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulation stopped.")

if __name__ == "__main__":
    main()
