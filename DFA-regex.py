import json
import sys
import copy

def readDFA(path):
    f = open(path, "r")
    DFA = json.load(f)
    return DFA

def convertToRegex(DFA, path):
    i = "q0"
    c = 0
    while i in DFA['states']:
        c += 1
        i = "q"+str(c)

    DFA['states'].append(i)
    DFA['transition_function'].append([i, "$", DFA['start_states'][0]])
    DFA['start_states'] = [i]

    i = "q0"
    c = 0
    while i in DFA['states']:
        c += 1
        i = "q"+str(c)

    DFA['states'].append(i)
    for state in DFA['final_states']:
        DFA['transition_function'].append([state, "$", i])
    DFA['final_states'] = [i]
    
    
    transitions = {}
    for trans in DFA['transition_function']:
        if trans[0] not in transitions.keys():
            transitions[trans[0]] = {}
        transitions[trans[0]][trans[1]] = trans[2]
    
    for state in transitions.keys():
        toChange = []
        for alph1 in transitions[state].keys():
            for alph2 in transitions[state].keys():
                if alph1 != alph2 and transitions[state][alph1] == transitions[state][alph2]:
                    dest = transitions[state][alph1]
                    toChange.append([alph1, dest, 0])
                    toChange.append([alph2, dest, 0])
    
        toChange = [list(x) for x in set(tuple(x) for x in toChange)]
    
        flag = True
        while flag:
            flag = False
            for exp1 in toChange:
                for exp2 in toChange:
                    if exp1[0] != exp2[0] and exp1[1] == exp2[1]:
                        if exp1[2] == 0:
                            exp1[0] += "+"+exp2[0]
                            exp1[2] = 1
                            exp2[2] = 1
                            toChange.remove(exp2)
                            flag = True
                        elif exp2[2] == 0:
                            exp1[0] += "+"+exp2[0]
                            exp1[2] = 1
                            exp2[2] = 1
                            toChange.remove(exp2)
                            flag = True
        toDel = []
        for key in transitions[state].keys():
            for trans in toChange:
                if key in trans[0]:
                    toDel.append(key)
        for key in toDel:
            del transitions[state][key]
              
        for trans in toChange:
            transitions[state][trans[0]] = trans[1]
        
    DFA['transition_function'] = []
    for state in transitions.keys():
        for alph in transitions[state].keys():
            DFA['transition_function'].append([state, alph, transitions[state][alph]])
    
   
    
    while len(DFA['states']) > 2:
        newTrans = copy.deepcopy(DFA['transition_function'])
        
        rip_state = ""
        for state in DFA['states']:
            if state not in DFA['start_states'] and state not in DFA['final_states']:
                rip_state = state
                break
        for state1 in DFA['states']:
            for state2 in DFA['states']:
                if state1 in DFA['final_states']:
                    continue
                if state2 in DFA['start_states']:
                    continue
                R1 = ""
                R2 = ""
                R3 = ""
                R4 = ""
                for trans in DFA['transition_function']:
                    if trans[0] == state1 and trans[2] == rip_state:
                        R1 = trans[1]
                    if trans[0] == rip_state and trans[2] == rip_state:
                        R2 = trans[1]
                    if trans[0] == rip_state and trans[2] == state2:
                        R3 = trans[1]
                    if trans[0] == state1 and trans[2] == state2:
                        R4 = trans[1]
                
                
                R = ""
                if R1 and R3:
                    if R1 and R1 != "$":
                        R += R1
                    if R2 and R2 != "$":
                        R += R2 + "*"
                    if R3 and R3 != "$":
                        R += R3
                        
                    if R4:
                        R += "+"+R4 
                else:
                    R = R4 
                if R and R != "$" and len(R) > 1:
                    R = "("+R+")"
                
                added = False    
                for trans in newTrans:
                    if state1 == trans[0] and state2 == trans[2]:
                        trans[1] = R
                        added = True
                if not added and R:
                    newTrans.append([state1, R, state2])
            
            
        DFA['states'].remove(rip_state)
        toDel = []
        for trans in newTrans:
            if trans[0] == rip_state or trans[2] == rip_state:
                toDel.append(trans)
        for trans in toDel:
            newTrans.remove(trans)
            
        DFA['transition_function'] = newTrans
    
    regEx = {}
    regEx['regex'] = DFA['transition_function'][0][1]
    
    f = open(path, "w+")
    json.dump(regEx, f, indent=4)
                
def main():
    if len(sys.argv) != 3:
        exit()
    
    DFA = readDFA(sys.argv[1])
    convertToRegex(DFA, sys.argv[2])

if __name__ == "__main__":
    main()
