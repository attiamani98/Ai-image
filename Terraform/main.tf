terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.97.1"
    }
  }
}
  
provider "azurerm" {
  features {}
}

# Retrieve existing Azure Resource Group
data "azurerm_resource_group" "existing" {
  name = "amani-sandbox"
}
# Define Azure Storage Account (updated to use existing resource group)
resource "azurerm_storage_account" "blob_storage" {
  name                     = "blobstorageaccount"
  resource_group_name      = data.azurerm_resource_group.existing.name
  location                 = data.azurerm_resource_group.existing.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Define Azure Storage Container
resource "azurerm_storage_container" "blob_container" {
  name                  = "images"
  storage_account_name  = azurerm_storage_account.blob_storage.name
  container_access_type = "private"
}

# Define Azure Storage Queue
resource "azurerm_storage_queue" "image_queue" {
  name                  = "imagequeue"
  storage_account_name  = azurerm_storage_account.blob_storage.name
}

# Define Azure Cognitive Search Service
resource "azurerm_search_service" "cognitive_search" {
  name                = "cognitivesearchservice"
  location            = data.azurerm_resource_group.existing.location
  resource_group_name = data.azurerm_resource_group.existing.name
  sku                 = "standard"
}

# Define Azure Cognitive Search Index
resource "azurerm_search_index" "image_index" {
  name              = "imageindex"
  service_name      = azurerm_search_service.cognitive_search.name
  resource_group_name = data.azurerm_resource_group.existing.name
  fields {
    name = "object"
    type = "Edm.String"
  }
}

# Define Azure Function App - Upload Function
resource "azurerm_function_app" "upload_function" {
  name                      = "uploadfunctionapp"
  location                  = data.azurerm_resource_group.existing.location
  resource_group_name       = data.azurerm_resource_group.existing.name
  app_service_plan_id       = azurerm_service_plan.example.id
  storage_account_name      = azurerm_storage_account.blob_storage.name
  storage_account_access_key = azurerm_storage_account.blob_storage.primary_access_key
  app_settings = {
    "AzureWebJobsStorage"      = azurerm_storage_account.blob_storage.primary_blob_connection_string
    "FUNCTIONS_WORKER_RUNTIME" = "dotnet"
  }
}

# Define Azure Function App - Index Function
resource "azurerm_function_app" "index_function" {
  name                      = "indexfunctionapp"
  location                  = data.azurerm_resource_group.existing.location
  resource_group_name       = data.azurerm_resource_group.existing.name
  app_service_plan_id       = azurerm_service_plan.example.id
  storage_account_name      = azurerm_storage_account.blob_storage.name
  storage_account_access_key = azurerm_storage_account.blob_storage.primary_access_key
  app_settings = {
    "AzureWebJobsStorage"      = azurerm_storage_account.blob_storage.primary_blob_connection_string
    "FUNCTIONS_WORKER_RUNTIME" = "python"
  }
}

# Define Azure Function App - Search Function
resource "azurerm_function_app" "search_function" {
  name                      = "searchfunctionapp"
  location                  = data.azurerm_resource_group.existing.location
  resource_group_name       = data.azurerm_resource_group.existing.name
  app_service_plan_id       = azurerm_service_plan.example.id
  storage_account_name      = azurerm_storage_account.blob_storage.name
  storage_account_access_key = azurerm_storage_account.blob_storage.primary_access_key
  app_settings = {
    "AzureWebJobsStorage"      = azurerm_storage_account.blob_storage.primary_blob_connection_string
    "FUNCTIONS_WORKER_RUNTIME" = "node"
  }
}
