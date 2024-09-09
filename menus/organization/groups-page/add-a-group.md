# Add a Group

Add group to organization in local organization metadata&#x20;

<figure><img src="../../../.gitbook/assets/Screenshot 2024-08-16 at 8.39.25 PM.png" alt=""><figcaption><p>Add Group page</p></figcaption></figure>

```bash
# Format of the command in the SNET CLI

snet organization add-group [-h]
                            [--payment-expiration-threshold PAYMENT_EXPIRATION_THRESHOLD]
                            [--payment-channel-storage-type PAYMENT_CHANNEL_STORAGE_TYPE]
                            [--payment-channel-connection-timeout PAYMENT_CHANNEL_CONNECTION_TIMEOUT]
                            [--payment-channel-request-timeout PAYMENT_CHANNEL_REQUEST_TIMEOUT]
                            [--metadata-file METADATA_FILE]
                            [--registry-at REGISTRY_AT]
                            group_name payment_address
                            [endpoints [endpoints ...]]
```

User Flow:

* Input your group name, endpoints, and payment address
* Input any optional parameters you would like (And if you would like quiet or verbose transaction data)
* Input the path to the local metadata file to edit
* Click the "Add group" button
