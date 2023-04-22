from pyteal import *
from beaker import *
import typing


class AuctionState:
    # GlobalState
    owner = GlobalStateValue(
        stack_type=TealType.bytes,
        default=Global.creator_address()
    )
    winner = GlobalStateValue(
        stack_type=TealType.bytes,
        default=Bytes("")
    )
    best_bid = GlobalStateValue(
        stack_type=TealType.uint64,
        default=Int(0)
    )
    auction_end = GlobalStateValue(
        stack_type=TealType.uint64,
        default=Int(0)
    )

    account_bid = LocalStateValue(
        stack_type=TealType.uint64,
        default=Int(0)
    )


auction_app = Application("Auction", state=AuctionState())


@auction_app.create
def create():
    return auction_app.initialize_global_state()


def pay(receiver: Expr, amount: Expr):
    return InnerTxnBuilder.Execute(
        {
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: receiver,
            TxnField.amount: amount,
            TxnField.fee: Int(0),
        }
    )


@auction_app.external(authorize=Authorize.only_creator())
def start_auction(payment: abi.PaymentTransaction, length: abi.Uint64):
    payment = payment.get()

    return Seq(
        # verifico la transasazione di Pagamento
        Assert(payment.receiver() == Global.current_application_address()),
        Assert(payment.amount() == Int(0)),
        # Setto il GlobalState
        auction_app.state.auction_end.set(Global.latest_timestamp() + length.get()),
    )


@auction_app.external
def bid(payment: abi.PaymentTransaction):
    payment = payment.get()
    best_bid = auction_app.state.best_bid
    winner = auction_app.state.winner
    auction_end = auction_app.state.auction_end

    return Seq(
        Assert(Global.latest_timestamp() < auction_end),

        Assert(Txn.sender() == payment.sender()),

        If(
            winner != Bytes(""),
            Seq(
                Assert(payment.amount() <= best_bid)
            ),
        ),
        auction_app.state.winner.set(payment.sender()),
        auction_app.state.best_bid.set(payment.amount()),
    )


@auction_app.external
def end_auction():
    auction_end = auction_app.state.auction_end.get()

    winner = auction_app.state.best_bid.get()

    return Seq(
        Assert(Global.latest_timestamp() > auction_end),
        auction_app.state.owner.set(winner),
        auction_app.state.auction_end.set_default(),
        auction_app.state.winner.set_default(),
    )


def demo():
    app_client = client.ApplicationClient(
        sandbox.get_algod_client(),
        auction_app,
        signer=sandbox.get_accounts().pop().signer,
    )
    app_client.create()


if __name__ == "__main__":
    demo()
