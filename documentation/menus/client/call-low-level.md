# Call Low Level

Low level function for calling the server. Service should be already initialized.

<figure><img src="../../.gitbook/assets/Screenshot 2024-08-17 at 6.17.01 PM.png" alt=""><figcaption><p>Call low-level page</p></figcaption></figure>

```bash
# Format of the command in the SNET CLI

snet client call-lowlevel [-h] [--service SERVICE]
                          [--wallet-index WALLET_INDEX]
                          [--multipartyescrow-at MULTIPARTYESCROW_AT]
                          [--save-response FILENAME]
                          [--save-field SAVE_FIELD SAVE_FIELD]
                          [--endpoint ENDPOINT]
                          ORG_ID SERVICE_ID group_name CHANNEL_ID NONCE
                          AMOUNT_IN_COGS METHOD [PARAMS]
```

User flow:

* Input the org id, service id, group name, channel id, nonce, amount in AGIX, method and a JSON formatted list of parameters
* Input any optional parameters you would like
* Click the "Call low-level" button
