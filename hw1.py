class SyntaxAnalyzer:
    def __init__(self):
        # Problem 0 about parsing table
        # left side: (state, input), right side: 'action + state/rule' or 'state' for goto
        self.parsing_table = {
            (0, 'N'): 'Shift 11',
            (0, 'E'): '1', # Goto 1 if state 0 & non-terminal E
            (0, 'T'): '2', # Goto 2 if state 0 & non-terminal T
            (1, '+'): 'Shift 3',
            (1, '-'): 'Shift 4',
            (1, '$'): 'Accept',
            (2, '+'): 'Reduce 3',
            (2, '-'): 'Reduce 3',
            (2, '*'): 'Shift 5',
            (2, '/'): 'Shift 8',
            (2, '$'): 'Reduce 3',
            (3, 'N'): 'Shift 11',
            (3, 'T'): '7', # Goto 7 if state 3 & non-terminal T
            (4, 'N'): 'Shift 11',
            (4, 'T'): '6', # Goto 6 if state 4 & non-terminal T
            (5, 'N'): 'Shift 9',
            (6, '+'): 'Reduce 2',
            (6, '-'): 'Reduce 2',
            (6, '*'): 'Shift 5',
            (6, '/'): 'Shift 8',
            (6, '$'): 'Reduce 2',
            (7, '+'): 'Reduce 1',
            (7, '-'): 'Reduce 1',
            (7, '*'): 'Shift 5',
            (7, '/'): 'Shift 8',
            (7, '$'): 'Reduce 1',
            (8, 'N'): 'Shift 10',
            (9, '+'): 'Reduce 4',
            (9, '-'): 'Reduce 4',
            (9, '*'): 'Reduce 4',
            (9, '/'): 'Reduce 4',
            (9, '$'): 'Reduce 4',
            (10, '+'): 'Reduce 5',
            (10, '-'): 'Reduce 5',
            (10, '*'): 'Reduce 5',
            (10, '/'): 'Reduce 5',
            (10, '$'): 'Reduce 5',
            (11, '+'): 'Reduce 6',
            (11, '-'): 'Reduce 6',
            (11, '*'): 'Reduce 6',
            (11, '/'): 'Reduce 6',
            (11, '$'): 'Reduce 6',
        }
        self.operators = {'+': lambda x, y: x + y, '-': lambda x, y: x - y, '*': lambda x, y: x * y, '/': lambda x, y: x / y} # used for calculating operations for Problem 2
        self.reduce_idx = {'1': ('E', 6), '2': ('E', 6), '3': ('E', 2), '4': ('T', 6), '5': ('T', 6), '6': ('T', 2)} # used for reduction in Problem 2. 'rule#': ('non-terminal', next state)
        self.index = 0 # used in Problem 3

# Problem 1
    def lexer(self, expression):
        # function to tokenize the input expression
        lexemes = [] # store lexemes
        tokens = [] # store tokens
        current_lexeme = "" # a variable to accumulate digits to form operands
        for char in expression:
            if char.isdigit(): # if it is a digit (= part of operand)
                current_lexeme += char
            else: # if it is operator
                if current_lexeme: # if there is operand
                    lexemes.append(int(current_lexeme)) # store the value in lexemes
                    tokens.append('N') # store N to represent a number
                    current_lexeme = ""
                if char in ['+', '-', '*', '/']: # when it is operator, store it in lexemes and tokens, respectively
                    lexemes.append(char)
                    tokens.append(char)
                else:
                    raise ValueError("Invalid character in expression: {}".format(char)) # exception handling for invalid input
        if current_lexeme: # for last operand in expression
            lexemes.append(int(current_lexeme))
            tokens.append('N')
        lexemes.append('$') # add last symbol as end sign
        tokens.append('$')
        return lexemes, tokens
    
# Problem 2
    def LRparser(self, input):
        # parser function for LR parsing
        lexemes, tokens = input
        stack = [0] # store elements in stack during parsing
        lex_stack = [0] # store lexeme values during parsing (for calculating operations later)
        input_idx = 0 # index to track current input token
        result = None # store final result of parsing
        count = 0 # counter for tracing parsing steps
        
        # exception handling for empty input lists
        if(len(str(lexemes)) == 0 or len(str(tokens)) == 0):
            raise Exception("No lexemes or tokens provided")
        
        # print tracing header
        print("\nTracing Start!!")
        print("+------+--------------+---------------+----------------+--------------------+")
        print("|      |            STACK             |     INPUT    |         ACTION       |")
        print("+------+--------------+---------------+----------------+--------------------+")

        # main parsing loop
        while True:
            top_of_stack = stack[-1]
            current_token = tokens[input_idx]
            current_lexemes = lexemes[input_idx]

            action = self.parsing_table.get((top_of_stack, current_token)) # get the action of corresponding state and input

            state = None
            action_str = None
            goto = None

            # exception handling if it is no acceptable expression to be defined using the BNF grammar
            if action is None:
                raise ValueError("Invalid action at position {}: {} {}".format(input_idx, top_of_stack, current_token))

            stack_str = "| ({:02d}) |".format(count) # number of steps
            # stack information
            if(input_idx == 0): # initial stack state
                stack_str += "0".ljust(30) + "|"
            else:
                stack_str += ' '.join([str(item) for item in stack[:-1]]) + f" {top_of_stack} "
                stack_str += " " * (38 - len(str(stack_str))) + "|"
            # input information
            stack_str += " {} ".format(''.join([str(token) for token in tokens[input_idx:]])).rjust(14) + "| "

            # action information: handle different types of actions
            if action.startswith('Shift'): # when it is shift
                state = int(action.split()[1]) # only need state info
                action_str = action.rjust(21)
            elif action.startswith('Reduce'): # when it is reduce
                state = int(action.split()[1]) # rule number
                idx = -(int(self.reduce_idx[str(state)][1]) + 1) # index for stack where reduce rule to be implemented
                goto = f"{stack[idx]} {self.reduce_idx[f'{state}'][0]}" # store goto information
                action_str = f"Reduce {state} (Goto[{stack[idx]}, {goto.split()[1]}])".rjust(20)
            elif action.startswith('Accept'): # when the expression is accepted
                action_str = "Accept".rjust(21)
            else: # otherwise, exception handling for invalid action
                raise Exception("Invalid action")
            action_str += "|"

            # print the current stack and input states, and action
            print(stack_str + action_str)

            # calculation and progress of parsing
            if action == 'Accept': # end of parsing, check for acceptance
                break
            elif action.startswith('Shift'): # move to next corresponding state
                state = int(action.split()[1]) # get the state to move to
                stack.append(current_token)
                lex_stack.append(current_lexemes)
                stack.append(state)
                input_idx += 1
            else: # handle reduce action
                key = int(action[7:])
                non_terminal, reduce = self.reduce_idx[str(key)]
                if(key in [3, 6]): # handle reductions regarding a single token without operators
                    for a in range(reduce): # reduce corresponding tokens in stack
                        stack.pop()
                    result = lex_stack[1] # store the value for result
                elif (key in [1, 2, 4, 5]): # handle reductions regarding operators
                    popped_items = []
                    for a in range(reduce): # reduce corresponding tokens in stack
                        stack.pop()
                        if(a < reduce / 2): # store popped lexemes for calculation
                            popped_items.append(lex_stack.pop())
                    popped_items.reverse()
                    if non_terminal in ['E', 'T']: # for E or T
                        operand2 = int(popped_items.pop())
                        operator = popped_items.pop()
                        operand1 = int(popped_items.pop())
                        result = self.operators[operator](operand1, operand2) # calculate following the matched operator
                        lex_stack.append(result) # store the result in lexemes stack
                # store info for stack
                stack.append(goto.split()[1])
                stack.append(int(self.parsing_table[(int(goto.split()[0]), goto.split()[1])]))
            count += 1 # increment counter

        return result # return calculated result during parsing

# Problem 3
    def LLparser(self, input):
        # parser function for LL parsing
        lexemes, tokens = input
        self.index = 0 # initialize index to track current token position

        #print start of parsing
        print("\nStart!!")

        # exception handling when empty input expression provided
        # when lexemes or tokens only have '$' (length of their string version is 5 since it's ['$'])
        if(len(str(lexemes)) == 5 or len(str(tokens)) == 5):
            raise Exception("No lexemes or tokens provided")
        
        result = self.E(lexemes, tokens) # start parsing expression with 'E' non-terminal since it is the first rule
        return result # final result of accumulated calculations in the progress of parsing

    # functions below represent BNF grammar rules with right recursion
    """
    Right Recursion:
    E → TE'
    E' → +TE' | -TE' | ε
    T → NT'
    T' → *NT' | /NT' | ε
    """

    def E(self, lexemes, tokens):
        print("enter E") # entry to E
        result = self.T(lexemes, tokens) # parse T
        result = self.E_prime(lexemes, tokens, result) # parse E'
        print("exit E") # exit from E
        return result

    def E_prime(self, lexemes, tokens, result):
        print("enter E'") # entry to E'
        if self.index < len(tokens) and tokens[self.index] in ['+', '-']: # check for '+' or '-' operator
            op = tokens[self.index] # take the operator
            self.index += 1
            temp = self.T(lexemes, tokens) # parse T
            if op == '+': # perform calculation
                result += temp
            else:
                result -= temp
            result = self.E_prime(lexemes, tokens, result) # parse next E'
        else:
            print("epsilon") # print for empty production grammar
        print("exit E'") # exit from E'
        return result

    def T(self, lexemes, tokens):
        print("enter T") # entry to T
        result = self.N(lexemes, tokens) # parse N
        result = self.T_prime(lexemes, tokens, result) # parse T'
        print("exit T") # exit from T
        return result

    def T_prime(self, lexemes, tokens, result):
        print("enter T'") # entry to T'
        if self.index < len(tokens) and tokens[self.index] in ['*', '/']: # check for '*' or '/' operator
            op = tokens[self.index] # take the operator
            self.index += 1
            temp = self.N(lexemes, tokens) # parse N
            if op == '*': # perform calculation
                result *= temp
            else:
                result /= temp
            result = self.T_prime(lexemes, tokens, result) # parse next T'
        else:
            print("epsilon") # print for empty production grammar
        print("exit T'") # exit from T'
        return result

    def N(self, lexemes, tokens):
        if tokens[self.index] == 'N': # check if current token is a number
            result = lexemes[self.index] # get the corresponding lexeme value
            self.index += 1 # move to next token
            return result
        else: # exception handling for syntax error in N
            raise ValueError("Syntax error in N")


# Test cases for Problem 1 & 2
# test case 1: original
S = SyntaxAnalyzer()
lexemes, tokens = S.lexer("100-12/12")
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))

result = S.LRparser((lexemes, tokens))
print("Result:" + str(result))
print("\n")

# test case 2: complex
lexemes, tokens = S.lexer("900*2-20+30-100/10")
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))

result = S.LRparser((lexemes, tokens))
print("Result:" + str(result))
print("\n")

# test case 3: single integer
lexemes, tokens = S.lexer("900")
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))

result = S.LRparser((lexemes, tokens))
print("Result:" + str(result))
print("\n")

# Test cases to show exception handling. Uncomment them to test
"""
# test case 4: unacceptable expression
lexemes, tokens = S.lexer("-10+90")
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))

result = S.LRparser((lexemes, tokens)) # exception handling occurs in Problem 2
print("Result:" + str(result))

# test case 5: invalid lexeme & token
lexemes, tokens = S.lexer("30/(900+2)") # exception handling occurs in Problem 1
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))

result = S.LRparser((lexemes, tokens))
print("Result:" + str(result))
"""


# Test cases for Problem 3
# test case 1: original
lexemes, tokens = S.lexer("100*12")
result = S.LLparser((lexemes, tokens))
print("Result:" + str(result))

# test case 2: complex
lexemes, tokens = S.lexer("900*2-20+30")
result = S.LLparser((lexemes, tokens))
print("Result:" + str(result))

# test case 3: single integer
lexemes, tokens = S.lexer("300")
result = S.LLparser((lexemes, tokens))
print("Result:" + str(result))

# Test cases to show exception handling. Uncomment them to test
"""
# test case 4: unacceptable expression
lexemes, tokens = S.lexer("-30+50")
result = S.LLparser((lexemes, tokens))
print("Result:" + str(result))

# test case 5: no input
lexemes, tokens = S.lexer("")
result = S.LLparser((lexemes, tokens))
print("Result:" + str(result))
"""