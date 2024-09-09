# Manage Members

Add/Remove members from organization&#x20;

<figure><img src="../../../.gitbook/assets/Screenshot 2024-08-16 at 8.45.09 PM.png" alt=""><figcaption><p>Manage members page</p></figcaption></figure>

```bash
# Format of the commands in the SNET CLI

snet organization add-members [-h] [--gas-price GAS_PRICE]
                              [--wallet-index WALLET_INDEX] [--yes]
                              [--quiet | --verbose]
                              [--registry-at REGISTRY_ADDRESS]
                              ORG_ID ORG_MEMBERS

snet organization rem-members [-h] [--gas-price GAS_PRICE]
                              [--wallet-index WALLET_INDEX] [--yes]
                              [--quiet | --verbose]
                              [--registry-at REGISTRY_ADDRESS]
                              ORG_ID ORG_MEMBERS
```

User Flow:

* Input your group id
* Input any optional parameters you would like (And if you would like quiet or verbose transaction data)
* Click the "Add members" or "Remove members" button, depending on what you would like to do
* Confirm/Deny the gas fee charges for the add/remove transaction
