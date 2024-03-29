from django.shortcuts import render
from django.http import request, JsonResponse
from solcx import compile_standard
import json
from web3 import Web3
import os

def deploy_contact(request):
    with open("./SimpleStorage.sol", "r") as file:
        simple_storage_file = file.read()

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.6.0",
    )

    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]

    private_key = os.getenv("PRIVATE_KEY")
    rpc_url = os.getenv("RPC_URL")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    chain_id = 1337

    address = "0xF3717793870a273f7651377A83c864595814962e"

    SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(address)

    transaction = SimpleStorage.constructor().build_transaction(
        {"from": address, "nonce": nonce, "chainId": chain_id}
    )

    sign_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(sign_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    return JsonResponse({"contractAddress": contract_address})
