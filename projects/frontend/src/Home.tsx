// src/components/Home.tsx
import * as algokit from '@algorandfoundation/algokit-utils'
import { useWallet } from '@txnlab/use-wallet'
import algosdk from 'algosdk'
import React, { useEffect, useState } from 'react'
import ConnectWallet from './components/ConnectWallet'
import MethodCall from './components/MethodCall'
import { MarketplaceSmartContractClient } from './contracts/MarketplaceSmartContract'
import { buy, create, deleteApp } from './methods'
import { getAlgodConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'
interface HomeProps {}

const Home: React.FC<HomeProps> = () => {
  algokit.Config.configure({ populateAppCallResources: true })
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  const [appId, setAppId] = useState<number>(0)
  //assetId, unitaryPrice, quantity
  const [assetId, setAssetId] = useState<bigint>(0n)
  const [unitaryPrice, setUnitaryPrice] = useState<bigint>(0n)
  const [quantity, setQuantity] = useState<bigint>(0n)
  const [unitsLeft, setUnitsLeft] = useState<bigint>(0n)
  const [seller, setSeller] = useState<string | undefined>(undefined)

  useEffect(() => {
    dmClient
      .getGlobalState()
      .then((globalState) => {
        setUnitaryPrice(globalState.unitaryPrice?.asBigInt() || 0n)
        const id = globalState.assetId?.asBigInt() || 0n
        setAssetId(id),
          algorand.account.getAssetInformation(algosdk.getApplicationAddress(appId), id).then((info) => {
            setUnitsLeft(info.balance)
          })
      })
      .catch(() => {
        setUnitaryPrice(0n)
        setAssetId(0n)
      })

    algorand.client.algod
      .getApplicationByID(appId)
      .do()
      .then((response) => {
        setSeller(response.params.creator)
      })
  }, [appId])

  const { activeAddress, signer } = useWallet()

  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal)
  }

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const algorand = algokit.AlgorandClient.fromConfig({ algodConfig })
  algorand.setDefaultSigner(signer)
  const dmClient = new MarketplaceSmartContractClient(
    {
      resolveBy: 'id',
      id: appId,
      sender: { addr: activeAddress!, signer },
    },
    algorand.client.algod,
  )
  return (
    <div className="hero min-h-screen bg-teal-400">
      <div className="hero-content text-center rounded-lg p-6 max-w-md bg-white mx-auto">
        <div className="max-w-md">
          <h1 className="text-4xl">
            Welcome to <div className="font-bold">AlgoKit 🙂</div>
          </h1>
          <p className="py-6">
            This starter has been generated using official AlgoKit React template. Refer to the resource below for next steps.
          </p>

          <div className="grid">
            <button data-test-id="connect-wallet" className="btn m-2" onClick={toggleWalletModal}>
              Wallet Connection
            </button>
            <div className="divider" />
            <label className="lable">App ID</label>
            <input
              type="number"
              className="input input-bordered"
              value={appId}
              onChange={(e) => setAppId(e.currentTarget.valueAsNumber || 0)}
            />

            <div className="divider" />
            {activeAddress && appId === 0 && (
              <div>
                <label className="label">Unitary Price</label>
                <input
                  type="number"
                  className="input input-bordered"
                  value={(unitaryPrice / BigInt(10e6)).toString()}
                  onChange={(e) => {
                    setUnitaryPrice(BigInt(e.currentTarget.valueAsNumber || 0) * BigInt(10e6))
                  }}
                />
                <MethodCall
                  methodFunction={create(algorand, dmClient, assetId, unitaryPrice, 10n, activeAddress!, setAppId)}
                  text="Create App"
                />
              </div>
            )}

            {appId !== 0 && (
              <div>
                <label className="label">Asset ID</label>
                <input type="text" className="input input-bordered" value={assetId.toString()} readOnly />
                <label className="label">Units Left</label>
                <input type="text" className="input input-bordered" value={unitsLeft.toString()} readOnly />
              </div>
            )}
            <div className="divider" />
            {activeAddress && appId !== 0 && unitsLeft > 0n && (
              <div>
                <label className="label">Price per Unit</label>
                <input type="text" className="input input-bordered" value={(unitaryPrice / BigInt(10e6)).toString()} readOnly />
                <label className="label">Desired quantity</label>
                <input
                  type="number"
                  className="input input-bordered"
                  value={quantity.toString()}
                  onChange={(e) => {
                    setQuantity(BigInt(e.currentTarget.value))
                  }}
                />
                <MethodCall
                  text={`Buy ${quantity} for ${(unitaryPrice * BigInt(quantity)) / BigInt(10e6)} Algo`}
                  methodFunction={buy(
                    algorand,
                    dmClient,
                    activeAddress,
                    algosdk.getApplicationAddress(appId),
                    quantity,
                    unitaryPrice,
                    setUnitsLeft,
                  )}
                />
              </div>
            )}

            {appId !== 0 && unitsLeft <= 0n && activeAddress !== seller && (
              <button disabled className="btn btn-disabled m-2">
                SOLD OUT!
              </button>
            )}

            {appId !== 0 && unitsLeft <= 0n && activeAddress === seller && (
              <MethodCall methodFunction={deleteApp(algorand, dmClient, setAppId)} text="Delete app" />
            )}
          </div>

          <ConnectWallet openModal={openWalletModal} closeModal={toggleWalletModal} />
        </div>
      </div>
    </div>
  )
}

export default Home
