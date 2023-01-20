$TARGET_HOST=""
$TEST_CLIENTS=20
$USERS_PER_CLIENT=1
$SPAWN_RATE=1
$RESOURCE_GROUP="test-perf-storage"
$AZURE_STORAGE_ACCOUNT="perfstorage"

echo "creating storage account: $AZURE_STORAGE_ACCOUNT"
az storage account create -n $AZURE_STORAGE_ACCOUNT -g $RESOURCE_GROUP --sku Standard_LRS -o json
	
echo "retrieving storage connection string"
$AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $AZURE_STORAGE_ACCOUNT -g $RESOURCE_GROUP -o tsv)

echo 'creating file share'
az storage share create -n locust --connection-string $AZURE_STORAGE_CONNECTION_STRING -o json

echo 'uploading simulator scripts'
az storage file upload-batch --destination locust --source locust/ --connection-string $AZURE_STORAGE_CONNECTION_STRING -o json

echo "deploying locust ($TEST_CLIENTS clients)..."
$LOCUST_MONITOR=$(az deployment group create -g $RESOURCE_GROUP --template-file locust-arm-template.json --parameters host=$TARGET_HOST storageAccountName=$AZURE_STORAGE_ACCOUNT fileShareName=locust	numberOfInstances=$TEST_CLIENTS	--query properties.outputs.locustMonitor.value	-o tsv)
sleep 10

echo "locust: endpoint: $LOCUST_MONITOR"

echo "locust: starting ..."
$USER_COUNT=$(($USERS_PER_CLIENT*$TEST_CLIENTS))
$SPAWN_RATE=$(($SPAWN_RATE*$TEST_CLIENTS))
echo "locust: monitor available at: $LOCUST_MONITOR"

echo "done"