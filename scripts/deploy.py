from brownie import Election, network, config
from scripts.helpful_scripts import get_account


def deploy_Election():
    account = get_account()
    election = Election.deploy(
        {"from": account}, publish_source=config["networks"][network.show_active()].get("verify"))
    print(f"Contract deployed to {election.address}")
    return election


def main():
    deploy_Election()
