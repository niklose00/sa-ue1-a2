import math
import grpc
import logging
import threading
import time
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

    def SendStatus(self, request, context):
        logging.info(f"[Port {self.port}] Status received: phase={request.phase}, freq={request.natural_frequency}")
        with self.phase_lock:
            response = Ack(message=f"Status received with phase {request.phase}")
            return response

    def ReceiveStatus(self, request, context):
        with self.phase_lock:
            logging.info(f"[Port {self.port}] Sending status: phase={self.phase}")
            return Status(phase=self.phase, natural_frequency=self.natural_frequency)

    def calculate_next_phase(self, neighbors_phases):
        influence = sum(math.sin(neighbor_phase - self.phase) for neighbor_phase in neighbors_phases)
        phase_change = self.natural_frequency + influence
        with self.phase_lock:
            self.phase = (self.phase + phase_change) % (2 * math.pi)
        logging.info(f"[Port {self.port}] Updated phase to {self.phase:.2f}")

    def communicate_with_neighbors(self):
        while self.running:
            neighbors_phases = []
            for port in self.neighbors_ports:
                with grpc.insecure_channel(f'localhost:{port}') as channel:
                    stub = glowworm_pb2_grpc.GlowwormServiceStub(channel)
                    response = stub.ReceiveStatus(Empty())
                    neighbors_phases.append(response.phase)
            self.calculate_next_phase(neighbors_phases)
            time.sleep(0.5)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        glowworm_pb2_grpc.add_GlowwormServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        logging.info(f"[Port {self.port}] gRPC server started")
        return server

    def run(self):
        server = self.start_server()
        neighbor_thread = threading.Thread(target=self.communicate_with_neighbors)
        neighbor_thread.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            server.stop(0)
            neighbor_thread.join()
