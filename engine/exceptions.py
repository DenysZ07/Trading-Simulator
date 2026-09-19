class OrderRejected(Exception):
    """Raised when an order cannot be filled. Either because insufficient cash or insufficient shares."""