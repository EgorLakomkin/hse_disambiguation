# -*- coding: utf-8 -*-
from collections import defaultdict
from math import log

from maxent import MaxentModel


def compute_features( ice_cream ,  i, previous_label):
    #if previous_label:
    #    yield "label-previous={0}".format(previous_label)

    #yield "yesterday-sold-more-5={0}".format( str( ice_cream[i-1] >=5 )  )
    #yield "yesterday-less-5={0}".format( str( ice_cream[i-1] <=5 ) )
    yield "today-sold-more-5={0}".format(  ice_cream[i] >=5   )
    yield "today-less-5={0}".format(  ice_cream[i] <=5  )


def get_viterbi_path_memm(x, Y,me):
    # Посчитать y = argmax_y P(y|x)
    #X - наблюдаемые события
    #Y - внутренние состояния
    #phi = вероятность цепочки y на шаге i
    phi = defaultdict(lambda: defaultdict(lambda : -1))

    backtrace = defaultdict(lambda: defaultdict(str))
    path = []

    features = list( compute_features( x , 0, None ) )

    probs = me.eval_all( features )
    #for class_name, class_prob in probs:
    #    phi[ -1 ][ class_name ] = log(class_prob)
    #    backtrace[ -1 ] [ class_name ] = None

    #проходим все наблюдения
    for i,obs in enumerate(  x  ):

        #перебираем все возможные следующие состояния
        for state in Y:
            max_prob = float('-inf')
            source_state = None
            #находим максимальный путь до состояния Y

            features = list( compute_features( x, i , source_state ) )
            class_probabilities = me.eval_all( features )

            for class_name, class_prob in class_probabilities:
                prob = phi[ i -1 ][ state ] + log(class_prob)
                if prob > max_prob:
                    max_prob = prob
                    source_state = class_name

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
    path.append(last_state)
    #проходим с конца и записываем в путь предыдущие состояния
    for index in reversed(range(1,len(x))):
        path.append( backtrace[index][it_state] )
        it_state = backtrace[index][it_state]


    return path[::-1] # Посчитать max_y P(y|x)


SUN = 'sun'
RAIN = 'rain'
train_data = [(SUN, 10),(SUN,8),(SUN,11), (RAIN,3),(RAIN,2),(SUN,6),(SUN,10),(RAIN,1)]


labels_train = [ i[0] for i in train_data]
icecream_train = [ i[1] for i in train_data]


me = MaxentModel()

me.begin_add_event()

for i,data in enumerate( train_data ):
    features = list(compute_features( icecream_train,  i , labels_train[ i - 1] if i > 0 else None )  )
    me.add_event(features, labels_train[i] )
me.end_add_event()

me.train()


Y = set([ SUN, RAIN ])


print get_viterbi_path_memm( x = [1,1,6], Y = Y , me = me)


me.save('sunny.dat')

