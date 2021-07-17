from random import randint
import sqlite3


class BankingSystem:
    def __init__(self):
        self.id = 0
        self.IIN = "400000"
        self.acc_num = None
        self.checksum = None
        self.card_num = None
        self.pin = None
        self.balance = None
        self.conn = None
        self.cur = None
        self.setup_db()
        self.print_menu()

    def setup_db(self):
        self.conn = sqlite3.connect('card.s3db')
        try:
            self.cur = self.conn.cursor()
            self.cur.execute("""CREATE TABLE card (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    number TEXT,
                                    pin TEXT,
                                    balance INTEGER DEFAULT 0
                                    );
                                    """)
            self.conn.commit()
        except sqlite3.OperationalError:
            self.cur.execute("DELETE FROM card")
            self.conn.commit()

    def print_menu(self):
        while True:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
            result = int(input())
            print()

            if result == 1:
                self.create_account()
            elif result == 2:
                self.log_in()
            elif result == 0:
                print("Bye!")
                exit()

            print()

    def create_account(self):
        self.balance = 0
        self.generate_card_num()
        self.generate_pin()
        print("Your card has been created")
        print("Your card number:")
        print(self.card_num)
        print("Your card PIN:")
        print(self.pin)
        self.save_to_db()

    def save_to_db(self):
        self.cur.execute(f"INSERT INTO card (number, pin, balance) VALUES ({self.card_num}, {self.pin}, {self.balance})")
        self.conn.commit()

    def generate_card_num(self):
        acc_num = str(randint(0, 999999999))
        self.acc_num = "0" * (9 - len(acc_num)) + acc_num
        self.calc_checksum()
        self.card_num = self.IIN + self.acc_num + self.checksum

    def calc_checksum(self):
        nums_list = list(map(int, list(self.IIN + self.acc_num)))

        double_odds = [num * 2 if i % 2 == 0 else num for i, num in enumerate(nums_list)]

        sub_9 = [num - 9 if num > 9 else num for num in double_odds]

        summed = sum(sub_9)

        self.checksum = str(10 - summed % 10) if summed % 10 != 0 else "0"

    def generate_pin(self):
        pin = str(randint(0, 9999))
        self.pin = "0" * (4 - len(pin)) + pin

    def log_in(self):
        print("Enter your card number:")
        card_num = input()
        print("Enter your PIN:")
        pin = input()
        print()

        result = self.query_db(card_num, pin)

        if result is not None:
            print("You have successfully logged in!", end="\n\n")

            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                res = int(input())
                print()

                result = self.query_db(card_num, pin)

                if res == 1:
                    print(f"Balance: {result[3]}")
                elif res == 2:
                    self.add_income(result)
                elif res == 3:
                    self.do_transfer(result)
                elif res == 4:
                    self.close_account(result)
                    return
                elif res == 5:
                    print("You have successfully logged out!")
                    return
                elif res == 0:
                    print("Bye!")
                    exit()

                print()
        else:
            print("Wrong card number or PIN!")

    def query_db(self, card_num, pin_num):
        self.cur.execute(f"SELECT id, number, pin, balance FROM card WHERE number = {card_num} AND pin = {pin_num};")
        return self.cur.fetchone()

    def add_income(self, result):
        print("Enter income:")
        income = int(input())

        self.cur.execute(f"UPDATE card SET balance = {result[3] + income} WHERE id = {result[0]};")
        self.conn.commit()

        print("Income was added!")

    def do_transfer(self, result):
        print("Transfer")
        print("Enter card number:")
        card_num = input()

        self.cur.execute(f"SELECT id, number, balance FROM card WHERE number = {card_num};")
        receiver_account = self.cur.fetchone()

        if card_num == result[1]:
            print("You can't transfer money to the same account!")
            return
        elif not self.check_integrity(card_num):
            print("Probably you made a mistake in the card number. Please try again!")
            return
        elif receiver_account is None:
            print("Such a card does not exist.")
            return

        print("Enter how much money you want to transfer:")
        amount = int(input())

        if amount > result[-1]:
            print("Not enough money!")
            return

        self.cur.execute(f"UPDATE card SET balance = {receiver_account[-1] + amount} WHERE id = {receiver_account[0]};")
        self.cur.execute(f"UPDATE card SET balance = {result[-1] - amount} WHERE id = {result[0]};")
        self.conn.commit()

    @staticmethod
    def check_integrity(card_num):
        nums_list = list(map(int, list(card_num[:-1])))

        double_odds = [num * 2 if i % 2 == 0 else num for i, num in enumerate(nums_list)]

        sub_9 = [num - 9 if num > 9 else num for num in double_odds]

        summed = sum(sub_9)

        checksum = str(10 - summed % 10) if summed % 10 != 0 else "0"

        return checksum == card_num[-1]

    def close_account(self, result):
        self.cur.execute(f"DELETE FROM card WHERE id = {result[0]}")
        self.conn.commit()
        print("The account has been closed!")


bank = BankingSystem()
