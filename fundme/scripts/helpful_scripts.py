from brownie import accounts, network, config, MockV3Aggregator
from web3 import Web3

FORKED_LOCAL_ENV = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
DECIMAL = 8
STARTING_PRICE = 200000000000

def get_account():
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENV
            or network.show_active() in FORKED_LOCAL_ENV):

        return accounts[0]

    else:
        return accounts.add(config["networks"][network.show_active()]["from_key"])

def deploy_mocks():
    print(f"The Active network is {network.show_active()}")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(DECIMAL, Web3.to_wei(STARTING_PRICE, "ether"), {"from": get_account()})