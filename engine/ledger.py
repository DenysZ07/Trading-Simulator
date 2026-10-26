import hashlib
import json

# Place holder for the row before row 1 since there isnt one 
START_OF_CHAIN = bytes(32)


def serialise_trade(trade):
    payload = {
        "schema_version" : 1,
        "symbol": trade.symbol,
        "side": trade.side.value, 
        "quantity": trade.quantity,
        "fill_price": f"{trade.fill_price:.8f}",
        "commission": f"{trade.commission:.8f}",
        "slippage": f"{trade.slippage:.8f}",
        "spread": f"{trade.spread:.8f}",
        "cost_basis": f"{trade.cost_basis:.8f}" if trade.cost_basis is not None else None, 
        "timestamp": trade.timestamp,
    }

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def chain_digest(previous, payload):
    return hashlib.sha256(previous + payload).digest()