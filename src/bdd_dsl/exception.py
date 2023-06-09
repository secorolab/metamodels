class ConstraintViolation(Exception):
    def __init__(self, domain, message):
        super().__init__(f"{domain} constraint: {message}")


class BDDConstraintViolation(ConstraintViolation):
    def __init__(self, message):
        super().__init__("BDD", message)
