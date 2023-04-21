import beaker as bk
import pyteal as pt
from beaker import *
from beaker.client import ApplicationClient
from pyteal import *

calculator_app = bk.Application("Calculator")


@calculator_app.external
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Add a and b, return the result"""
    return output.set(a.get() + b.get())


@calculator_app.external
def mul(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Multiply a and b, return the result"""
    return output.set(a.get() * b.get())


@calculator_app.external
def sub(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Subtract b from a, return the result"""
    return output.set(a.get() - b.get())


@calculator_app.external
def div(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Divide a by b, return the result"""
    return output.set(a.get() / b.get())


def demo() -> None:
    # Here we use `sandbox` but beaker.client.api_providers can also be used
    # with something like ``AlgoNode(Network.TestNet).algod()``
    algod_client = sandbox.get_algod_client()

    acct = sandbox.get_accounts().pop()

    # Create an Application client containing both an algod client and app
    app_client = ApplicationClient(
        client=algod_client, app=calculator_app, signer=acct.signer
    )

    # Create the application on chain, implicitly sets the app id for the app client
    app_id, app_addr, txid = app_client.create()
    print(f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid}")

    result = app_client.call(add, a=2, b=2)
    print(f"add result: {result.return_value}")


if __name__ == "__main__":
    demo()
