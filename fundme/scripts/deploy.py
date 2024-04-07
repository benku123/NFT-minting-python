from brownie import FundMe, network, config, MockV3Aggregator
from .helpful_scripts import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENV
from web3 import Web3




def deploy_fund_me():
    account = get_account()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address
        print("Mock Deployed!")
    fund_me = FundMe.deploy(
            price_feed_address,
            {"from": account},
            publish_source=config['networks'][network.show_active()].get("varify")
    )
    print(f"Contract deployed to: {fund_me.address}")


def main():
    deploy_fund_me()