import random
from typing import Dict

class X402Agent:
    """
    Mock implementation of the x402 tool for Fandango Gift Cards.
    """
    def __init__(self):
        print("Initializing x402 Secure Commerce Link...")

    def check_balance(self, card_number: str) -> Dict[str, float]:
        # Implementation of balance check
        return {"card": card_number, "balance": 0.00}

    def buy_gift_card(self, amount: float, email: str) -> Dict[str, str]:
        """
        Simulates buying a gift card.
        """
        transaction_id = f"tx_x402_{random.randint(10000, 99999)}"
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "provider": "Fandango",
            "amount": f"${amount}",
            "recipient": email,
            "message": "Gift card code sent via email."
        }

if __name__ == "__main__":
    agent = X402Agent()
    print(agent.buy_gift_card(25.0, "fan@example.com"))
