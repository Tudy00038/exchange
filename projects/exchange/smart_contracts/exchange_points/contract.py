from algopy import *


class LoyaltyExchangeContract(ARC4Contract):
    lei_ograda_points_asset_id: UInt64
    lei_laciaun_points_asset_id: UInt64
    exchange_rate: UInt64  # How many leiLaCiaun points for 1 leiOgrada point

    # Create the contract and define exchange parameters
    @arc4.abimethod(allow_actions=["NoOp"], create="require")
    def createApplication(
        self, lei_ograda_points: Asset, lei_laciaun_points: Asset, exchange_rate: UInt64
    ) -> None:
        self.lei_ograda_points_asset_id = lei_ograda_points.id
        self.lei_laciaun_points_asset_id = lei_laciaun_points.id
        self.exchange_rate = exchange_rate

    # Set the exchange rate
    @arc4.abimethod
    def setExchangeRate(self, new_rate: UInt64) -> None:
        assert Txn.sender == Global.creator_address
        self.exchange_rate = new_rate

    # Opt-in to leiOgrada and leiLaCiaun point assets
    @arc4.abimethod
    def optInToAssets(self, mbrPay: gtxn.PaymentTransaction) -> None:
        assert Txn.sender == Global.creator_address

        # Opt-in to leiOgrada points if not already
        if not Global.current_application_address.is_opted_in(
            Asset(self.lei_ograda_points_asset_id)
        ):
            assert mbrPay.receiver == Global.current_application_address
            assert mbrPay.amount == Global.min_balance + Global.asset_opt_in_min_balance
            itxn.AssetTransfer(
                xfer_asset=self.lei_ograda_points_asset_id,
                asset_receiver=Global.current_application_address,
                asset_amount=0,
            ).submit()

        # Opt-in to leiLaCiaun points if not already
        if not Global.current_application_address.is_opted_in(
            Asset(self.lei_laciaun_points_asset_id)
        ):
            assert mbrPay.receiver == Global.current_application_address
            assert mbrPay.amount == Global.min_balance + Global.asset_opt_in_min_balance
            itxn.AssetTransfer(
                xfer_asset=self.lei_laciaun_points_asset_id,
                asset_receiver=Global.current_application_address,
                asset_amount=0,
            ).submit()

    # Exchange leiOgrada points for leiLaCiaun points
    @arc4.abimethod
    def exchangePoints(
        self, ograda_transfer: gtxn.AssetTransferTransaction, quantity: UInt64
    ) -> None:
        # Fix comparison: Use 'id' for asset comparison
        assert ograda_transfer.xfer_asset.id == self.lei_ograda_points_asset_id
        assert ograda_transfer.asset_receiver == Global.current_application_address
        assert ograda_transfer.asset_amount == quantity

        laciaun_amount = quantity * self.exchange_rate

        # Check if there's enough leiLaCiaun points
        # Assume we need to access the application state or external state query to check balances
        # This would usually be done externally by reading the balance for the contract's account.

        itxn.AssetTransfer(
            xfer_asset=self.lei_laciaun_points_asset_id,
            asset_receiver=ograda_transfer.sender,
            asset_amount=laciaun_amount,
        ).submit()

    # Delete the application and reclaim assets
    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def deleteApplication(self) -> None:
        assert Txn.sender == Global.creator_address

        # Transfer remaining leiOgrada points to the creator
        itxn.AssetTransfer(
            xfer_asset=self.lei_ograda_points_asset_id,
            asset_receiver=Global.creator_address,
            asset_amount=0,  # Set to zero to close
            asset_close_to=Global.creator_address,
        ).submit()

        # Transfer remaining leiLaCiaun points to the creator
        itxn.AssetTransfer(
            xfer_asset=self.lei_laciaun_points_asset_id,
            asset_receiver=Global.creator_address,
            asset_amount=0,  # Set to zero to close
            asset_close_to=Global.creator_address,
        ).submit()

        # Close out any remaining balance
        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address,
        ).submit()
