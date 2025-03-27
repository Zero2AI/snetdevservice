import grpc
import simplechatbot_pb2
import simplechatbot_pb2_grpc

def run():
    # Connect to the gRPC server
    channel = grpc.insecure_channel('localhost:50051')
    stub = simplechatbot_pb2_grpc.simplechatbotStub(channel)

    def get_user_input():
        return input("You: ")

    try:
        while True:
            # Get user input
            user_input = get_user_input()
            if user_input.lower() in ['exit', 'quit']:
                break

            # Create a predict_req message
            request = simplechatbot_pb2.predict_req(input1=user_input)

            # Call the predict RPC with a timeout of 30 seconds
            response = stub.predict(request, timeout=120)

            # Print the response from the server
            print("Assistant:", response.output1)

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print("Error: The request timed out. The server took too long to respond.")
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print("Error: The server is currently unavailable. Please try again later.")
        else:
            print(f"An error occurred: {e.code()}: {e.details()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("\nChat session ended.")
        channel.close()

if __name__ == '__main__':
    run()
