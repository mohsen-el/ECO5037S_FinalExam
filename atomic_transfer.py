# Import libraries
from typing import Dict, Any
from algosdk import transaction
from algosdk.v2client import algod
import json

# Connect new client to testnet
algod_address = "https://testnet-api.algonode.cloud"
algod_token = "7fqaktd2q36pesas8fnsk300b8csbnqus7e0da606ome9alf99f"
headers = {
    "X-API-Key":algod_token
}
algod_client = algod.AlgodClient(algod_token, algod_address,headers)


# Define data
# Save generated accounts to variables
adrs_acct_a = "STXHYB5QSVVYPH5LAGZZ3BGMN43WPCISF6VWGIW2XX2WSEHICM3JNW4QJU"
adrs_acct_b = "ZEN5E7HHBLYEE4EZSOYJWIOG7GN6UTVLSFGAZ4MEAQXQWR6WJVDVQ7EFI4"
pk_acct_a = "/NxXiKmM9LSI0eoqLtue8fLrsaClPPlbzgzcHQ5wEsqU7nwHsJVrh5+rAbOdhMxvN2eJEi+rYyLavfVpEOgTNg=="
pk_acct_b = "M1RUOyBHQdNigoXdjFy5NZ6MG16vEugI2/de/V2TCq/JG9J85wrwQnCZk7CbIcb5m+pOq5FMDPGEBC8LR9ZNRw=="

# Define asset
sp = algod_client.suggested_params()
sp = algod_client.suggested_params()
txn = transaction.AssetConfigTxn(
    sender=adrs_acct_b,
    sp=sp,
    default_frozen=False,
    unit_name="UCTZAR",
    asset_name="UCTZAR",
    manager=adrs_acct_b,
    reserve=adrs_acct_b,
    freeze=adrs_acct_b,
    clawback=adrs_acct_b,
    total=100,
    decimals=0,
)
# Sign with secret key of creator
stxn = txn.sign(pk_acct_b)


# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)
print(f"Sent asset create transaction with txid: {txid}")
# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")

# Create opt-in transaction
# asset transfer from account B to A for asset id we want to opt-in to with amt==0
optin_txn = transaction.AssetOptInTxn(
    sender=adrs_acct_a, 
    sp=sp, 
    index=created_asset
)
signed_optin_txn = optin_txn.sign(pk_acct_a)
txid = algod_client.send_transaction(signed_optin_txn)
print(f"Sent opt in transaction with txid: {txid}")

# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# Create transfer transaction
xfer_txn = transaction.AssetTransferTxn(
    sender=adrs_acct_b,
    sp=sp,
    receiver=adrs_acct_a,
    amt=10,
    index=created_asset,
)
# Create payment transaction (send 5 algos to account a)
txn_a = transaction.PaymentTxn(adrs_acct_a, sp, adrs_acct_b, 5000000)

# Group payment and asset transactions
transaction.assign_group_id([txn_a, xfer_txn])

# sign transactions
signed_xfer_txn = xfer_txn.sign(pk_acct_b)
stxn_a = txn_a.sign(pk_acct_a)

# combine the signed transactions into a single list
signed_group = [stxn_a, signed_xfer_txn]


# Only the first transaction id is returned
tx_id = algod_client.send_transactions(signed_group)

# wait for confirmation
result: Dict[str, Any] = transaction.wait_for_confirmation(
    algod_client, tx_id, 4
)
print(f"txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")



