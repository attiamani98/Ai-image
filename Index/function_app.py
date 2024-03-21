import os
import azure.functions as func
from azure.storage.queue import QueueServiceClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
import logging

app = func.FunctionApp()

@app.function_name(name="IndexFunc")
@app.queue_trigger(arg_name="msg", queue_name="inputqueue",
                   connection="storageAccountConnectionString")  # Queue trigger
def IndexFunc(msg: func.QueueMessage):
    # Connect to Azure Cognitive Services for Computer Vision
    cognitive_services_endpoint = os.environ["CognitiveServicesEndpoint"]
    cognitive_services_key = os.environ["CognitiveServicesKey"]
    computer_vision_client = ComputerVisionClient(cognitive_services_endpoint, AzureKeyCredential(cognitive_services_key))

    # Process the message (image location)
    image_location = msg.get_body().decode('utf-8')

    # Analyze the image using Computer Vision
    image_analysis = computer_vision_client.analyze_image(image_location, visual_features=[VisualFeatureTypes.objects])

    # Extract detected objects from the analysis results
    detected_objects = [obj.object_property for obj in image_analysis.objects]

    # Connect to Azure Cognitive Search
    search_endpoint = os.environ["SearchEndpoint"]
    admin_key = os.environ["SearchAdminKey"]
    search_index_name = os.environ["SearchIndexName"]
    search_client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(admin_key))
    search_client.upload_documents(search_index_name, documents=[{"image_location": image_location, "detected_objects": detected_objects}])

    # Delete the message from the Azure Queue once processed
    queue_service_client = QueueServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
    queue_client = queue_service_client.get_queue_client(os.environ["QueueName"])
    queue_client.delete_message(msg.id, msg.pop_receipt)
