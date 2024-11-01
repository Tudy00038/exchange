# # from collections.abc import Iterator

# # import pytest
# # from algopy_testing import AlgopyTestContext, algopy_testing_context

# from smart_contracts.smart_contract_two.contract import LoyaltyExchangeContract

# from algopy_testing import algopy_testing_context
# import pytest
# from algopy import *

# # from smart_contract_two.contract import LoyaltyExchangeContract
# from algokit_utils.beta.algorand_client import (
#     AlgorandClient,
#     PayParams,
#     AssetCreateParams,
# )
# from algokit_utils.beta.account_manager import AddressAndSigner


# @pytest.fixture(scope="session")
# def algorant() -> AlgorandClient:
#     # Get an AlgorantClient to use throughout the tests
#     return AlgorandClient.default_local_net()


# @pytest.fixture(scope="session")
# def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
#     # Get the sispenser to fund test assresses
#     return algorand.account.dispenser()


# @pytest.fixture(scope="session")
# def creator(algorand: AlgorandClient, dispenser: AddressAndSigner) -> AddressAndSigner:
#     acct = algorand.account.random()

#     algorand.send.payment(
#         PayParams(sender=dispenser.address, receiver=acct.address, amount=10_000_000)
#     )
#     return acct


# @pytest.fixture(scope="session")
# def test_asset_id(creator: AddressAndSigner, algorand: AlgorandClient) -> int:
#     sent_txn = algorand.send.asset_create(
#         AssetCreateParams(sender=creator.address, total=10)
#     )
#     return sent_txn["confirmation"]["asset-index"]


# @pytest.fixture(scope="session")
# def loyality_exchange_contract_client(
#     algorand: AlgorandClient, creator: AddressAndSigner, test_asset_id: int
# ) -> LoyaltyExchangeContract:
#     # Instantiate an aplication client we can use for our tests
#     client = LoyaltyExchangeContract(
#         algod_client=algorand.client.algod,
#         sender=creator.address,
#         signer=creator.signer,
#     )

#     client.create_create_application(unitary_price=0, asset_id=test_asset_id)


# def test_pass(
#     loyalty_exchange_contract_client: LoyaltyExchangeContract,
# ):
#     pass


# @pytest.fixture
# def setup_contract():
#     with algopy_testing_context() as context:
#         contract = LoyaltyExchangeContract()
#         ograda_asset = Asset(1001)
#         laciaun_asset = Asset(1002)
#         exchange_rate = UInt64(10)
#         contract.createApplication(
#             lei_ograda_points=ograda_asset,
#             lei_laciaun_points=laciaun_asset,
#             exchange_rate=exchange_rate,
#         )
#         yield contract


# def test_create_application(setup_contract):
#     contract = setup_contract
#     assert contract.lei_ograda_points_asset_id == 1001
#     assert contract.lei_laciaun_points_asset_id == 1002
#     assert contract.exchange_rate == 10

#     with pytest.raises(Exception):
#         contract.createApplication(
#             lei_ograda_points=Asset(1001),
#             lei_laciaun_points=Asset(1002),
#             exchange_rate=UInt64(10),
#         )


# def test_set_exchange_rate(setup_contract):
#     contract = setup_contract
#     new_rate = UInt64(15)
#     contract.setExchangeRate(new_rate)
#     assert contract.exchange_rate == 15

#     with pytest.raises(Exception):
#         contract.setExchangeRate(UInt64(20))

#     with pytest.raises(Exception):
#         contract.setExchangeRate(UInt64(0))


# def test_exchange_points(setup_contract):
#     contract = setup_contract
#     ograda_transfer = gtxn.AssetTransferTransaction(
#         xfer_asset=Asset(contract.lei_ograda_points_asset_id),
#         asset_receiver=Global.current_application_address,
#         asset_amount=UInt64(10),
#     )
#     contract.exchangePoints(ograda_transfer, UInt64(10))

#     laciaun_amount = 10 * contract.exchange_rate

#     with pytest.raises(Exception):
#         contract.exchangePoints(ograda_transfer, UInt64(1000000))

#     invalid_transfer = gtxn.AssetTransferTransaction(
#         xfer_asset=Asset(id=999),
#         asset_receiver=Global.current_application_address,
#         asset_amount=UInt64(10),
#     )
#     with pytest.raises(Exception):
#         contract.exchangePoints(invalid_transfer, UInt64(10))


import pytest
from algopy import *
from algosdk.v2client.algod import AlgodClient
from smart_contracts.artifacts.exchange_points import LoyaltyExchangeContract
from algopy_testing import algopy_testing_context

from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    PayParams,
    AssetCreateParams,
)
from algokit_utils.beta.account_manager import AddressAndSigner


@pytest.fixture(scope="session")
def algorand() -> AlgorandClient:
    # Instantiate the Algorand client for the tests
    return AlgorandClient.default_local_net()


@pytest.fixture(scope="session")
def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
    # Provide funding for the test accounts
    return algorand.account.dispenser()


@pytest.fixture(scope="session")
def creator(algorand: AlgorandClient, dispenser: AddressAndSigner) -> AddressAndSigner:
    acct = algorand.account.random()
    algorand.send.payment(
        PayParams(sender=dispenser.address, receiver=acct.address, amount=10_000_000)
    )
    return acct


@pytest.fixture(scope="session")
def test_asset_id(creator: AddressAndSigner, algorand: AlgorandClient) -> int:
    sent_txn = algorand.send.asset_create(
        AssetCreateParams(sender=creator.address, total=10)
    )
    return sent_txn["confirmation"]["asset-index"]


@pytest.fixture
def setup_contract():
    with algopy_testing_context() as context:
        contract = LoyaltyExchangeContract()
        ograda_asset = Asset(1001)
        laciaun_asset = Asset(1002)
        exchange_rate = UInt64(10)
        contract.createApplication(
            lei_ograda_points=ograda_asset,
            lei_laciaun_points=laciaun_asset,
            exchange_rate=exchange_rate,
        )
        yield contract


# @algopy_testing_context()
def test_create_application(setup_contract):
    contract = setup_contract
    assert contract.lei_ograda_points_asset_id == 1001
    assert contract.lei_laciaun_points_asset_id == 1002
    assert contract.exchange_rate == 10

    with pytest.raises(Exception):
        contract.createApplication(
            lei_ograda_points=Asset(1001),
            lei_laciaun_points=Asset(1002),
            exchange_rate=UInt64(10),
        )


# @algopy_testing_context()
def test_set_exchange_rate(setup_contract):
    contract = setup_contract
    new_rate = UInt64(15)
    contract.setExchangeRate(new_rate)
    assert contract.exchange_rate == 15

    with pytest.raises(AssertionError):
        contract.setExchangeRate(UInt64(0))


# @algopy_testing_context()
def test_exchange_points(setup_contract):
    contract = setup_contract
    with algopy_testing_context() as context:
        ograda_transfer = gtxn.AssetTransferTransaction(
            xfer_asset=Asset(contract.lei_ograda_points_asset_id),
            asset_receiver=Global.current_application_address,
            asset_amount=UInt64(10),
        )
    contract.exchangePoints(ograda_transfer, UInt64(10))

    laciaun_amount = 10 * contract.exchange_rate

    with pytest.raises(Exception):
        contract.exchangePoints(ograda_transfer, UInt64(1000000))
