from random import choice, randint
from time import perf_counter
from pylab import plot, show, legend

STARTING_DOVES = 500
STARTING_HAWKS = 500
STARTING_POPULATION = STARTING_HAWKS + STARTING_DOVES

ROUNDS = 100
STARTING_ENERGY = 100


MIN_FOOD_PER_ROUND = 10
MAX_FOOD_PER_ROUND = 50

ENERGY_REQUIRED_FOR_REPRODUCTION = 40	
ENERGY_LOSS_FROM_FIGHTING = 500
ENERGY = 5 
RATIO = 0.2 #Modify this variable to get different results

"""
ECO equilibrium (two species cohexist)

RATIO = 0.2

Doves supremacy (Hawks disapear)

RATIO = 0.1 #or less

Hawks supremacy (everyone die)

RATIO = 0.5 #or more

"""

ENERGY_REQUIRED_FOR_LIVING = 10

STATUS_ACTIVE = "active"
STATUS_ASLEEP = "asleep"

TYPE_HAWK = "hawk"
TYPE_DOVE = "dove"

agents = []

# Graph stuff
graph_hawk_points = []
graph_dove_points = []

# Profiling


class Agent:
	id = 0
	agent_type = None
	status = STATUS_ACTIVE
	energy = STARTING_ENERGY


def main():
	init()
	current_round = 1
	death_count = 0
	breed_count = 0
	main_tic = perf_counter()

	while current_round <= ROUNDS and len(agents) > 2 :
		if(getAgentCountByType(TYPE_DOVE)+getAgentCountByType(TYPE_HAWK)>=20000):
				break
		
		tic = perf_counter()
		awakenAgents()

		food = getFood()
		if (current_round==1) :			
			print()
		else:
			# This could be optimized further by creating a list every time
			# that only has active agents, so it isn't iterating over entire list every time
			while True:
				agent, nemesis = getRandomAgents()
				if agent is None or nemesis is None: 
					break
				compete(agent, nemesis, food)


			round_dead_hawks, round_dead_doves = cull()
		
		toc = perf_counter()

		print("ROUND %d" % current_round)
		print("Food produced          : %d" % food)
		print("Population             : Hawks-> %d, Doves-> %d" % (getAgentCountByType(TYPE_HAWK), getAgentCountByType(TYPE_DOVE)))
		print("Hawks                  : %s" % getPercByType(TYPE_HAWK))
		print("Doves                  : %s" % getPercByType(TYPE_DOVE))
		print("----")
		print("Round Processing time  : %s" % getTimeFormatted(toc - tic))
		print("Elapsed time           : %s\n" % getTimeFormatted(perf_counter() - main_tic))

		# Plot
		graph_hawk_points.append(getAgentCountByType(TYPE_HAWK))
		graph_dove_points.append(getAgentCountByType(TYPE_DOVE))

		current_round += 1


	main_toc = perf_counter()

	print("=============================================================")
	print("Total dead agents      : %d" % death_count)
	print("Total breeding agents  : %d" % breed_count)
	print("Total rounds completed : %d" % (current_round - 1))
	print("Total population size  : %s" % len(agents))
	print("Hawks                  : %s" % getPercByType(TYPE_HAWK))
	print("Doves                  : %s" % getPercByType(TYPE_DOVE))
	print("Processing time        : %s" % getTimeFormatted(main_toc - main_tic))
	print("=============================================================")


def init():

	for x in range(0,STARTING_DOVES):
		a = Agent()
		a.agent_type = TYPE_DOVE
		agents.append(a)

	for x2 in range(0,STARTING_HAWKS):
		a2 = Agent()
		a2.agent_type = TYPE_HAWK
		agents.append(a2)


def getAvgFromList(list):
	return float( sum(list) / len(list) )


def getTimeFormatted(seconds):
	m, s = divmod(seconds, 60)
	return "%02d:%02d" % (m, s)	


def getFood():
	return randint(MIN_FOOD_PER_ROUND, MAX_FOOD_PER_ROUND)


def getPercByType(agent_type):
	perc = float(getAgentCountByType(agent_type)) / float(len(agents))
	return '{percent:.2%}'.format(percent=perc)


def getAliveAgentsCount():
	return getAgentCountByStatus(STATUS_ACTIVE) + getAgentCountByStatus(STATUS_ASLEEP)


def getRandomAgents():
	nemesis = None
	active_agents = list(generateAgentsByStatus(STATUS_ACTIVE))
	if len(active_agents) < 2:
		return None, None
	max_index = len(active_agents) - 1
	agent = active_agents[ randint(0, max_index) ]
	while nemesis is None:
		n = active_agents[ randint(0, max_index) ]
		if n is not agent:
			nemesis = n

	return agent, nemesis


def awakenAgents():
	for agent in agents:
		agent.status = STATUS_ACTIVE


def generateAgentsByType(agent_type):
	for agent in agents:
		if agent.agent_type == agent_type:
			yield agent


def generateAgentsByStatus(status):
	for agent in agents:
		if agent.status == status:
			yield agent


def getEnergyFromFood(food):
	return food # 1 to 1


def getAgentCountByStatus(status):
	count = len( list(generateAgentsByStatus(status)) )
	return count


def getAgentCountByType(agent_type):
	return len( list(generateAgentsByType(agent_type)) )


def compete(agent, nemesis, food):
	winner = choice([agent, nemesis])
	loser = agent if (winner is nemesis) else nemesis
	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_HAWK:
		if (getAgentCountByType(TYPE_HAWK)/(getAgentCountByType(TYPE_HAWK)+getAgentCountByType(TYPE_DOVE))) > RATIO:
			winner.energy += getEnergyFromFood(food) - ENERGY_LOSS_FROM_FIGHTING
			loser.energy  -= ENERGY_LOSS_FROM_FIGHTING
		else :
			winner.energy -= ENERGY
			loser.energy -= ENERGY
			breed(winner)

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_DOVE:
		agent.energy += getEnergyFromFood(food) - ENERGY
		nemesis.energy -= ENERGY_LOSS_FROM_FIGHTING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_HAWK:
		nemesis.energy += getEnergyFromFood(food) - ENERGY
		agent.energy -= ENERGY_LOSS_FROM_FIGHTING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_DOVE:
		agent.energy += getEnergyFromFood(food)/2 - ENERGY
		nemesis.energy += getEnergyFromFood(food)/2 - ENERGY
		breed(winner)

	nemesis.status = agent.status = STATUS_ASLEEP


def getNewAgent(agent_type, starting_energy=STARTING_ENERGY, status=STATUS_ASLEEP):
	agent = Agent()
	agent.agent_type = agent_type
	agent.status = status
	agent.energy = starting_energy
	return agent


def breed(agent):
		if agent.energy > ENERGY_REQUIRED_FOR_REPRODUCTION:
			agent.energy /= 2

			if agent.agent_type == TYPE_DOVE: 
				baby_agent = getNewAgent(agent.agent_type, (agent.energy/2))
				agents.append(baby_agent)

			if (agent.agent_type == TYPE_HAWK): 
				baby_agent = getNewAgent(agent.agent_type, (agent.energy/2))
				agents.append(baby_agent)
			
		

"""
def count_breeds():

	hawk_babies = 0
	dove_babies = 0
	for agent in agents:
		if agent.energy > ENERGY_REQUIRED_FOR_REPRODUCTION:
			baby_agent_a = getNewAgent(agent.agent_type, (agent.energy/2))
			baby_agent_b = getNewAgent(agent.agent_type, (agent.energy/2))

			agents.append(baby_agent_b)
			agents.append(baby_agent_a)

			agent.energy /= 2

			if agent.agent_type == TYPE_DOVE: dove_babies += 4
			if (agent.agent_type == TYPE_HAWK): 
				
				if randint(0,100)==1 :
					hawk_babies += 1


	return hawk_babies, dove_babies
"""
def cull():

	dead_hawks = 0
	dead_doves = 0
	for index, agent in enumerate(agents):
		if agent.energy < ENERGY_REQUIRED_FOR_LIVING:
			if agent.agent_type == TYPE_DOVE: dead_doves += 1
			if agent.agent_type == TYPE_HAWK: dead_hawks += 1
			del agents[index]


	return dead_hawks, dead_doves


main()
plot(graph_dove_points, label="Doves")
plot(graph_hawk_points, label="Hawks")
legend()

show()
