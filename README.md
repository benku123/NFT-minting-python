# Ethereum Smart Contract Deployment Example

## Description
This project demonstrates the compilation and deployment of a Solidity smart contract to a local Ethereum blockchain, specifically using Ganache as the local development environment

## Prerequisites
To run this project, you need to have the following installed on your local machine:
- Python 3.x
- Ganache (local blockchain)
- Solidity Compiler (solc)

Additionally, you'll need some Python libraries which can be installed using pip. Navigate to your project directory and run:

```bash
pip install web3 solcx python-dotenv
```

## Javascript Configuration
**install npm**
```bash
npm intall --global yarn
yarn global add ganache-cli
```

## install Brownie on WIndows
```
pip install pipx
pipx ensurepath 
```

## Run brownie

```angular2html
brownie init 
```
## Configuration
1) Install Solc: The Solidity compiler can be installed directly from the script using install_solc('0.6.0')


2) Ganache Setup: Make sure Ganache is up and running on your local machine. Note the RPC server address **(usually HTTP://127.0.0.1:7545)** and ensure it matches the ***RPC_URL*** in your .env file


3) Environment Variables: Create a .env file in the root of your project directory with the following content, replacing the placeholder with your actual private key from Ganache