from api.oanda_api import OandaApi
import constants.defs as defs
from infrastructure.instrument_collection import instrumentCollection as ic
import math

# sensible minimum stop distances
MIN_LOSS_NON_JPY = 0.0005   # ~5 pips
MIN_LOSS_JPY     = 0.05     # ~5 pips

MAX_UNITS = 1_000       # safety cap (adjust if needed)


def get_trade_units(api, pair, signal, loss, trade_risk, log_message):

    if loss is None or loss <= 0:
        log_message("Invalid loss — cannot size trade", pair)
        return None

    pipLocation = ic.instruments_dict[pair].pipLocation

    min_loss = 0.05 if "JPY" in pair else 0.0005
    # prevent trades with very small/0 losses
    if loss < min_loss:
        log_message(f"Loss {loss} too small → clamped to {min_loss}", pair)
        loss = min_loss

    prices = api.get_prices([pair])
    if not prices:
        return None

    price = next(p for p in prices if p.instrument == pair)

    conv = price.sell_conv if signal == defs.SELL else price.buy_conv

    num_pips = loss / pipLocation
    risk_per_pip = trade_risk / num_pips

    units = risk_per_pip / (conv * pipLocation)

    log_message(
        f"loss={loss:.1f} pips={num_pips:.1f} units={units:.1f}",
        pair
    )

    return units