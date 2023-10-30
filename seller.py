class seller_hist:
    def __init__(self, seller, warehouse, product):
        self.seller = seller
        self.warehouse = warehouse
        self.product = product
        self.history = []
        # History will be a list of 2 element tuple: (date, quantity)
        self.prediction = None
    def get_seller(self):
        return self.seller
    def get_history(self):
        return self.history
    def add_history(self, date, quantity):
        self.history.append((date, quantity))