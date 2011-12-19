#automatically generated by the proxygenerator
from clientproxyonerun import *

class Bank():
    def __init__(self, bootstrap):
        self.proxy = ClientProxy(bootstrap)

    def open(self, accntno):
        self.proxy.invoke_command("open", accntno)

    def getvalue(self):
        self.proxy.invoke_command("getvalue", )

    def close(self, accntno):
        self.proxy.invoke_command("close", accntno)

    def debit(self, accntno, amount):
        self.proxy.invoke_command("debit", accntno, amount)

    def deposit(self, accntno, amount):
        self.proxy.invoke_command("deposit", accntno, amount)

    def balance(self, accntno):
        self.proxy.invoke_command("balance", accntno)

    def __str__(self):
        self.proxy.invoke_command("__str__", )
