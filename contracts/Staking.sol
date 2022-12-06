/// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
@title A contract for staking some specific tokens to earn profit with a special rate for each one by the end of 30 days that staked tokens have been locked.
@author Shack
@notice By staking your tokens, you won't be able to reach them within a month; after 30 days, you can withdraw both staked and rewarded tokens.
@dev This contract works with Chainlink AggregatorV3Interface, so ensure that contract addresses are all up to date.
*/

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Staking is Ownable, ReentrancyGuard {
    mapping(address => bool) public s_tokenIsApproved;
    mapping(address => uint8) public s_tokensToRate;
    mapping(address => address) public s_tokensToPriceFeed;
    mapping(address => mapping(address => uint256)) public s_tokenToUserBalance;
    mapping(address => mapping(address => uint256)) public s_tokenToUserReward;
    mapping(address => mapping(uint256 => uint256))
        public s_tokenAmountToStakingTime;
    uint256 public immutable unstakeTime;
    IERC20 public immutable rewardToken;
    event Staked(
        address indexed investor,
        address indexed token,
        uint256 indexed amount
    );
    event Unstaked(
        address indexed investor,
        address indexed token,
        uint256 indexed amount
    );
    event Claimed(
        address indexed investor,
        address indexed token,
        uint256 indexed amount
    );

    constructor(address _rewardToken, uint256 _unstakeTime) {
        rewardToken = IERC20(_rewardToken);
        unstakeTime = _unstakeTime;
    }

    /// @param _token A new token address that can be staked in the future.
    /// @param _rate _token will be rewarded with this rate.
    /// @param _priceFeed Chainlink data feed contract address of _token.
    /// @dev Once a token's added to the contract within this function user can stake them.
    function setTokensData(
        address _token,
        uint8 _rate,
        address _priceFeed
    ) public onlyOwner {
        s_tokensToRate[_token] = _rate;
        s_tokensToPriceFeed[_token] = _priceFeed;
        s_tokenIsApproved[_token] = true;
    }

    /// @param _token  Token address that should be disapproved for staking.
    /// @dev Once a token's disapproved, people won't be able to stake them.
    function changeTokenApproval(address _token) public onlyOwner {
        s_tokenIsApproved[_token] = !s_tokenIsApproved[_token];
    }

    /// @param _token An approved token address is to be staked.
    /// @param _amount A unique and not duplicated amount of token that is wished to be staked by a user.
    /// @notice The token address should be approved and be staked in a unique and not duplicated amount, so if a specific amount of a token was staked before by a user, another amount of it should be staked now.
    /// @dev Once a token's added to the contract within this function user can stake them.
    function stakeToken(address _token, uint256 _amount) external nonReentrant {
        require(s_tokenIsApproved[_token] == true, "Token isn't allowed");
        require(_amount > 0, "You should send at least some token!");
        require(
            s_tokenAmountToStakingTime[msg.sender][_amount] == 0,
            "You have already staked this amount!"
        );
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        updateUserBalance(_token, msg.sender, _amount, block.timestamp);
        emit Staked(msg.sender, _token, _amount);
    }

    /// @param _token token address entered by a user to be staked.
    /// @param _user user address who called stakeToken().
    /// @param _amount A unique and not duplicated amount of token that is wished to be staked by a user.
    /// @param _stakingTime The block time in which the amount of a token is staked in it by a user.
    /// @dev This function is called by stakeToken() whenever a user calls that to stake some token to update the user's new balances.
    /// @dev the 30 days to be able to withdraw the staked amount by the user started by calling this function.
    function updateUserBalance(
        address _token,
        address _user,
        uint256 _amount,
        uint256 _stakingTime
    ) private {
        uint256 _currentBalance = s_tokenToUserBalance[_token][_user];
        s_tokenAmountToStakingTime[_user][_amount] = _stakingTime;
        s_tokenToUserBalance[_token][_user] = _currentBalance + _amount;
    }

    /// @param _token Token address entered by a user for checking its total balance value in USD.
    /// @return uint256 Total token balance value of a user in USD, staked by the user.
    /// @notice This function returns the current token's total balance value in USD that the user staked. It gets this value off-chain using Chainlink oracles.
    /// @dev Current price and token decimals are got off-chain with Chainlink AggregatorV3Interface. Price feed addresses should be checked during time within Chainlink contract addresses for not being disabled. The owner can edit the new price feed address by calling setTokensData().
    function getUserBalanceValue(address _token) public view returns (uint256) {
        uint256 _balance = s_tokenToUserBalance[_token][msg.sender];
        require(_balance > 0, "There's no fund in your account!");
        (uint256 _price, uint256 _decimals) = getValue(_token);
        return (_balance * _price) / (10**_decimals);
    }

    /// @param _token Token address for getting its current price.
    /// @return uint256 Price value in USD gets from Chainlink AggregatorV3Interface.
    /// @return uint256 token's decimals gets from Chainlink AggregatorV3Interface.
    /// @dev Price feed addresses should be checked during time within Chainlink contract addresses for not being disabled. The owner can edit the new price feed address by calling setTokenData().
    function getValue(address _token) private view returns (uint256, uint256) {
        address priceFeedAddress = s_tokensToPriceFeed[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return (uint256(price), uint256(priceFeed.decimals()));
    }

    /// @param _token Token address staked by the user.
    /// @param _amount Staked token amount of each staking.
    /// @notice This function unstakes the amount of token that had been staked by calling stakeToken() individually, not the total token amount that the user has staked. It also calculates the token staking reward.
    /// @notice This amount can be unstake if 30 days have passed of staked time.
    /// @dev unstakeTime was set within the constructor during contract creation.
    function unstakeToken(address _token, uint256 _amount)
        external
        nonReentrant
    {
        require(s_tokenToUserBalance[_token][msg.sender] >= _amount);
        uint256 _stakingTime = s_tokenAmountToStakingTime[msg.sender][_amount];
        require(block.timestamp >= _stakingTime + (unstakeTime * 1 days));
        s_tokenToUserBalance[_token][msg.sender] - _amount;
        IERC20(_token).transfer(msg.sender, _amount);
        rewardCalculator(_token, _amount);
        delete s_tokenAmountToStakingTime[msg.sender][_amount];
        emit Unstaked(msg.sender, _token, _amount);
    }

    /// @dev This private function, called within unstakeToken(), calculates the user reward by multiplying the token staked amount by the token's rate and adds it to the rewards that the user hasn't claimed yet.
    function rewardCalculator(address _token, uint256 _amount) private {
        uint256 preReward = s_tokenToUserReward[_token][msg.sender];
        uint256 _reward = s_tokensToRate[_token] * _amount;
        s_tokenToUserReward[_token][msg.sender] = preReward + _reward;
    }

    /// @param _token Token address staked and unstaked by the user before.
    /// @notice This function transfers all the reward tokens that had been rewarded to the user for staking some _token.
    function claimRewards(address _token) external nonReentrant {
        uint256 _reward = s_tokenToUserReward[_token][msg.sender];
        require(_reward != 0, "You should stake some token to get rewarded");
        rewardToken.transfer(msg.sender, _reward);
        delete s_tokenToUserReward[_token][msg.sender];
        emit Claimed(msg.sender, _token, _reward);
    }
}
