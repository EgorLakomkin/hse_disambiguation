# -*- coding: utf-8 -*-
from collections import defaultdict

from maxent import MaxentModel


def compute_features( ice_cream , current_day, i, previous_label):
    if previous_label:
        yield "label-previous={0}".format(previous_label)

    if current_day:
        yield "label-current={0}".format(current_day)

    yield "yesterday-sold-more-5={0}".format( str( ice_cream[i-1] >=5 )  )
    yield "yesterday-less-5={0}".format( str( ice_cream[i-1] <=5 ) )
    yield "today-sold-more-5={0}".format( str( ice_cream[i] >=5 )  )
    yield "today-less-5={0}".format( str( ice_cream[i] <=5 ) )

SUN = 'sun'
RAIN = 'rain'
train_data = [(SUN, 10),(SUN,8),(SUN,11), (RAIN,3),(RAIN,2),(SUN,6),(SUN,10),(RAIN,1)]
test_data = [ 5, 3, 5, 6, 7, 8, 1, 2, 6 ]


labels_train = [ i[0] for i in train_data]
icecream_train = [ i[1] for i in train_data]

icecream_test = [ i for i in test_data]

me = MaxentModel()

me.begin_add_event()

for i,data in enumerate( train_data ):
    features = list(compute_features( icecream_train, labels_train[i], i , labels_train[ i - 1] if i > 0 else None )  )
    me.add_event(features, labels_train[i] )
me.end_add_event()

me.train()

for i in test_data:
    features = list(compute_features( icecream_test, None, i , None  ) )
    result = me.eval_all( features )
    print result

me.save('sunny.dat')

