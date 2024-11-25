import math
import grpc
import logging
import threading
import time
import sys
import socket
from concurrent import futures
from glowworm_pb2 import Status, Ack, Empty
import glowworm_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


class Glowworm(glowworm_pb2_grpc.GlowwormServiceServicer):
    def __init__(self, port, neighbors_ports):
        self.phase = math.pi  # Initialphase
        self.natural_frequency = 0.5
        self.neighbors_ports = neighbors_ports
        self.phase_lock = threading.Lock()
        self.running = True
        self.port = port

    def is_port_in_use(self, port):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_server(self):
        """Start the gRPC server on the given port."""
        if self.is_port_in_use(self.port):
            logging.error(f"[Port {self.port}] Port is already in use. Exiting...")
            sys.exit(1)

        try:
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            glowworm_pb2_grpc.add_GlowwormServiceServicer_to_server(self, server)
            server.add_insecure_port(f'[::]:{self.port}')
            server.start()
            logging.info(f"[Port {self.port}] gRPC server successfully started and listening")
            return server
        except Exception as e:
            logging.error(f"[Port {self.port}] Failed to start gRPC server: {e}")
            sys.exit(1)

    def ReceiveStatus(self, request, context):
        """Respond to status requests from neighbors."""
        with self.phase_lock:
            logging.info(f"[Port {self.port}] Sending status: phase={self.phase}")
            return Status(phase=self.phase, natural_frequency=self.natural_frequency)

    def communicate_with_neighbors(self):
        """Continuously communicate with neighbors to synchronize phases."""
        logging.info(f"[Port {self.port}] Communicating with neighbors: {self.neighbors_ports}")
        while self.running:
            neighbors_phases = []
            for port in self.neighbors_ports:
                try:
                    with grpc.insecure_channel(f'localhost:{port}') as channel:
                        stub = glowworm_pb2_grpc.GlowwormServiceStub(channel)
                        response = stub.ReceiveStatus(Empty())
                        neighbors_phases.append(response.phase)
                        logging.info(f"[Port {self.port}] Received phase {response.phase:.2f} from neighbor at port {port}")
                except grpc.RpcError as e:
                    logging.warning(f"[Port {self.port}] Could not connect to neighbor at port {port}: {e}")
            if neighbors_phases:
                self.calculate_next_phase(neighbors_phases)
            time.sleep(0.5)

    def calculate_next_phase(self, neighbors_phases):
        """Update the phase based on neighbor phases."""
        influence = sum(math.sin(neighbor_phase - self.phase) for neighbor_phase in neighbors_phases)
        phase_change = self.natural_frequency + influence
        with self.phase_lock:
            self.phase = (self.phase + phase_change) % (2 * math.pi)
        logging.info(f"[Port {self.port}] Updated phase to {self.phase:.2f}")

    def run(self):
        """Run the Glowworm process."""
        server = self.start_server()
        logging.info(f"[Port {self.port}] Waiting for neighbors to start...")
        time.sleep(5)  # Give neighbors time to start
        neighbor_thread = threading.Thread(target=self.communicate_with_neighbors)
        neighbor_thread.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info(f"[Port {self.port}] Stopping process...")
            self.running = False
            server.stop(0)
            neighbor_thread.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Port and neighbors are required.")
        sys.exit(1)

    port = int(sys.argv[1])
    neighbors_ports = [int(arg) for arg in sys.argv[2:]]
    logging.info(f"Starting Glowworm on port {port} with neighbors {neighbors_ports}")

    glowworm = Glowworm(port=port, neighbors_ports=neighbors_ports)
    glowworm.run()
