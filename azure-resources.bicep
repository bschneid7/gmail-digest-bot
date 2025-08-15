@description('Location for all resources')
param location string = resourceGroup().location

@description('Name prefix for all resources')
param namePrefix string = 'gmail-digest'

@description('Admin email for initial access')
param adminEmail string

@description('Google OAuth client ID')
@secure()
param googleClientId string

@description('Google OAuth client secret')
@secure()
param googleClientSecret string

@description('Gmail refresh token')
@secure()
param gmailRefreshToken string

@description('SendGrid API key')
@secure()
param sendGridApiKey string

@description('Flask secret key')
@secure()
param flaskSecretKey string = newGuid()

@description('API key for internal communication')
@secure()
param apiKey string = newGuid()

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: '${namePrefix}-plan'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
  kind: 'linux'
}

// Cosmos DB Account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: '${namePrefix}-cosmos'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

// Cosmos DB Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosAccount
  name: 'GmailDigest'
  properties: {
    resource: {
      id: 'GmailDigest'
    }
  }
}

// Cosmos DB Container
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'Data'
  properties: {
    resource: {
      id: 'Data'
      partitionKey: {
        paths: ['/pk']
        kind: 'Hash'
      }
    }
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: '${namePrefix}-app'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|nginx'
      appSettings: [
        {
          name: 'FLASK_SECRET_KEY'
          value: flaskSecretKey
        }
        {
          name: 'GOOGLE_CLIENT_ID'
          value: googleClientId
        }
        {
          name: 'GOOGLE_CLIENT_SECRET'
          value: googleClientSecret
        }
        {
          name: 'GMAIL_REFRESH_TOKEN'
          value: gmailRefreshToken
        }
        {
          name: 'ADMIN_EMAIL'
          value: adminEmail
        }
        {
          name: 'X_API_KEY'
          value: apiKey
        }
        {
          name: 'COSMOS_URL'
          value: cosmosAccount.properties.documentEndpoint
        }
        {
          name: 'COSMOS_KEY'
          value: cosmosAccount.listKeys().primaryMasterKey
        }
        {
          name: 'COSMOS_DB'
          value: 'GmailDigest'
        }
        {
          name: 'COSMOS_CONTAINER'
          value: 'Data'
        }
        {
          name: 'SENDGRID_API_KEY'
          value: sendGridApiKey
        }
        {
          name: 'TZ'
          value: 'America/Los_Angeles'
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://index.docker.io/v1'
        }
      ]
    }
  }
}

// Storage Account for Functions
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${replace(namePrefix, '-', '')}storage'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

// Function App Plan
resource functionPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: '${namePrefix}-func-plan'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
  }
  kind: 'functionapp'
}

// Function App
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: '${namePrefix}-scheduler'
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: functionPlan.id
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'BACKEND_BASE_URL'
          value: 'https://${webApp.properties.defaultHostName}'
        }
        {
          name: 'X_API_KEY'
          value: apiKey
        }
        {
          name: 'TZ'
          value: 'America/Los_Angeles'
        }
      ]
    }
  }
}

// Outputs
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output functionAppName string = functionApp.name
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint

