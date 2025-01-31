
# worldmodel time_rate: each secconds in realworld equals how many clocks in worldmodel
TIME_RATE = 1


## intial data for worldmodel

#initial population of the world:
INITIAL_POPULATION = 20
#initial people in line of each entity type - sum better not be greater than INITIAL__POPULATION
INITIAL_STORE_LINE = 3
INITIAL_HOSPITAL_LINE = 3
INITIAL_ECU_LINE = 3
#====================================================

## interval data for worldmodel

#repopulate interval clock:
REP_INTERVAL = 50
#repopulate count: how many persons should be created in each repopulate:
REP_COUNT = 5

# refill entity lines interval:
REFILL_INTERVAL = 25
# refill count for each entity:
STORE_REFILL_COUNT = 2
HOSPITAL_REFILL_COUNT = 2
ECU_REFILL_COUNT = 2
#==================================================


#earthquake clock inter vall:
EQ_INTERVAL = 300

#earchquake duration clock:
EQ_DURATION = 15
