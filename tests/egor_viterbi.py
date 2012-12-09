# -*- coding: utf-8 -*-
from collections import defaultdict
import operator

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
    #X - наблюдаемые события
    #Y - внутренние состояния
    #phi = вероятность цепочки y на шаге i
    phi = defaultdict(lambda: defaultdict(float))

    all_states = ['start'] + list(Y)
    for state in all_states:
        phi[-1][state] = 1.0
        A['start'][state] = p[state]

    #проходим все наблюдения
    for i,obs in enumerate(x):

        #перебираем все возможные следующие состояния
        for state in Y:
            max_prob = float('-inf')
            #находим максимальный путь до состояния Y
            for prev_state in all_states:
                prob = phi[i-1][prev_state] * A[prev_state][state] * B[state][obs]
                if prob > max_prob: max_prob = prob
            #записываем max P(x1..xi,y1..i)
            phi[i][state] = max_prob

    return phi[len(x) -1][max(phi[len(x) -1])] # Посчитать max_y P(y|x)

def get_viterbi_path(x, X, Y, A, B, p):
    # Посчитать y = argmax_y P(y|x)
    #X - наблюдаемые события
    #Y - внутренние состояния
    #phi = вероятность цепочки y на шаге i
    phi = defaultdict(lambda: defaultdict(float))

    backtrace = defaultdict(lambda: defaultdict(str))
    path = []

    all_states = ['start'] + list(Y)
    for state in all_states:
        phi[-1][state] = 1.0
        A['start'][state] = p[state]

    #проходим все наблюдения
    for i,obs in enumerate(x):

        #перебираем все возможные следующие состояния
        for state in Y:
            max_prob = float('-inf')
            source_state = None
            #находим максимальный путь до состояния Y
            for prev_state in all_states:
                prob = phi[i-1][prev_state] * A[prev_state][state] * B[state][obs]
                if prob > max_prob:
                    max_prob = prob
                    source_state = prev_state
                #записываем max P(x1..xi,y1..i)
            phi[i][state] = max_prob
            backtrace[i][state] = source_state

    #начинаем back_trace

    last_state = None
    max_prob = float('-inf')

    #ищем максимальное состояние
    for key in phi[len(x) - 1]:
        prob = phi[len(x) - 1][key]
        if prob > max_prob:
            max_prob = prob
            last_state = key

    it_state = last_state
    #проходим с конца и записываем в путь предыдущие состояния
    for index in reversed(range(1,len(x))):
        path.append( backtrace[index][it_state] )
        it_state = backtrace[index][it_state]
    path.append(last_state)
    return path # Посчитать max_y P(y|x)

if __name__ == "__main__":
    print get_viterbi_probability([1,0,0,1,1,0],X,Y,A,B,p)
    print get_viterbi_path([1,0,0,1,1,0],X,Y,A,B,p)
