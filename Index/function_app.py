import uuid
import azure.functions as func
import logging
import os
from urllib.parse import urlparse
import json
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Azure Cognitive Search settings
search_service_name = "object-search"
index_name = "azureblob-index"
search_key = "mm6scwzV4h307dYYiNeDVrXehMRFH4SeFtsL5gvbMXAzSeCySCtX"
search_client = SearchClient(f"https://{search_service_name}.search.windows.net/", index_name, AzureKeyCredential(search_key))
queue_name = os.environ["QueueName"]
key = '6b129a68441e44baa72b62c89066ccfc'
endpoint = 'https://objects-detection.cognitiveservices.azure.com/'
sas_token = os.environ["sas_token"]
# Configure Azure Cognitive Search credentials
search_service_name = os.environ["SearchServiceName"]
search_admin_key = os.environ["SearchAdminKey"]
search_index_name = os.environ["SearchIndexName"]
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))


app = func.FunctionApp()


def index_detected_objects(search_client, detected_object, descrption,image_path):
    # Define a unique key for the document
    document_key = str(uuid.uuid4())

    # Create the document to be indexed
    document = {
        "@search.action": "upload",  # Action specifies the operation to perform (e.g., upload, merge, delete)
        "id": document_key,          
        "object_property": detected_object,
        "description": descrption
    }

    try:
        # Log the document as JSON
        logging.info(json.dumps(document))

        # Upload the document to Azure Cognitive Search
        result = search_client.upload_documents(documents=[document])


        return result
        
    except Exception as e:
        logging.error(f"Error indexing document: {str(e)}")

def index_detected_tags(search_client, detected_tags, descrption, image_path):
    # Define a unique key for the document
    document_key = str(uuid.uuid4())

    # Create the document to be indexed
    document = {
        "@search.action": "upload",  
        "id": document_key,          
        "tags": detected_tags,          
        "description": descrption
    }

    try:
        # Log the document as JSON
        logging.info(json.dumps(document))

        # Upload the document to Azure Cognitive Search
        result = search_client.upload_documents(documents=[document])

        logging.info(f"Indexed document for image {image_path}")

        return result
        
    except Exception as e:
        logging.error(f"Error indexing document: {str(e)}")

@app.queue_trigger(arg_name="azqueue", queue_name=queue_name, connection="")
def Indexes(azqueue: func.QueueMessage):
   
     # Retrieve the image URL from the queue message
    image_url = azqueue.get_body().decode('utf-8')
    logging.info('Python Queue trigger processed a message %s', image_url)
    image_url_with_sas = f"{image_url}?{sas_token}"

    # Parse the URL
    parsed_url = urlparse(image_url_with_sas)

    # Get the full URL
    image_path = parsed_url.geturl()

    logging.info(image_path)

    try:
        analysis = computervision_client.analyze_image(image_path, visual_features=[VisualFeatureTypes.objects, VisualFeatureTypes.tags, VisualFeatureTypes.description])
        logging.info("Objects: %s", analysis)
        description = analysis.description.captions[0].text

        for obj in analysis.objects:
            index_detected_objects(search_client,image_path,obj.object_property,description)

        for tag in analysis.tags:
            index_detected_tags(search_client, image_path, tag.name,description)

        logging.info("Analyses done")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    