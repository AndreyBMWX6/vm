from vm import StackMachine


if __name__ == '__main__':
    print('Running encryptor.txt...')
    with open('encryptor.txt', 'r') as f:
        code = f.read()
    sm = StackMachine(code)
    sm.run()
