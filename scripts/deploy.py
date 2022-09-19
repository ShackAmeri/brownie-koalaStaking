from brownie import KoalaToken, Staking, network
from scripts.helpful_scripts import get_contract, get_account
from web3 import Web3

REMAINED_KLA_AMOUNT = Web3.toWei(1000, "ether")


def deploy_KoalaToken_and_Staking():
    account = get_account()
    koala_Token = KoalaToken.deploy(
        1000000000000000000000000, {"from": account}, publish_source=True
    )
    staking = Staking.deploy(
        koala_Token.address, 30, {"from": account}, publish_source=True
    )
    tx = koala_Token.transfer(
        staking.address,
        koala_Token.totalSupply() - REMAINED_KLA_AMOUNT,
        {"from": account},
    )
    tx.wait(2)
    link_token = get_contract("link_token")
    TOKENS_PRIC_FEED_ADDRESSES = {
        koala_Token: get_contract("dai_usd_price_feed"),
        link_token: get_contract("link_usd_price_feed"),
    }
    TOKENS_RATE = {koala_Token: 6, link_token: 0.5}
    set_tokens_data(staking, TOKENS_PRIC_FEED_ADDRESSES, TOKENS_RATE, account)
    return staking, koala_Token


def set_tokens_data(staking, TOKENS_PRICE_FEED_ADDRESSES, TOKENS_RATE, account):
    for token in TOKENS_PRICE_FEED_ADDRESSES:
        set_tx = staking.setTokensData(
            token,
            TOKENS_RATE[token],
            TOKENS_PRICE_FEED_ADDRESSES[token],
            {"from": account},
        )
        set_tx.wait(1)
    return staking


def main():
    deploy_KoalaToken_and_Staking()
