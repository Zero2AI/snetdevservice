# Server Imports
from concurrent import futures
import logging
import os
import grpc
import ocr2txt_pb2
import ocr2txt_pb2_grpc
from gradio_client import Client


class ocr2txt(ocr2txt_pb2_grpc.ocr2txtServicer):

    def predict(self, request, context):
        with open(request.fileName2, mode='wb') as f:
            f.write(request.fileBytes2)
        space_client = Client(
            src='https://pragnakalp-ocr-image-to-text.hf.space/--replicas/5dpj4/')
        #src='https://pragnakalp-ocr-image-to-text.hf.space/--replicas/ydkay/')

        output1 = space_client.predict(
            request.input1, request.fileName2, api_name='/predict')

        return ocr2txt_pb2.predict_resp(output1=output1)


# main server body
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options=[('grpc.max_message_length', 64*1024*1024),
                                                                             ('grpc.max_send_message_length', 64*1024*1024),
                                                                             ('grpc.max_receive_message_length', 64*1024*1024)])
    ocr2txt_pb2_grpc.add_ocr2txtServicer_to_server(ocr2txt(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
