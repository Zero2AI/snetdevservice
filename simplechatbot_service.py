from concurrent import futures
import logging
import grpc
import simplechatbot_pb2
import simplechatbot_pb2_grpc
import httpx
import asyncio
import json

# Suppress DEBUG messages from httpx and httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class simplechatbot(simplechatbot_pb2_grpc.simplechatbotServicer):

    def predict(self, request, context):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(self._async_predict(request.input1))
            
            loop.close()
            
            output = str(response.get("response", ""))
            return simplechatbot_pb2.predict_resp(output1=output)

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return simplechatbot_pb2.predict_resp(output1="")
        except Exception as e:
            logging.error(f"Error in predict: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return simplechatbot_pb2.predict_resp(output1="")

    async def _async_predict(self, input1):
        async with httpx.AsyncClient() as client:
            payload = {"message": input1}
            logging.info(f"Sending request with payload: {json.dumps(payload)}")
            response = await client.post(
                "https://simplechatbot1.zero2ai.net/predict",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            logging.info(f"Received response: {json.dumps(result)}")
            return result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4),
                         options=[('grpc.max_message_length', 64*1024*1024),
                                  ('grpc.max_send_message_length', 64*1024*1024),
                                  ('grpc.max_receive_message_length', 64*1024*1024)])
    simplechatbot_pb2_grpc.add_simplechatbotServicer_to_server(simplechatbot(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
