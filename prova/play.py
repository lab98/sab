from beaker import *
from pyteal import *


class AuctionState:
    owner = GlobalStateValue(
        stack_type=TealType.bytes, default=Global.creator_address()
    )
    winner = GlobalStateValue(stack_type=TealType.bytes, default=Bytes(""))
    best_bid = GlobalStateValue(stack_type=TealType.uint64, default=Int(0))
    auction_end = GlobalStateValue(stack_type=TealType.uint64, default=Int(0))


app = Application(name="ReverseAuction", state=AuctionState())


@app.create(authorize=Authorize.only_creator())
def create() -> Expr:
    app.initialize_global_state()
    return Seq()


@app.external(authorize=Authorize.only_creator())
def auction_start(duration: abi.Uint64) -> Expr:
    return Seq(app.state.auction_end.set(Global.latest_timestamp() + duration.get()))


@app.external
def bid(bidder: abi.Address, bid: abi.Uint64) -> Expr:
    auction_end = app.state.auction_end.get()
    best_bid = app.state.best_bid.get()
    return Seq(
        Assert(Global.latest_timestamp() < auction_end),
        If(Eq(best_bid, Int(0)))
        .Then(app.state.winner.set(bidder.get()), app.state.best_bid.set(bid.get()))
        .ElseIf(Gt(best_bid, bid.get()))
        .Then(app.state.winner.set(bidder.get()), app.state.best_bid.set(bid.get())),
    )


@app.external(authorize=Authorize.only_creator())
def auction_end() -> Expr:
    auction_end = app.state.auction_end.get()
    return Seq(
        Assert(Global.latest_timestamp() < auction_end),
        app.state.best_bid.set_default(),
        app.state.winner.set_default(),
        app.state.auction_end.set_default(),
    )


if __name__ == "__main__":
    app.build().export("./artifacts")
