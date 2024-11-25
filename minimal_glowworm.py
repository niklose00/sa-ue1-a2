import sys
import time
from concurrent import futures

import grpc
from glowworm_pb2_grpc import add_GlowwormServiceServicer_to_server
from glowworm import Glowworm

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python minimal_glowworm.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glowworm = Glowworm(port=port, neighbors_ports=[])
    add_GlowwormServiceServicer_to_server(glowworm, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Server running on port {port}. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)
