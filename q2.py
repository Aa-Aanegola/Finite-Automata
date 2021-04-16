import json
import sys


def readNFA(path):
    f = open(path, "r")
    NFA = json.load(f)
    return NFA

def getPowerset(states):
    if len(states) == 0:
        return [[]]

    subsets = []
    firstState = states[0]
    otherStates = states[1:]
    for subset in getPowerset(otherStates):
        subsets.append(subset)
        subsets.append(subset[:] + [firstState])

    return subsets

def toDFA(NFA, path):
    DFA = {}
    DFA['states'] = getPowerset(NFA['states'])
    
    DFA['letters'] = NFA['letters']
    
    DFA['transition_function'] = []
    
    for curState in DFA['states']:
        for alph in DFA['letters']:
            reach = []
            flag = True
            while flag:
                flag = False
                for trans in NFA['transition_function']:
                    if trans[1] == alph:
                        if trans[0] in curState:
                            if trans[2] not in reach:
                                reach.append(trans[2])
                                flag = True
                    if trans[1] == '$':
                        if trans[0] in reach:
                            if trans[2] not in reach:
                                reach.append(trans[2])
                                flag = True
            DFA['transition_function'].append([curState, alph, reach])
    

    DFA['start_states'] = [NFA['start_states']]
    flag = True
    while flag:
        flag = False
        for trans in NFA['transition_function']:
            if trans[1] == '$':
                if trans[0] in NFA['start_states']:
                    if trans[2] not in DFA['start_states'][0]:
                        DFA['start_states'][0].append(trans[2])
                        flag = True
    
    DFA['final_states'] = []
    for state in NFA['final_states']:
        for stateSet in DFA['states']:
            if state in stateSet and stateSet not in DFA['final_states']:
                DFA['final_states'].append(stateSet)
    
    f = open(path, "w+")
    json.dump(DFA, f, indent=4)


def main():
    if len(sys.argv) != 3:
        exit()
    
    NFA = readNFA(sys.argv[1])
    toDFA(NFA, sys.argv[2])


if __name__ == "__main__":
    main()