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
    P = 0
    if len(x) == 1:
        for j in Y:
            if p[j]*B[j][x[0]] > P:
                P = p[j]*B[j][x[0]]
    if len(x) >= 2:
        P = 0
        for l in Y:
            for m in Y:
                if p[l]*B[l][x[1]]*A[l][m]*B[m][x[1]] > P:
                    P = p[l]*B[l][x[1]]*A[l][m]*B[m][x[1]]
                    p_fixed = p[l]*B[l][x[1]]
                    y_pred = l

        for i in range(2, len(x)):
            P = 0
            for l in Y:
                for m in Y:
                    if p_fixed*A[y_pred][l]*B[l][x[i-1]]*A[l][m]*B[m][x[i]] > P:
                        P = p_fixed*A[y_pred][l]*B[l][x[i-1]]*A[l][m]*B[m][x[i]]
                        fix = p_fixed*A[y_pred][l]*B[l][x[i-1]]
                        y_pred = l
            p_fixed = fix
                
    return P
            
  # Посчитать max_y P(y|x)

def get_viterbi_path(x, X, Y, A, B, p):
    P = 0
    path = []
    if len(x) == 1:
        for j in Y:
            if p[j]*B[j][x[0]] > P:
                P = p[j]*B[j][x[0]]
                y = j
        path.append(y)
    if len(x) >= 2:
        P = 0
        for l in Y:
            for m in Y:
                if p[l]*B[l][x[0]]*A[l][m]*B[m][x[1]] > P:
                    P = p[l]*B[l][x[0]]*A[l][m]*B[m][x[1]]
                    p_fixed = p[l]*B[l][x[0]]
                    y_pred = l
        path.append(y_pred)

        for i in range(2, len(x)):
            P = 0
            for l in Y:
                for m in Y:
                    if p_fixed*A[y_pred][l]*B[l][x[i-1]]*A[l][m]*B[m][x[i]] > P:
                        P = p_fixed*A[y_pred][l]*B[l][x[i-1]]*A[l][m]*B[m][x[i]]
                        fix = p_fixed*A[y_pred][l]*B[l][x[i-1]]
                        y_pred = l
                        y_last = m
            p_fixed = fix
            path.append(y_pred)
        path.append(y_last)
        
    return P, path

  # Посчитать y = argmax_y P(y|x)

x = [0, 1, 1, 0, 0, 1, 0]
print get_viterbi_probability(x, X, Y, A, B, p)
print get_viterbi_path(x, X, Y, A, B, p)
