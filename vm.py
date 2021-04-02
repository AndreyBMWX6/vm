from stack import Stack
from io import StringIO
import tokenize
import sys
import random


def parse(text):
    tokens = tokenize.generate_tokens(StringIO(text).readline)
    comment = False
    for toknum, tokval, _, _, _ in tokens:
        if tokval == '':
            continue
        if toknum == 54 and tokval == '//':
            comment = True
            continue
        if toknum == tokenize.NEWLINE or toknum == tokenize.NL and comment:
            comment = False
            continue
        elif comment:
            continue
        if toknum == tokenize.NUMBER:
            yield int(tokval)
        elif toknum in [tokenize.NL, tokenize.NEWLINE, tokenize.INDENT]:
            pass
        else:
            yield tokval
    return text


class StackMachine:
    def __init__(self, text: str):
        self.__data_stack = Stack()
        self.__return_stack = Stack()
        self.__instruction_pointer = 0
        self.__code = list(parse(text))
        self.__operations = {
            "+": self.__add,
            "-": self.__sub,
            "*": self.__mul,
            "/": self.__div,
            "%": self.__mod,
            "==": self.__eq,
            "!=": self.__ne,
            "<": self.__lt,
            "<=": self.__le,
            ">": self.__gt,
            ">=": self.__ge,
            "ord": self.__ord,
            "chr": self.__chr,
            "sep": self.__sep,
            "uni": self.__uni,
            "encr": self.__encr,
            "decr": self.__decr,
            "cast_int": self.__cast_int,
            "cast_str": self.__cast_str,
            "drop": self.__drop,
            "dup": self.__dup,
            "if": self.__if_cond,
            "jmp": self.__jmp,
            "stack": self.__stack,
            "swap": self.__swap,
            "print": self.__print_,
            "println": self.__println,
            "read": self.__read,
            "call": self.__call,
            "return": self.__return_,
            "exit": self.__exit,
            "test": self.__test,
            "store": self.__store,
            "load": self.__load,
        }
        self.__vars = {}
        self.__key = random.randint(0, 1000)

    def __compile(self):
        procedures = {}
        call_addrs = {}
        while self.__code.count(':') and self.__code.count(';'):
            proc_id = self.__code.index(':')
            proc_end = self.__code.index(';')
            name = self.__code[proc_id + 1]
            proc = list(self.__code[proc_id + 2:proc_end])
            proc.append('return')
            procedures[name] = proc
            self.__code = list(self.__code[:proc_id] + self.__code[proc_end + 1:])

        for name, proc in procedures.items():
            for op in proc:
                if op in procedures:
                    op_id = list(proc).index(op)
                    procedures[name] = list(proc[:op_id + 1] + ['call'] + proc[op_id + 1:])
                    proc = list(proc[:op_id + 1] + ['call'] + proc[op_id + 1:])

        if self.__code[0] != 'test':
            self.__code.append('exit')

        for name, proc in procedures.items():
            addr = len(self.__code)
            self.__code.extend(proc)
            procedures[name] = addr

        in_main = True
        for op in self.__code:
            if op == 'exit':
                in_main = False
                continue
            if op in procedures and in_main:
                op_id = self.__code.index(op)

                for name, _ in procedures.items():
                    procedures[name] += 1
                self.__code = list(self.__code[:op_id] + [procedures[op], 'call'] + self.__code[op_id + 1:])

                if op not in call_addrs:
                    call_addrs[op] = list()
                call_addrs[op].append(op_id)

            elif op in procedures:
                op_id = self.__code.index(op)
                self.__code = list(self.__code[:op_id] + [procedures[op]] + self.__code[op_id + 1:])

                if op not in call_addrs:
                    call_addrs[op] = list()
                call_addrs[op].append(op_id)

        for op_name in call_addrs:
            for addr in call_addrs[op_name]:
                self.__code[addr] = procedures[op_name]
        print(f'Compilation result: {self.__code}\n')

    def run(self):
        self.__compile()
        while self.__instruction_pointer < len(self.__code):
            opcode = (self.__code[self.__instruction_pointer])
            self.__instruction_pointer += 1
            self.__execute(opcode)

    def __execute(self, op):
        if op in self.__operations:
            self.__operations[op]()
        elif isinstance(op, int):
            self.__data_stack.push(op)
        elif isinstance(op, str) and op[0] == op[-1] == '"':
            self.__data_stack.push(op[1:-1])
        else:
            raise RuntimeError('No such operation: ', op)

    def top(self):
        return self.__data_stack.top()

    def __push(self, value):
        self.__data_stack.push(value)

    def __pop(self):
        return self.__data_stack.pop()

    def __add(self):
        self.__push(self.__pop() + self.__pop())

    def __sub(self):
        last = self.__pop()
        self.__push(self.__pop() - last)

    def __mul(self):
        self.__push(self.__pop() * self.__pop())

    def __div(self):
        last = self.__pop()
        self.__push(self.__pop() / last)

    def __mod(self):
        last = self.__pop()
        self.__push(self.__pop() % last)

    def __eq(self):
        self.__push(self.__pop() == self.__pop())

    def __ne(self):
        self.__push(self.__pop() != self.__pop())

    def __lt(self):
        last = self.__pop()
        self.__push(self.__pop() < last)

    def __le(self):
        last = self.__pop()
        self.__push(self.__pop() <= last)

    def __gt(self):
        last = self.__pop()
        self.__push(self.__pop() > last)

    def __ge(self):
        last = self.__pop()
        self.__push(self.__pop() >= last)

    def __ord(self):
        char = self.__pop()
        if isinstance(char, str) and len(char) == 1:
            self.__push(ord(char))
        elif isinstance(char, str):
            raise ValueError('ord accepts only one symbol')
        else:
            raise ValueError('ord accepts char(one-symbol str)')

    def __chr(self):
        code = self.__pop()
        if isinstance(code, int) and code > 0:
            self.__push(chr(code))
        else:
            raise ValueError('chr accepts positive int')

    def __sep(self):
        word = self.__pop()
        word_size = len(word)
        if isinstance(word, str):
            for char in list(word):
                self.__push(char)
            self.__push(word_size)
        else:
            raise ValueError('sep accepts str')

    def __uni(self):
        word = ''
        word_size = self.__pop()
        for i in range(word_size):
            word += self.__pop()
        word = word[::-1]
        self.__push(word)

    def __encr(self):
        self.__sep()
        word_size = self.__pop()
        word = [0 for _ in range(word_size)]
        for i in reversed(range(word_size)):
            self.__ord()
            word[i] = self.__pop() + self.__key
        for char in word:
            self.__push(char)
            self.__chr()
        self.__push(word_size)
        self.__uni()

    def __decr(self):
        self.__sep()
        word_size = self.__pop()
        word = [0 for _ in range(word_size)]
        for i in reversed(range(word_size)):
            self.__ord()
            word[i] = self.__pop() - self.__key
        for char in word:
            self.__push(char)
            self.__chr()
        self.__push(word_size)
        self.__uni()

    def __cast_int(self):
        self.__push(int(self.__pop()))

    def __cast_str(self):
        self.__push(str(self.__pop()))

    def __drop(self):
        self.__pop()

    def __dup(self):
        self.__push(self.top())

    def __if_cond(self):
        condition = self.__pop()
        false_clause = self.__pop()
        true_clause = self.__pop()
        self.__push(true_clause if condition else false_clause)

    def __jmp(self):
        addr = self.__pop()
        if isinstance(addr, int) and 0 <= addr < len(self.__code):
            self.__instruction_pointer = addr
        else:
            raise ValueError('jmp address should be non-negative integer')

    def __stack(self):
        print('Data stack:', end='')
        print(' Empty') if self.__data_stack.empty() else print()
        for el in self.__data_stack:
            print(f" - type {type(el)}, value '{el}'")
        print(f'Instruction pointer: {self.__instruction_pointer}')
        print('Return stack:', end='')
        print(' Empty\n') if self.__return_stack.empty() else print('\n')
        for el in self.__return_stack:
            print(f" - type {type(el)}, value '{el}'")

    def __swap(self):
        self.__data_stack[-1], self.__data_stack[-2] = self.__data_stack[-2], self.__data_stack[-1]

    def __print_(self):
        print(self.__pop(), end=' ')

    def __println(self):
        print(self.__pop())

    def __read(self):
        self.__push(self.__get_input())

    def __get_input(self):
        return input()

    def __call(self):
        self.__return_stack.push(self.__instruction_pointer)
        self.__jmp()

    def __return_(self):
        self.__instruction_pointer = self.__return_stack.pop()

    def __exit(self):
        sys.exit(0)

    def __test(self):
        pass

    def __store(self):
        name = self.__pop()
        value = self.__pop()
        self.__vars[name] = value

    def __load(self):
        self.__push(self.__vars[self.__pop()])
