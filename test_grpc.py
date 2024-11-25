import grpc
from glowworm_pb2 import Empty
from glowworm_pb2_grpc import GlowwormServiceStub

def test_connection(port):
    try:
        with grpc.insecure_channel(f'localhost:{port}') as channel:
            stub = GlowwormServiceStub(channel)
            response = stub.ReceiveStatus(Empty())
            print(f"Connected to port {port}: Phase = {response.phase}")
    except grpc.RpcError as e:
        print(f"Failed to connect to port {port}: {e}")

if __name__ == "__main__":
    ports = [5000, 5001, 5002, 5003]
    for port in ports:
        test_connection(port)
