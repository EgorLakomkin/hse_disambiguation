from collections import defaultdict

Y = set([ 'sun', 'rain' ])
X = set([ 0, 1 ])
A = defaultdict(lambda: defaultdict(float))
A['sun']['sun'] = 0.5
A['sun']['rain'] = 0.5
A['rain']['sun'] = 0.5
A['rain']['rain'] = 0.5
B = defaultdict(lambda: defaultdict(float))
B['sun'][0] = 0.2
B['sun'][1] = 0.8
B['rain'][0] = 0.8
B['rain'][1] = 0.2
p = defaultdict(float)
p['sun'] = 0.5
p['rain'] = 0.5

def get_viterbi_probability(x, X, Y, A, B, p):
    M = defaultdict(lambda: defaultdict(float))
    vit_prob = []
    for state in Y:
        P = p[state]*B[state][x[0]]
        M[0][state] = P
        if len(x) == 1:
            vit_prob.append(M[0][state])
    
    for i in range(1, len(x)):
        for act_state in Y:
            P = 0
            for previous_state in Y:
                if M[i-1][previous_state]*A[previous_state][act_state]*B[act_state][x[i]] > P:
                    P = M[i-1][previous_state]*A[previous_state][act_state]*B[act_state][x[i]]
            M[i][act_state] = P
            if i == len(x) - 1:
                vit_prob.append(M[i][act_state])
    viterbi = max(vit_prob)
    return viterbi
               
  # Посчитать max_y P(y|x)

def get_viterbi_path(x, X, Y, A, B, p):
    M = defaultdict(lambda: defaultdict(float))
    path = defaultdict(lambda: defaultdict(str))
    max_path_reversed = []
    max_path = []
    for state in Y:
        P = p[state]*B[state][x[0]]
        M[0][state] = P
        
    if len(x) == 1:
        P = 0
        for state in Y:
            if M[0][state] > P:
                P = M[0][state]
                y = state
        max_path.append(y)
            
    for i in range(1, len(x)):            
        for act_state in Y:
            P = 0
            for previous_state in Y:
                if M[i-1][previous_state]*A[previous_state][act_state]*B[act_state][x[i]] > P:
                    P = M[i-1][previous_state]*A[previous_state][act_state]*B[act_state][x[i]]
                    y = previous_state
            M[i][act_state] = P
            path[i][act_state] = y
        if i == len(x) - 1:
            P = 0
            for state in Y:
                if M[i][state] > P:
                    P = M[i][state]
                    y = state
            max_path_reversed.append(y)
    for s in range(len(x)-1, 0, -1):
        max_path_reversed.append(path[s][y])
        y = path[s][y]
    for i in range(len(max_path_reversed)-1, -1, -1):
        max_path.append(max_path_reversed[i])
    return max_path

  # Посчитать y = argmax_y P(y|x)

x = [0, 1, 0, 1]
print get_viterbi_probability(x, X, Y, A, B, p)
print get_viterbi_path(x, X, Y, A, B, p)


