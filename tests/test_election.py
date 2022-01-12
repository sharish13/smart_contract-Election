from scripts.deploy import deploy_Election
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import accounts, network, exceptions
import pytest


def test_deploy_nd_add_candidates():
    account = get_account()
    election = deploy_Election()
    tx = election.add_candidate("Harry", {"from": account})
    tx.wait(1)
    tx2 = election.add_candidate("Allen", {"from": account})
    tx2.wait(1)
    candidate = election.CandidatesToVotes
    assert candidate(0) == ("Harry", 0)
    assert candidate(1) == ("Allen", 0)
    return election


def test_deploy_nd_add_candidates_from_other_account():
    account = get_account()
    election = deploy_Election()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    bad_actor = accounts[1]
    with pytest.raises(exceptions.VirtualMachineError):
        tx = election.add_candidate("Harry", {"from": bad_actor})


def test_vote_before_election_starts():
    election = test_deploy_nd_add_candidates()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    with pytest.raises(exceptions.VirtualMachineError):
        tx = election.vote("Harry", {"from": accounts[1]})


def test_voting():
    election = test_deploy_nd_add_candidates()
    tx1 = election.start_election({"from": get_account()})
    tx1.wait(1)
    tx2 = election.vote("Harry", {"from": accounts[1]})
    tx2.wait(1)
    assert election.VotersToVotes(accounts[1].address) == 1
    assert election.CandidatesToVotes(0) == ("Harry", 1)
    return election


def test_vote_more_than_once():
    election = test_voting()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    with pytest.raises(exceptions.VirtualMachineError):
        tx = election.vote("Allen", {"from": accounts[1]})


def test_check_the_winner():
    account = get_account()
    election = deploy_Election()
    tx = election.add_candidate("Harry", {"from": account})
    tx.wait(1)
    tx2 = election.add_candidate("Allen", {"from": account})
    tx2.wait(1)
    tx3 = election.start_election({"from": account})
    tx3.wait(1)
    tx4 = election.vote("Harry", {"from": accounts[1]})
    tx4.wait(1)
    tx5 = election.vote("Allen", {"from": accounts[4]})
    tx5.wait(1)
    tx6 = election.vote("Harry", {"from": accounts[6]})
    tx6.wait(1)
    tx7 = election.end_election({"from": account})
    tx7.wait(1)
    assert election.winner() == "Harry"
    return election


def test_vote_nd_stop_election_then_try_to_vote():
    election = test_check_the_winner()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    with pytest.raises(exceptions.VirtualMachineError):
        tx = election.vote("Allen", {"from": accounts[4]})
