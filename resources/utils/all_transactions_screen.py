from collections import defaultdict
import json


def mixed_investment_data(investments):
    transactions = []

    for investment in investments:
        investment_id = investment['id']
        stockName = investment['name']
        transaction_price = investment['price']
        kind = investment['kind']
        amount = investment['amount']
        date = investment['createdAt']

        investment_dict = {
            "id": str(investment_id),
            "name": stockName,
            "price": transaction_price,
            "kind": kind,
            "amount": amount,
            "date": str(date)
        }

        transactions.append(investment_dict)

    result = {
        "result": transactions
    }

    return result
