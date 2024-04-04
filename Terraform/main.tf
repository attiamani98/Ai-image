provider "azurerm" {
  skip_provider_registration = true

  features {}
}
resource "azurerm_resource_group" "existing" {
  name = "amani-sandbox"
  location = "westeurope"
}
resource "azurerm_storage_account" "blob_storage" {
  name                     = "imagestorageamani"
  resource_group_name      = azurerm_resource_group.existing.name
  location                 = "westeurope"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "sandbox"
  }
}

resource "azurerm_storage_queue" "queue" {
  name                  = "imagequeue"
  storage_account_name  = azurerm_storage_account.blob_storage.name
}

resource "azurerm_cognitive_account" "objects_detection" {
  resource_group_name      = azurerm_resource_group.existing.name
  name             = "objects-detection"
  location         = "westeurope"
  sku_name         = "F0"
  kind             = "ComputerVision"
  public_network_access_enabled = true
  lifecycle {
    ignore_changes = [
      custom_subdomain_name,
      network_acls
    ]
  }
}


resource "azurerm_search_service" "object_search" {
  name                = "object-search"
  resource_group_name      = azurerm_resource_group.existing.name
  location            = "North Europe"
  sku                 = "standard"
  replica_count       = 1
  partition_count     = 1
  public_network_access_enabled = true
  
}

# Output the endpoint for verification
output "endpoint" {
  value = azurerm_cognitive_account.objects_detection.endpoint
}
