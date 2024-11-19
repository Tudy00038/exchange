import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from smart_contracts.artifacts.exchange_points.marketplace_smart_contract_client import (
    CreateApplicationArgs,
    DeleteApplicationArgs,
    DeployCreate,
    Deploy,
)

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.exchange_points.marketplace_smart_contract_client import (
        MarketplaceSmartContractClient,
    )

    app_client = MarketplaceSmartContractClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
        create_args=DeployCreate(
            args=CreateApplicationArgs(assetId=123, unitaryPrice=456)
        ),
        delete_args=Deploy(args=DeleteApplicationArgs()),
    )
    # name = "world"
    # response = app_client.hello(name=name)
    # logger.info(
    #     f"Called hello on {app_spec.contract.name} ({app_client.app_id}) "
    #     f"with name={name}, received: {response.return_value}"
    # )
