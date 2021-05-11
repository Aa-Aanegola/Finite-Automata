import sys
import json

ALLOWED = "0123456789qwertyuiopasdfghjklzxcvbnm*.+()$"
OPS = "*.+()"
PRIORITY = {'*' : 2, '.' : 1, '+' : 0}
INVALID_REGEX = -1
VALID_REGEX = 0


class State:
    id = 0
    def __init__(self):
        self.id = State.id
        self.name = ""
        State.id += 1
        self.transitions = []
        
    def addTransition(self, node, alph):
        self.transitions.append((node, alph))

class NFA:
    def __init__(self):
        self.states = []
        self.start = None
        self.accept = []
        self.alphabet = []
    
    def getAlph(self, regex):
        for c in regex:
            if c not in OPS and c not in self.alphabet:
                self.alphabet.append(c)
    
    def getStart(self):
        return self.start
    
    def getAccept(self):
        return self.accept
    
    def addState(self, s):
        self.states.append(s)
    
    def addTransition(self, s1, s2, a):
        s1.addTransition(s2, a)
    
    def makeStart(self, s):
        self.start = s
    
    def makeAccept(self, s):
        self.accept.append(s)

    def removeAccept(self, s):
        self.accept.remove(s)

    def names(self):
        c = 0
        self.start.name = f"q{c}"
        c += 1
        states = []
        states.append(self.start)
        while len(states) != 0:
            cur = states[0]
            states.pop(0)
            for state, alph in cur.transitions:
                if len(state.name) == 0:
                    state.name = f"q{c}"
                    c += 1
                    states.append(state)
    
    def printTuple(self, path):
        js = {}
        js['states'] = []
        for state in self.states:
            js['states'].append(state.name)
        js['letters'] = self.alphabet
        js['transition_function'] = []
        for state in self.states:
            for trans in state.transitions:
                node, alph = trans
                js['transition_function'].append([state.name, alph, node.name])

        js['start_states'] = [self.start.name]
        js['final_states'] = []
        for state in self.accept:
            js['final_states'].append(state.name)
        
        f = open(path, "w+")
        json.dump(js, f, indent=4)
        
def concat(N1, N2):
    N = NFA()
    for state in N1.states:
        N.addState(state)
        if N1.getStart() == state:
            N.makeStart(state)
            
    for state in N2.states:
        N.addState(state)
        if state in N2.getAccept():
            N.makeAccept(state)
    N.addTransition(N1.accept[0], N2.start, '$')

    return N


def union(N1, N2):
    N = NFA()
    
    newStart = State()
    newAccept = State()
    N.addState(newStart)
    N.addState(newAccept)
    N.makeStart(newStart)
    N.makeAccept(newAccept)
    
    for state in N1.states:
        N.addState(state)
        if N1.getStart() == state:
            N.addTransition(newStart, state, '$')
        if state in N1.getAccept():
            N.addTransition(state, newAccept, '$')
    for state in N2.states:
        N.addState(state)
        if N2.getStart() == state:
            N.addTransition(newStart, state, '$')
        if state in N2.getAccept():
            N.addTransition(state, newAccept, '$')

    return N


def kleen(N):
    
    newStart = State()
    newAccept = State()
    N.addState(newStart)
    N.addState(newAccept)
    
    N.addTransition(newStart, N.start, '$')
    N.addTransition(newStart, newAccept, '$')
    N.addTransition(N.accept[0], newAccept, '$')
    N.addTransition(N.accept[0], N.start, '$')
    N.removeAccept(N.accept[0])
    N.makeStart(newStart)
    N.makeAccept(newAccept)
    return N

def addConcat(regex):
    newRegex = '('
    for i in range(len(regex)-1):
        newRegex += regex[i]
        if regex[i] not in OPS and regex[i+1] not in OPS:
            newRegex += '.'
        elif regex[i] not in OPS and regex[i+1] == '(':
            newRegex += '.'
        elif regex[i] == ')' and regex[i+1] == '(':
            newRegex += '.'
        elif regex[i] == ")" and regex[i+1] not in OPS:
            newRegex += '.'
        elif regex[i] == "*" and regex[i+1] not in '+*)':
            newRegex += '.'
    newRegex += regex[-1]
    newRegex += ')'
    return newRegex

def parseRegEx(regEx, postfix):
    regEx.replace(' ', '')
    for a in regEx:
        if a not in ALLOWED:
            return INVALID_REGEX
    
    postfix.clear()
    stack = []
    for a in regEx:
        if a not in OPS:
            postfix.append(a)
        elif a == '(':
            stack.append('(')
        elif a == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop());
            stack.pop();
        else:
            while stack and stack[-1] != '(' and PRIORITY[a] <= PRIORITY[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(a)
    while stack:
        postfix.append(stack.pop())
    return VALID_REGEX


def readJSON(path):
    f = open(path, "r")
    data = json.load(f)
    regex = data['regex']
    
    return regex

def main():
    if len(sys.argv) != 3:
        exit()
    
   

    regEx = readJSON(sys.argv[1])
    regEx = addConcat(regEx)
    postfix = []
    res = parseRegEx(regEx, postfix)

    
    if res == INVALID_REGEX:
        print("Invalid regular expression, terminating.")
        exit()


    stackNFA = []
    
    for a in postfix:
        if a not in OPS:
            newNFA = NFA()
            q0 = State()
            q1 = State()
            newNFA.addState(q0)
            newNFA.addState(q1)
            newNFA.makeStart(q0)
            newNFA.makeAccept(q1)
            newNFA.addTransition(q0, q1, a)
            stackNFA.append(newNFA)
            
        elif a == '.':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            N = concat(N1, N2)
            stackNFA.append(N)
        elif a == '+':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            N = union(N1, N2)
            stackNFA.append(N)
        elif a == '*':
            N = stackNFA.pop()
            N = kleen(N)
            stackNFA.append(N)
    
    N = stackNFA[0]
    N.getAlph(regEx)
    N.names()
    N.printTuple(sys.argv[2])
    
if __name__ == "__main__":
    main()
