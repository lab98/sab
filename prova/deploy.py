from beaker import client, sandbox

from play import *

app.build().export("./artifacts")

accounts = sandbox.get_accounts()

print(f"Vi sono un totale di {len(accounts)} accounts")

creator = accounts.pop()


app_client = client.ApplicationClient(
    client=sandbox.get_algod_client(),
    app=app,
    sender=creator.address,
    signer=creator.signer,
)

app_client.create()
print(f"Creata dApp \n addr : {app_client.app_addr} \n ID : {app_client.app_id} ")


app_client.call(auction_start, duration=100_000)

first_bidder = accounts.pop()
first_bid = 15000

sp = app_client.get_suggested_params()


app_client.call(bid, bidder=first_bidder.address, bid=first_bid)
print(f"Prima offerta effettuata da {first_bidder.address} di {first_bid} microAlgos\n")
print(f"{app_client.get_global_state()} \n")

second_bidder = accounts.pop()
second_bid = 10000

app_client.call(bid, bidder=second_bidder.address, bid=second_bid)
print(
    f"Seconda offerta effettuata da {second_bidder.address} di {second_bid} microAlgos\n"
)
print(f"{app_client.get_global_state()} \n")
app_client.call(auction_end)
print(f"{app_client.get_global_state()} \n")
