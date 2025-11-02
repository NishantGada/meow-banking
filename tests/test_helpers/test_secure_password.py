from apis.helper_functions.secure_password import hash_password, verify_password


# def test_hash_password():
#     password = "testpass123"
#     hashed = hash_password(password)

#     assert hashed != password
#     assert len(hashed) > 0


# def test_verify_password_correct():
#     password = "testpass123"
#     hashed = hash_password(password)

#     assert verify_password(password, hashed) == True


# def test_verify_password_incorrect():
#     password = "testpass123"
#     wrong_password = "wrongpass"
#     hashed = hash_password(password)

#     assert verify_password(wrong_password, hashed) == False


class TestPasswordHashing:
    def setup_method(self):
        self.password = "testpass123"
        self.hashed = hash_password(self.password)

    def test_hash_not_equal_plain(self):
        assert self.hashed != self.password

    def test_verify_correct(self):
        assert verify_password(self.password, self.hashed) == True
    
    def test_verify_password_incorrect(self):
        self.wrong_password = "testpassword456"
        assert verify_password(self.wrong_password, self.hashed) == False
