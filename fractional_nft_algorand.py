from typing import Dict, Any
from algosdk import transaction, account, encoding, mnemonic
from algosdk.v2client import algod
from itertools import compress
import json

algod_address = "https://testnet-api.algonode.cloud"
algod_token = "d54uj7ll4121290uo8sr05bgllj3rudlq7nf1v3oqr201lf0un4"
headers = {
    "X-API-Key":algod_token
}
algod_client = algod.AlgodClient(algod_token, algod_address,headers)

# # Uncomment this to create new accounts
# # Define data
# # Accounts addresses
# pk_owner, adrs_owner = account.generate_account()
# pk_rec_1, adrs_rec_1 = account.generate_account()
# pk_rec_2, adrs_rec_2 = account.generate_account()
# pk_rec_3, adrs_rec_3 = account.generate_account()

# print(f"owner address: {adrs_owner}, owner private key: {pk_owner} \n receipient 1 adress: {adrs_rec_1} recipient 1 private key: {pk_rec_1} \n recipient 2 address: {adrs_rec_2} recipient 2 private key: {pk_rec_2} \n recipient 3 address: {adrs_rec_3} recipient 3 private key: {pk_rec_3}")

# Define accounts information (Accounts needs to be funded manually so we cannot generate new accounts before the run)
# Accounts addresses
adr_owner = "GBYHFTOXXKIHXL757YBBKP4ZQ5JAZCKRDB7BSPNRVCBR5Y6TTXY7J73YEM"
adrs_1 = "XPII5XUG6YRTQH3HOWHMVVFJJ6U6ZY5KXQI4SQKU2BZWCTPV44IKKWQRLE"
adrs_2 = "26KEA4LA3CARQEDWHY2GBKHQF3BIQ2VKSCZ5NLOHN3TTUPRTQOVPKOIQZY"
adrs_3 = "M3UDYVFXLDEMCUEL36IG6SD6UYNVI7D2SBOJMIAFJBUJXZM7TENY3HEIA4"

# Accounts private keys
pk_owner = "ST/YIBCOlT1Ju+3QPjM15cxWP+oEd5PTEa5WXbRHdZEwcHLN17qQe6/9/gIVP5mHUgyJURh+GT2xqIMe49Od8Q=="
pk_1 = "zm6VB5SP7jo9tTtTJzirk6FxYrotrw3JPNgRQH6sMly70I7ehvYjOB9ndY7K1KlPqezjqrwRyUFU0HNhTfXnEA=="
pk_2 = "PZWn3sB7tElSPWABtvnoGy3kMEDSFGLiqHhyU2zkvjPXlEBxYNiBGBB2PjRgqPAuwohqqpCz1q3Hbuc6PjODqg=="
pk_3 = "w8UCNIjoHUMZ0YJOKg3EW0hEoJOEkzlzEGmHnc43mC5m6DxUt1jIwVCL35BvSH6mG1R8epBcliAFSGib5Z+ZGw=="

# Create NFT
sp = algod_client.suggested_params()
txn = transaction.AssetConfigTxn(
    sender=adr_owner,
    sp=sp,
    default_frozen=False,
    asset_name="FinTech",
    manager=adr_owner,
    reserve=adr_owner,
    freeze=adr_owner,
    clawback=adr_owner,
    total=1000,
    decimals=3,
)

# Sign with secret key of owner
stxn = txn.sign(pk_owner)
# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)
print(f"Sent asset create transaction with txid: {txid}")
# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")

# Create function to opt in
def transactionOptIn(sender_adress, asset, sender_private_key):
    optin_txn = transaction.AssetOptInTxn(
        sender=sender_adress, sp=sp, index=asset
    )
    signed_optin = optin_txn.sign(sender_private_key)
    txid = algod_client.send_transaction(signed_optin)
    results_round = transaction.wait_for_confirmation(algod_client, txid, 4)
    return([txid, results_round])

# Create function to transfer assets
suggested_params = algod_client.suggested_params()
def assetTransfer(asset, amount, sender_address, sender_private_key, receiver_address):
    xfer_txn = transaction.AssetTransferTxn(
        sender=sender_address, 
        sp=suggested_params,
        receiver=receiver_address,
        amt=amount,
        index=asset
        )
    signed_transaction = xfer_txn.sign(sender_private_key)
    transaction_id = algod_client.send_transaction(signed_transaction)
    result_round = transaction.wait_for_confirmation(algod_client, transaction_id, 4)
    return([transaction_id, result_round])

# Function to check if account holds an asset
def checkAssetExistence(asset, account_address):
    asset_index = [] # a list of booleans to get the index of the asset
    for i in range(0,len(algod_client.account_info(adrs_1)['assets'])):
        exists = created_asset == algod_client.account_info(account_address)['assets'][i]['asset-id']
        asset_index.append(created_asset == algod_client.account_info(account_address)['assets'][i]['asset-id'])
    res = list(compress(range(len(asset_index)), asset_index)) # index where asset exists
    if exists:
        address = account_address
        asset_id = algod_client.account_info(account_address)['assets'][res[0]]['asset-id']
        asset_amount = algod_client.account_info(account_address)['assets'][res[0]]['amount']
        print(f"Address: {address} owns the asset with ID: {asset_id} with a total amount of {asset_amount}")
    else:
        print('Specified account does not hold the asset')

# Use optin function to optin with the 3 accounts
txid_1, result_round_1 = transactionOptIn(adrs_1, created_asset, pk_1)
txid_2, result_round_2 = transactionOptIn(adrs_2, created_asset, pk_2)
txid_3, result_round_3 = transactionOptIn(adrs_3, created_asset, pk_3)

# # Uncomment this to print information about optin transaction for each account
# # Print results
# print(f"Sent opt in transaction with txid1: {txid_1} confirmed in round {result_round_1} \nSent opt in transaction with txid2: {txid_2} confirmed in round {result_round_2} \nSent opt in transaction with txid3 {txid_3} confirmed in round {result_round_3}")

# Use assetTransfer function to transfer fractional NFT to the 3 users
trid1, tr_round_1 = assetTransfer(created_asset, 12, adr_owner, pk_owner, adrs_1)
trid2, tr_round_2 = assetTransfer(created_asset, 16, adr_owner, pk_owner, adrs_2)
trid3, tr_round_3 = assetTransfer(created_asset, 8, adr_owner, pk_owner, adrs_3)

# # Uncomment this to print information about asset transfer transaction for each account
# # Print results
# print(f"transaction to user 1 ID: {trid1} complete in round: {tr_round_1} \ntransaction to user 2 ID: {trid2} complete in round: {tr_round_2} \ntransaction to user 3 ID: {trid3} complete in round: {tr_round_3} \n")

# Check if user holds a fraction of NFT
checkAssetExistence(created_asset ,adrs_1)
checkAssetExistence(created_asset ,adrs_2)
checkAssetExistence(created_asset ,adrs_3)
