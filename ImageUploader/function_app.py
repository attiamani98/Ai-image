import uuid
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
from azure.storage.queue import QueueServiceClient
app = func.FunctionApp()

@app.route(route="MyHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    
    connection_string = os.environ["AzureWebJobsStorage"]
    container_name = os.environ["ContainerName"] 
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    queue_name = os.environ["QueueName"]
    queue_service_client = QueueServiceClient.from_connection_string(connection_string)

    image = req.get_body()


    # Check if image data is provided
    if not image:
        return func.HttpResponse("No image data provided", status_code=400)
    
    unique_image_name = str(uuid.uuid4()) + ".jpg"

    # Upload the image to Blob Storage with the unique name
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_image_name)
    blob_client.upload_blob(image)
    
    
    image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{unique_image_name}"
    queue_client = queue_service_client.get_queue_client(queue_name)
    queue_client.send_message(image_url)

    return func.HttpResponse(f"Image uploaded successfully. Image location: {image_url}", status_code=200)
