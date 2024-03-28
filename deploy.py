from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

install_solc('0.6.0')


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {  # This is corrected from "pipoutputSelection" to "outputSelection"
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

abi = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']
bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']

private_key = os.getenv("PRIVATE_KEY")
rpc_url = os.getenv("RPC_URL")

print(private_key)
w3 = Web3(Web3.HTTPProvider(rpc_url))
chain_id = 1337

address = "0x467B5EA8844B3dEA1d4037172c63880A270A9BA7"

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(address)

transaction = SimpleStorage.constructor().build_transaction({
    "from": address,
    "nonce": nonce,
    "chainId": chain_id
})

sign_txn = w3.eth.account.sign_transaction(transaction, private_key)
tx_hash = w3.eth.send_raw_transaction(sign_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)