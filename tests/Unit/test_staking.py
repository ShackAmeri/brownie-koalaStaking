# How to test nonreentrent
# How to test emit event
from brownie import network, exceptions, accounts, chain
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
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    bat_usd_price_feed = get_contract("bat_usd_price_feed")
    rate = 2
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.setTokensData(bat_token, rate, bat_usd_price_feed, {"from": account})


def test_owner_can_set_tokens_to_rate():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=0)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    bat_usd_price_feed = get_contract("bat_usd_price_feed")
    rate = 2
    # Act
    staking.setTokensData(bat_token, rate, bat_usd_price_feed, {"from": account})
    # Assert
    assert staking.tokensToRate(bat_token) == 2


def test_owner_can_set_tokens_to_price_feed():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=0)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    bat_usd_price_feed = get_contract("bat_usd_price_feed")
    rate = 2
    # Act
    staking.setTokensData(bat_token, rate, bat_usd_price_feed, {"from": account})
    # Assert
    assert staking.tokensToPriceFeed(bat_token) == bat_usd_price_feed


def test_owner_can_approve_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=0)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    bat_usd_price_feed = get_contract("bat_usd_price_feed")
    rate = 2
    # Act
    staking.setTokensData(bat_token, rate, bat_usd_price_feed, {"from": account})
    # Assert
    assert staking.tokenIsApproved(bat_token) == True


def test_only_owner_can_change_tokens_approval():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.changeTokenApproval(bat_token, {"from": account})


def test_owner_can_change_tokens_approval():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=0)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    # Act
    staking.changeTokenApproval(koala_Token, {"from": account})
    # Assert
    assert staking.tokenIsApproved(koala_Token) == False


def test_only_can_stake_approved_token():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    bat_token = get_contract("bat_token")
    amount = Web3.toWei(10, "ether")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.stakeToken(bat_token, amount, {"from": account})


def test_cant_stake_zero_amount():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.stakeToken(koala_Token, 0, {"from": account})


def test_cant_stake_duplicate_amount():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("Some kla has transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.stakeToken(koala_Token, amount, {"from": account})


def test_stake_token():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("Some kla has transfered")
    user_balance = koala_Token.balanceOf(account)
    staking_balance = koala_Token.balanceOf(staking.address)
    koala_Token.approve(staking, amount, {"from": account})
    # Act
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    # Assert
    assert koala_Token.balanceOf(account) == user_balance - amount
    assert koala_Token.balanceOf(staking.address) == staking_balance + amount


def test_can_stake_token_and_update_user_balance():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("Some kla has transfered")
    koala_Token.approve(staking, amount, {"from": account})
    pre_balance = staking.tokenToUserBalance(koala_Token, account)
    # Act
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    # Assert
    assert staking.tokenToUserBalance(koala_Token, account) == pre_balance + amount


def test_can_update_user_staking_time():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    koala_Token.approve(staking, amount, {"from": account})
    # Act
    staking_time = chain.time()
    staking.stakeToken(koala_Token, amount, {"from": account})
    # Assert
    assert staking.tokenAmountToStakingTime(account, amount) == staking_time


#
def test_cant_get_user_balance_value_if_there_is_no_fund():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.getUserBalanceValue(koala_Token, {"from": account})


def test_can_get_user_balance_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    # Act
    balance_value = staking.getUserBalanceValue(koala_Token, {"from": account})
    # Assert
    assert balance_value == 1000000000000000000


def test_cannot_unstake_more_than_funds():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (
        staking,
        koala_Token,
    ) = deploy_KoalaToken_and_Staking()
    staked_amount = Web3.toWei(5, "ether")
    koala_Token.transfer(account, staked_amount, {"from": get_account(index=0)})
    print("user has bought some kla")
    koala_Token.approve(staking, staked_amount, {"from": account})
    staking.stakeToken(koala_Token, staked_amount, {"from": account})
    print("Staked successfully")
    # Act & Assert
    unstake_amount = Web3.toWei(10, "ether")
    with pytest.raises(exceptions.VirtualMachineError):
        staking.unstakeToken(koala_Token, unstake_amount, {"from": account})


def test_cannot_unstake_before_unstake_time():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (
        staking,
        koala_Token,
    ) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("user has bought some kla")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.unstakeToken(koala_Token, amount, {"from": account})


def test_can_decrease_balance_as_unstake():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("kla is transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    balance = staking.tokenToUserBalance(koala_Token, account)
    # Act
    chain.sleep(2592000)
    staking.unstakeToken(koala_Token, amount, {"from": account})
    # Assert
    new_balance = staking.tokenToUserBalance(koala_Token, account)
    assert new_balance == balance - amount


def test_can_unstake():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (
        staking,
        koala_Token,
    ) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("user has bought some kla")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    user_balance = koala_Token.balanceOf(account)
    staking_balance = koala_Token.balanceOf(staking)
    chain.sleep(2592000)
    # Act
    staking.unstakeToken(koala_Token, amount, {"from": account})
    # Assert
    assert koala_Token.balanceOf(account) == user_balance + amount
    assert koala_Token.balanceOf(staking) == staking_balance - amount


def test_can_calculate_user_reward():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("kla is transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    chain.sleep(2592000)
    # Act
    reward = staking.unstakeToken(koala_Token, amount, {"from": account})
    # Assert
    assert staking.tokenToUserReward(koala_Token, account) == 60000000000000000000


def test_can_remove_amount_staking_time():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (
        staking,
        koala_Token,
    ) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("user has bought some kla")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    chain.sleep(2592000)
    # Act
    staking.unstakeToken(koala_Token, amount, {"from": account})
    # Assert
    assert staking.tokenAmountToStakingTime(account, amount) == 0


def test_cant_claim_rewards_before_unstake():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("kla is transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    chain.sleep(2592000)
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking.claimRewards(koala_Token, {"from": account})


def test_can_delete_user_reward():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("kla is transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    chain.sleep(2592000)
    staking.unstakeToken(koala_Token, amount, {"from": account})
    # Act
    staking.claimRewards(koala_Token, {"from": account})
    # Assert
    assert koala_Token.balanceOf(account) == 70000000000000000000


def test_can_delete_user_reward():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    (staking, koala_Token) = deploy_KoalaToken_and_Staking()
    amount = Web3.toWei(10, "ether")
    koala_Token.transfer(account, amount, {"from": get_account(index=0)})
    print("kla is transfered")
    koala_Token.approve(staking, amount, {"from": account})
    staking.stakeToken(koala_Token, amount, {"from": account})
    print("Staked successfully")
    chain.sleep(2592000)
    staking.unstakeToken(koala_Token, amount, {"from": account})
    # Act
    staking.claimRewards(koala_Token, {"from": account})
    # Assert
    assert staking.tokenToUserReward(koala_Token, account) == 0
