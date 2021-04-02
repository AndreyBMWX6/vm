from vm import StackMachine


if __name__ == '__main__':
    print("Running example.txt...")
    with open('example.txt', 'r') as f:
        code = f.read()
    sm = StackMachine(code)
    sm.run()
