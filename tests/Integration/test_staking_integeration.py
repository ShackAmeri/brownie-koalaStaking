from brownie import network, exceptions, accounts, config, Staking, KoalaToken
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_contract,
    get_account,
)
from scripts.deploy import (
    deploy_KoalaToken_and_Staking,
)
import pytest
from web3 import Web3


def test_only_owner_can_set_tokens_data():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = accounts.add(config["wallets"]["from_key_non_owner"])
    link_token = get_contract("link_token")
    link_usd_price_feed = get_contract("link_usd_price_feed")
    rate = 2
    (staking, kola_token) = deploy_KoalaToken_and_Staking()
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.setTokensData(
            link_token,
            rate,
            link_usd_price_feed,
            {"from": account, "allow_revert": True},
        )


def test_owner_can_set_tokens_data():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    eth_token = get_contract("eth_token")
    eth_usd_price_feed = get_contract("eth_usd_price_feed")
    rate = 1
    # Act
    staking.setTokensData(eth_token, rate, eth_usd_price_feed, {"from": account})
    # Assert
    assert staking.tokensToRate(eth_token) == 1
    assert (
        staking.tokensToPriceFeed(eth_token)
        == "0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e"
    )
    assert staking.tokenIsApproved(eth_token) == True


def test_only_owner_can_change_tokens_approval():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = accounts.add(config["wallets"]["from_key_non_owner"])
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    link_token = get_contract("link_token")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.changeTokenApproval(link_token, {"from": account})


def test_owner_can_change_tokens_approval():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    # Act
    staking.changeTokenApproval(koala_token, {"from": account})
    # Assert
    assert staking.tokenIsApproved(koala_token) == False


def test_cant_stake_token_requirments():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account_owner = get_account()
    account_user = accounts.add(config["wallets"]["from_key_non_owner"])
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    tx_transfer = koala_token.transfer(account_user, amount, {"from": account_owner})
    tx_transfer.wait(1)
    print("user has bought some kla")
    tx_approve = koala_token.approve(staking, amount, {"from": account_user})
    tx_approve.wait(1)
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.stakeToken(koala_token, 0, {"from": account_user})
        staking.changeTokenApproval(koala_token, {"from": account_owner})
        staking.stakeToken(koala_token, 10, {"from": account_user})


def test_can_stake_token():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account_owner = get_account()
    account_user = accounts.add(config["wallets"]["from_key_non_owner"])
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    tx_transfer = koala_token.transfer(account_user, amount, {"from": account_owner})
    tx_transfer.wait(1)
    print("user has bought some kla")
    tx_approve = koala_token.approve(staking, amount, {"from": account_user})
    tx_approve.wait(1)
    balance = staking.tokenToUserBalance(koala_token, account_user)
    # Act
    tx_stake = staking.stakeToken(koala_token, amount, {"from": account_user})
    tx_stake.wait(1)
    print("Staked successfully")
    # Assert
    assert staking.tokenToUserBalance(koala_token, account_user) == balance + amount


def test_can_get_user_balance_value():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account_user = accounts.add(config["wallets"]["from_key_non_owner"])
    account_owner = get_account()
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    tx_transfer = koala_token.transfer(account_user, amount, {"from": account_owner})
    tx_transfer.wait(1)
    print("user has bought some kla")
    tx_approve = koala_token.approve(staking, amount, {"from": account_user})
    tx_approve.wait(1)
    tx_stake = staking.stakeToken(koala_token, amount, {"from": account_user})
    tx_stake.wait(1)
    # Act
    balance_value = staking.getUserBalanceValue(koala_token, {"from": account_user})
    # Assert
    assert balance_value == 9998000000000000000


def test_cant_unstake_before_unstake_time():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account_owner = get_account()
    account_user = accounts.add(config["wallets"]["from_key_non_owner"])
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_token.transfer(account_user, amount, {"from": account_owner})
    print(f"user has bought some kla")
    koala_token.approve(staking, amount, {"from": account_user})
    staking.stakeToken(koala_token, amount, {"from": account_user})
    print(f"Staked successfully")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.unstakeToken(koala_token, amount, {"from": account_user})


def test_cant_claim_zero_rewards():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account_owner = get_account()
    account_user = accounts.add(config["wallets"]["from_key_non_owner"])
    (staking, koala_token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_token.transfer(account_user, amount, {"from": account_owner})
    koala_token.approve(staking, amount, {"from": account_user})
    staking.stakeToken(koala_token, amount, {"from": account_user})
    print(f"Staked successfully")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.claimRewards(koala_token, {"from": account_user})
