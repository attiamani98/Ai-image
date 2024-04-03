import os
import azure.functions as func
import logging
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json

app = func.FunctionApp()

search_service_name = os.environ["SearchServiceName"]
search_admin_key = os.environ["SearchAdminKey"]
search_index_name = os.environ["SearchIndexName"]
search_endpoint = f"https://{search_service_name}.search.windows.net/"

@app.route(route="search", auth_level=func.AuthLevel.ANONYMOUS)
def search_images(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get search query parameter
    search_query = req.params.get('object')
    if not search_query:
        return func.HttpResponse("Please provide a search query", status_code=400)

    try:
        # Create Search Client with endpoint
        search_client = SearchClient(endpoint=search_endpoint,
                                     index_name=search_index_name,
                                     credential=AzureKeyCredential(search_admin_key))

        # Search for images containing the specified object
        search_results = search_client.search(search_text=search_query, include_total_count=True)

        # Extract necessary information from search results
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "@search.score": result["@search.score"],
                "id": result["id"],
                "object_property":result.get("image_url") ,
                "tags": result.get("tags"),
                "description": result.get("description"),
                "image_url": result.get("object_property")
            }
            formatted_results.append(formatted_result)

        # Construct response JSON object
        response_data = {
            "@odata.context": f"https://{search_service_name}.search.windows.net/indexes('{search_index_name}')/$metadata#docs(*)",
            "value": formatted_results,
        }

        # Serialize response JSON object to string
        response_str = json.dumps(response_data)

        # Return HTTP response with the serialized JSON data
        return func.HttpResponse(response_str, status_code=200, mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
