import json
import sys


def readDFA(path):
    f = open(path, "r")
    DFA = json.load(f)
    return DFA

def optimize(DFA, path):
    for state in DFA['states']:
        reachable = False
        for trans in DFA['transition_function']:
            if trans[2] == state:
                reachable = True
        if reachable == False:
            DFA['states'].remove(state)
        
    
    optDFA = {}
    
    statePairs = []
    
    for state1 in DFA['states']:
        for state2 in DFA['states']:
            if (state2, state1) not in statePairs and state1 != state2:
                statePairs.append((state1, state2))

    marked = []
    for state1, state2 in statePairs:
        if (state1 in DFA['final_states']) != (state2 in DFA['final_states']):
            marked.append((state1, state2))
    
    transitions = {}
    for trans in DFA['transition_function']:
        if trans[0] not in transitions.keys():
            transitions[trans[0]] = {}
        transitions[trans[0]][trans[1]] = trans[2]
    
    for state1, state2 in statePairs:
        for alph in DFA['letters']:
            if (transitions[state1][alph], transitions[state2][alph]) in marked:
                if (state1, state2) not in marked:
                    marked.append((state1, state2))

    curStates = []
    
    for state1, state2 in statePairs:
        if (state1, state2) not in marked:
            toAdd = True
            for state in curStates:
                if state1 in state and state2 in state:
                    toAdd = False
                elif state1 in state:
                    state.append(state2)
                    toAdd = False
                elif state2 in state:
                    state.append(state1)
                    toAdd = False
            if toAdd:
                curStates.append([state1, state2])
    
    for state in DFA['states']:
        toAdd = True
        for arr in curStates:
            if state in arr:
                toAdd = False
        if toAdd:
            curStates.append([state])
                
    map = {}
    for state in DFA['states']:
        for lis in curStates:
            if state in lis:
                map[state] = lis            
    
    optDFA['states'] = curStates
    optDFA['letters'] = DFA['letters']
    
    optDFA['transition_function'] = []
    for state in optDFA['states']:
        for trans in DFA['transition_function']:
            if trans[0] == state[0]:
                optDFA['transition_function'].append([state, trans[1], map[trans[2]]])
    
    for state in optDFA['states']:
        if DFA['start_states'][0] in state:
            optDFA['start_states'] = [state]
            break
    
    optDFA['final_states'] = []
    for state in optDFA['states']:
        if state[0] in DFA['final_states']:
            optDFA['final_states'].append(state)
        
    f = open(path, "w+")
    json.dump(optDFA, f, indent=4)                        
            
                        
def main():
    if len(sys.argv) != 3:
        exit()
    
    DFA = readDFA(sys.argv[1])
    optimize(DFA, sys.argv[2])


if __name__ == "__main__":
    main()