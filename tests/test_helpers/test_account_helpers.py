from apis.helper_functions.account_helpers import generate_account_number


class TestGenerateAccountNumber:
    def setup_method(self):
        self.test_account_number = generate_account_number()

    def test_account_number_length(self):
        assert len(self.test_account_number) == 10

    def test_account_number_is_digits(self):
        assert self.test_account_number.isdigit()

    def test_account_number_uniqueness(self):
        self.new_account_number = generate_account_number()
        assert self.test_account_number != self.new_account_number
