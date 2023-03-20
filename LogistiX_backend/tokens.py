from django.contrib.auth.tokens import PasswordResetTokenGenerator
import hashlib

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        m = hashlib.sha512()
        msg = str(user.pk) + str(user.username) + str(timestamp) + str(user.is_active)
        m.update(msg.encode('utf-8'))
        hexhash = m.hexdigest()
        return hexhash

account_activation_token_gen = AccountActivationTokenGenerator()