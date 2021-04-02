class Stack:
    def __init__(self):
        self.__items = list()

    def __getitem__(self, item):
        return self.__items[item]

    def __iter__(self):
        return self.__items.__iter__()

    def empty(self):
        return len(self.__items) == 0

    def size(self):
        return len(self.__items)

    def top(self):
        return self.__items[-1]

    def push(self, value):
        self.__items.append(value)

    def pop(self):
        return self.__items.pop()
