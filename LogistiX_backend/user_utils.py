import hashlib

def user_hash(user):
    d = f"{user.username}{user.date_joined}"
    h = hashlib.sha256(bytes(d, 'utf-8'))
    return(h.hexdigest())