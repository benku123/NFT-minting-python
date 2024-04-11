from brownie import accounts, config, network


LOCAL_BLOCKCHAIN_ENVIRONMENT = [
    'development',
    'ganache',
    'hardhat',
    'local-ganache',
    'mainnet-fork'
]


def get_account(index=None, id=None):
    if index:
        return accounts[0]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        print(accounts[0].balance())
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() == "development":
        return accounts.add(config["wallets"]["from_key"])
    return None