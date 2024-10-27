import algokit_utils
import pytest
from algokit_utils import get_localnet_default_account
from algokit_utils.config import config
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.artifacts.exchange_points.loyalty_exchange_contract_client import (
    LoyaltyExchangeContractClient,
)


import pytest
from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    PayParams,
    AssetCreateParams,
)
from algokit_utils.beta.account_manager import AddressAndSigner

# from smart_contracts.artifacts.marketplace_smart_contract.marketplace_smart_contract_client import (
# MarketplaceSmartContractClient,
# )


@pytest.fixture(scope="session")
def algorant() -> AlgorandClient:
    # Get an AlgorantClient to use throughout the tests
    return AlgorandClient.default_local_net()


@pytest.fixture(scope="session")
def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
    # Get the sispenser to fund test assresses
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


@pytest.fixture(scope="session")
def exchange_points_client(
    algorand: AlgorandClient, creator: AddressAndSigner, test_asset_id: int
) -> LoyaltyExchangeContractClient:
    # Instantiate an aplication client we can use for our tests
    client = LoyaltyExchangeContractClient(
        algod_client=algorand.client.algod,
        sender=creator.address,
        signer=creator.signer,
    )

    client.create_create_application(unitary_price=0, asset_id=test_asset_id)

    def test_pass(
        exchange_points_client: LoyaltyExchangeContractClient,
    ):
        pass
