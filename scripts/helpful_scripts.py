from brownie import (
    accounts,
    network,
    config,
    Contract,
    MockV3Aggregator,
    MockDAI,
    MockBAT,
    MockLINK,
    MockETH,
)
import dotenv

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["ganache", "hardhat", "development"]
INITIAL_PRICE_FEED_VALUE = 2000000000000000000000
DECIMALS = 18
contract_to_mock = {
    "link_usd_price_feed": MockV3Aggregator,
    "bat_usd_price_feed": MockV3Aggregator,
    "bat_token": MockBAT,
    "link_token": MockLINK,
    "dai_token": MockDAI,
    "dai_usd_price_feed": MockV3Aggregator,
    "eth_token": MockETH,
    "eth_usd_price_feed": MockV3Aggregator,
}


def get_account(id=None, index=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it
        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
            )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE_FEED_VALUE):
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")
    print("Deploying Mock DAI...")
    mock_dai = MockDAI.deploy({"from": account})
    print(f"Deployed to {mock_dai.address}")
    print("Deploying Mock LINK...")
    mock_link = MockLINK.deploy({"from": account})
    print(f"Deployed to {mock_link.address}")
    print("Deploying Mock BAT...")
    mock_bat = MockBAT.deploy({"from": account})
    print(f"Deployed to {mock_bat.address}")
    print("Mocks Deployed!")
