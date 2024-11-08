import pytest
from algosdk.v2client.algod import AlgodClient
import algokit_utils
from smart_contracts.artifacts.exchange_points.marketplace_smart_contract_client import (
    MarketplaceSmartContractClient,
)

from algosdk import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algopy_testing import algopy_testing_context
from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    PayParams,
    AssetCreateParams,
    AssetTransferParams,
    AssetOptInParams,
)
import algosdk
from algokit_utils.beta.account_manager import AddressAndSigner

from tests.conftest import algod_client


@pytest.fixture(scope="session")
def algorand() -> AlgorandClient:
    return AlgorandClient.default_local_net()


@pytest.fixture(scope="session")
def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
    return algorand.account.dispenser()


@pytest.fixture(scope="session")
def creator(algorand: AlgorandClient, dispenser: AddressAndSigner) -> AddressAndSigner:
    acct = algorand.account.random()
    algorand.send.payment(
        PayParams(
            sender=dispenser.address,
            receiver=acct.address,
            amount=100_000_000,
        )
    )
    return acct


@pytest.fixture(scope="session")
def test_asset_id(creator: AddressAndSigner, algorand: AlgorandClient) -> int:
    sent_txn = algorand.send.asset_create(
        AssetCreateParams(sender=creator.address, total=10)
    )
    return sent_txn["confirmation"]["asset-index"]


@pytest.fixture(scope="session")
def loyalty_exchange_contract_client(
    algorand: AlgorandClient,
    creator: AddressAndSigner,
    test_asset_id: int,
) -> MarketplaceSmartContractClient:
    with algopy_testing_context():
        client = MarketplaceSmartContractClient(
            algod_client=algorand.client.algod,
            sender=creator.address,
            signer=creator.signer,
        )
        client.create_create_application(assetId=test_asset_id, unitaryPrice=0)
        return client


def test_opt_in_to_asset(
    loyalty_exchange_contract_client: MarketplaceSmartContractClient,
    creator: AddressAndSigner,
    test_asset_id: int,
    algorand: AlgorandClient,
):
    # ensure get_asset_information throws an error because the app in not opted in
    pytest.raises(
        algosdk.error.AlgodHTTPError,
        lambda: algorand.account.get_asset_information(
            loyalty_exchange_contract_client.app_address, test_asset_id
        ),
    )

    # We need to send 100_000 uAlgo for account MBR and 100_000 uAlgo for ASA MBR
    mbr_pay_txn = algorand.transactions.payment(
        PayParams(
            sender=creator.address,
            receiver=loyalty_exchange_contract_client.app_address,
            amount=200_000,
            extra_fee=1_000,
        )
    )

    result = loyalty_exchange_contract_client.opt_in_to_asset(
        mbrPay=TransactionWithSigner(txn=mbr_pay_txn, signer=creator.signer),
        transaction_parameters=algokit_utils.TransactionParameters(
            # We are using this asset in the contract , thus we need to tell the AVM that we using this asset
            foreign_assets=[test_asset_id]
        ),
    )
    assert result.confirmed_round
    assert (
        algorand.account.get_asset_information(
            loyalty_exchange_contract_client.app_address, test_asset_id
        )["asset-holding"]["amount"]
        == 0
    )


def test_deposit(
    loyalty_exchange_contract_client: MarketplaceSmartContractClient,
    creator: AddressAndSigner,
    test_asset_id: int,
    algorand: AlgorandClient,
):
    result = algorand.send.asset_transfer(
        AssetTransferParams(
            sender=creator.address,
            receiver=loyalty_exchange_contract_client.app_address,
            asset_id=test_asset_id,
            amount=3,
        )
    )

    assert result["confirmation"]
    assert (
        algorand.account.get_asset_information(
            loyalty_exchange_contract_client.app_address, test_asset_id
        )["asset-holding"]["amount"]
        == 3
    )


def test_set_price(loyalty_exchange_contract_client: MarketplaceSmartContractClient):
    result = loyalty_exchange_contract_client.set_price(unitaryPrice=3_300_000)

    assert result.confirmed_round


def test_buy(
    loyalty_exchange_contract_client: MarketplaceSmartContractClient,
    creator: AddressAndSigner,
    test_asset_id: int,
    algorand: AlgorandClient,
    dispenser: AddressAndSigner,
):
    # create a new account to be the buyer
    buyer = algorand.account.random()

    # use the dispenser to fund buyer
    algorand.send.payment(
        PayParams(
            sender=dispenser.address,
            receiver=buyer.address,
            amount=100_000_000,
        )
    )

    # opt the buyer into the asset
    algorand.send.asset_opt_in(
        AssetOptInParams(sender=buyer.address, asset_id=test_asset_id)
    )

    # form a transaction to buy two assets(2* 3_300_000)
    buyer_payment_txn = algorand.transactions.payment(
        PayParams(
            sender=buyer.address,
            receiver=loyalty_exchange_contract_client.app_address,
            amount=2 * 3_300_000,
            extra_fee=1_000,
        )
    )

    result = loyalty_exchange_contract_client.buy(
        buyerTxn=TransactionWithSigner(txn=buyer_payment_txn, signer=buyer.signer),
        quantity=2,
        transaction_parameters=algokit_utils.TransactionParameters(
            sender=buyer.address, signer=buyer.signer, foreign_assets=[test_asset_id]
        ),
    )

    assert result.confirmed_round

    assert (
        algorand.account.get_asset_information(buyer.address, test_asset_id)[
            "asset-holding"
        ]["amount"]
        == 2
    )


def test_delete_application(
    loyalty_exchange_contract_client: MarketplaceSmartContractClient,
    creator: AddressAndSigner,
    test_asset_id: int,
    algorand: AlgorandClient,
    dispenser: AddressAndSigner,
):
    before_call_amount = algorand.account.get_information(creator.address)["amount"]

    suggested_params = algorand.get_suggested_params()
    result = loyalty_exchange_contract_client.delete_delete_application(
        transaction_parameters=algokit_utils.TransactionParameters(
            foreign_assets=[test_asset_id],
        ),
    )

    assert result.confirmed_round

    after_call_amount = algorand.account.get_information(creator.address)["amount"]

    assert after_call_amount - before_call_amount == (2 + 3_3000_000) + 200_000 - 3_000

    assert (
        algorand.account.get_information(creator.address, test_asset_id)["amount"] == 8
    )
