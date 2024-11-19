import * as algokit from '@algorandfoundation/algokit-utils'
import { MarketplaceSmartContractClient } from './contracts/MarketplaceSmartContract'

export function create(
  algorand: algokit.AlgorandClient,
  dmClient: MarketplaceSmartContractClient,
  assetBeingSold: bigint,
  unitaryPrice: bigint,
  quantity: bigint,
  sender: string,
  setAppId: (id: number) => void,
) {
  return async () => {
    let assetId = assetBeingSold
    if (assetId === 0n) {
      const assetCreate = await algorand.send.assetCreate({
        sender,
        total: quantity,
      })
      assetId = BigInt(assetCreate.confirmation.assetIndex!)
      //assetId = BigInt(1023)
    }

    const createResult = await dmClient.create.createApplication({ assetId, unitaryPrice })

    const mbrPay = await algorand.transactions.payment({
      sender,
      receiver: createResult.appAddress,
      amount: algokit.algos(0.1 + 0.1),
      extraFee: algokit.algos(0.001),
    })
    await dmClient.optInToAsset({ mbrPay })
    await algorand.send.assetTransfer({
      sender,
      assetId,
      receiver: createResult.appAddress,
      amount: quantity,
    })

    setAppId(Number(createResult.appId))
  }
}

export function buy(
  algorand: algokit.AlgorandClient,
  dmClient: MarketplaceSmartContractClient,
  sender: string,
  appAddress: string,
  quantity: bigint,
  unitaryPrice: bigint,
  setUnitsLeft: (units: bigint) => void,
) {
  return async () => {
    const buyerTxn = await algorand.transactions.payment({
      sender,
      receiver: appAddress,
      amount: algokit.microAlgos(Number(quantity * unitaryPrice)),
      extraFee: algokit.algos(0.001),
    })
    await dmClient.buy({ buyerTxn, quantity })

    const state = await dmClient.getGlobalState()
    const info = await algorand.account.getAssetInformation(appAddress, state.assetId!.asBigInt())
    setUnitsLeft(info.balance)
  }
}

export function deleteApp(algorand: algokit.AlgorandClient, dmClient: MarketplaceSmartContractClient, setAppId: (id: number) => void) {
  return async () => {
    await dmClient.delete.deleteApplication({}, { sendParams: { fee: algokit.algos(0.003) } })
    setAppId(0)
  }
}
