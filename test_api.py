from models import XRate


def update_xrates(from_currency, to_currency):
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()

    print("rate before:", xrate)
    xrate.rate += 0.01
    xrate.save()

    print("rate after:", xrate)
