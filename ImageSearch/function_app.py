import os
import azure.functions as func
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp()

@app.route(route="search_images", auth_level=func.AuthLevel.ANONYMOUS)
def search_images(req: func.HttpRequest) -> func.HttpResponse:
    # Get the user query from the request
    query = req.params.get('query')
    if not query:
        return func.HttpResponse(
            "Please provide a 'query' parameter in the request.",
            status_code=400
        )

    # Set up Azure Cognitive Search client
    search_service_name = os.environ["SearchServiceName"]
    index_name = os.environ["SearchIndexName"]
    api_key = os.environ["SearchApiKey"]

    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(search_service_name, index_name, credential)

    # Search for images based on user query
    search_results = search_client.search(search_text=query)
    
    # Retrieve image URLs from search results
    image_urls = [result['imageUrl'] for result in search_results.get_results()]

    # Prepare response
    if image_urls:
        response_body = {
            "images": image_urls
        }
        return func.HttpResponse(
            body=response_body,
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "No images found for the given query.",
            status_code=404
        )

