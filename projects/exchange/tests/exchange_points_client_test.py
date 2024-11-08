# import algokit_utils
# import pytest
# from algokit_utils import get_localnet_default_account
# from algokit_utils.config import config
# from algosdk.v2client.algod import AlgodClient
# from algosdk.v2client.indexer import IndexerClient

# from smart_contracts.artifacts.smart_contract_two.loyalty_exchange_contract_client import (
#     LoyaltyExchangeContractClient,
# )


# import pytest
# from algopy import *
# from smart_contract_two.contract import LoyaltyExchangeContract
# from algopy_testing import algopy_testing_context


# @pytest.fixture
# def deployed_contract():
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
#         print(contract.lei_laciaun_points_asset_id)
#         print
#         yield contract


# def test_opt_in_to_assets(deployed_contract):
#     contract = deployed_contract
#     mbrPay = gtxn.PaymentTransaction(
#         receiver=Global.current_application_address,
#         amount=Global.min_balance + Global.asset_opt_in_min_balance,
#     )
#     contract.optInToAssets(mbrPay)
#     assert Global.current_application_address.is_opted_in(
#         Asset(contract.lei_ograda_points)
#     )
#     assert Global.current_application_address.is_opted_in(
#         Asset(contract.lei_laciaun_points_asset_id)
#     )

#     with pytest.raises(Exception):
#         contract.optInToAssets(mbrPay)


# def test_delete_application(deployed_contract):
#     contract = deployed_contract
#     contract.deleteApplication()
#     assert Global.current_application_address.is_deleted()

#     with pytest.raises(Exception):
#         contract.deleteApplication()


# import pytest
# from algopy import *
# from algosdk.v2client.algod import AlgodClient
# from smart_contracts.exchange_points import LoyaltyExchangeContract
# from algopy_testing import algopy_testing_context


# @pytest.fixture
# def deployed_contract():
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


# @algopy_testing_context()
# def test_opt_in_to_assets(deployed_contract):
#     contract = deployed_contract
#     mbrPay = gtxn.PaymentTransaction(
#         receiver=Global.current_application_address,
#         amount=Global.min_balance + Global.asset_opt_in_min_balance,
#     )
#     contract.optInToAssets(mbrPay)
#     assert Global.current_application_address.is_opted_in(
#         Asset(contract.lei_ograda_points_asset_id)
#     )
#     assert Global.current_application_address.is_opted_in(
#         Asset(contract.lei_laciaun_points_asset_id)
#     )


# # @algopy_testing_context()
# def test_delete_application(deployed_contract):
#     contract = deployed_contract
#     contract.deleteApplication()
#     assert Global.current_application_address.is_deleted()
