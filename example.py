from state import state as football_state, nil_state as football_nil

from result import eval as result
from selection import typeof as selns
from trend import trend
from gfootball import gfootball

from market import *


most_goals = max(map(partition(goals, 'team'), len))
total_goals = len(goals)

print result(most_goals, football_state)
print result(most_goals, football_nil)
print selns(most_goals)
print trend(most_goals, football_nil, football_state)
print trend(most_goals, football_nil, football_nil)

print result(total_goals, football_state)
print result(total_goals, football_nil)
print selns(total_goals)
print trend(total_goals, football_nil, football_state)

calculate = gfootball(football_state)
print calculate(most_goals)
print calculate(total_goals)
