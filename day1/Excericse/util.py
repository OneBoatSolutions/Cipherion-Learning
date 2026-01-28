#-------------------HASH--------------
def simple_hash(password):
    hash_value = 0
    prime = 31
    for char in password:
        hash_value = (hash_value * prime + ord(char)) % 100000
    return str(hash_value)