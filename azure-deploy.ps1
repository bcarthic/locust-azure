param
(
    [Parameter(Mandatory=$True)]
    [string]
    $ResourceGroup,

    [Parameter(Mandatory=$True)]
    [string]
    $Region,

    [Parameter(Mandatory=$True)]
    [string]
    $StorageAccountName,

    [Parameter(Mandatory=$True)]
    [string]
    $TargetHost,

    [Parameter(Mandatory=$True)]
    [Security.SecureString]
    $BearerToken,

    [Parameter(Mandatory=$False)]
    [int]
    $NumberOfLocustWorkers = 1
)

Set-PSDebug -Off
$ErrorActionPreference = "Stop"
Write-Host "Ensure resource group and storage account exists"

$rsgExists = az group exists -n $ResourceGroup
if ($rsgExists -eq 'false') {
    Write-Host "Creating resource group"
    az group create --name $ResourceGroup --location $Region
}

$nameAvailable = az storage account check-name -n $StorageAccountName --query 'nameAvailable' -o tsv
if($nameAvailable -eq 'true') {
    Write-Host "Creating storage account: $StorageAccountName with file share: locust"
    az storage account create -n $StorageAccountName -g $ResourceGroup --sku Standard_LRS -o json
    $connectionString=$(az storage account show-connection-string --name $StorageAccountName -g $ResourceGroup -o tsv)
    az storage share create -n locust --connection-string $connectionString -o json
}
else {
    $connectionString=$(az storage account show-connection-string --name $StorageAccountName -g $ResourceGroup -o tsv)
}

Write-Host "Uploading locust scripts"
az storage file upload-batch --destination locust --source locust/ --connection-string $connectionString -o json

Write-Host  "Deploying locust ($NumberOfLocustWorkers clients)..."
$locust=$(az deployment group create -g $ResourceGroup --template-file locust-arm-template.json --parameters host=$TargetHost storageAccountName=$StorageAccountName numberOfInstances=$NumberOfLocustWorkers fileShareName=locust bearerToken=$BearerToken location=$Region --query properties.outputs.locustMonitor.value -o tsv)

Start-Sleep -Seconds 10

Write-Host "Locust: endpoint: $locust"