import random


# Calculates how unfit a geneotype is
# More fit genes are represented by a lower returned value
# "Phenotype" calculation
def calcUnfit(g, teams):
	defect = 0
	UEFA_flag = []

	for a1 in range(0,len(g)):
		for a2 in range(a1+1,len(g)):
			# Basic condition (Rest doesn't matter if not in same group)
			b = (g[a1] == g[a2])

			# Defect 1: Only 1 team for each pot
			d1 = (b and teams[int(a1)][1] == teams[int(a2)][1])
			
			# Defect 2: Only 1 team for each confed except "UEFA" (2 allowed)
			d2 = (b and teams[int(a1)][2] == teams[int(a2)][2])

			if d2 and teams[int(a1)][2] == "UEFA" and g[a1] not in UEFA_flag:
				d2 = False
				UEFA_flag.append(g[a1])
			
			if d1:
				defect += 1

			if d2:
				defect += 1

	return defect



# Sort the genotypes by fitness
# Return the highest fitness
def evaluate(genes, teams):
	genes.sort(key=lambda x: calcUnfit(x,teams))

	return calcUnfit(genes[0],teams)


# Generate random genotypes
# Formulated such that every team always assigned 1 group
def genGenes(numGenes, gCount, numTeams):
	gList = []
	for i in range(0,numGenes):
		gString = ""
		for j in range(0,numTeams):
			gString += str(random.randint(0, gCount-1))
		gList.append(gString)

	return gList 

# Given set of genes gen(x) create new set of genes gen(x+1)
'''
What to consider
----------------
How do we select survivors? 
- Eletism? / Always kill the worst?

How do we introduce variation?
- Who gets to reproduce?
- Recombination?
- Mutation?

Approach
--------
1. Save mu best and kill rest
2. Choose from top at random to reproduce
3. Mutation - 1 random #, 1 random place

Additions?
----------
Crossover based on hemming distance?
'''

def reproduce(genes, mu, teams, gCount, numTeams):

	for i in range(mu,len(genes)):
		which = random.randint(0,mu-1) 
		genes[i] = genes[which] # Replace 
		
		# Mutate
		where = random.randint(0,numTeams-1)
		what = random.randint(0,gCount-1)

		# Because python strings immutable
		temp = list(genes[i])
		temp[where] = str(what)
		genes[i] = "".join(temp)


def main():
	# Read in data (AKA the boring work...)
	with open("input.txt") as fp:
		lines = fp.readlines()


	gCount = int(lines[0]) # Num groups
	pCount = int(lines[1]) # Num plots


	teams = {} # List of teams -> [name pot# conf]
	numTeams = 0

	for i in range(0,pCount):
		pot = lines[2+i].strip().split(",")
		for p in pot:
			teams[numTeams] = []
			teams[numTeams].append(p)
			teams[numTeams].append(i)
			numTeams += 1 

	
	for i in range(0,6):
		name, conf = lines[2+pCount+i].strip().split(":")
		for t in teams:
			if teams[t][0] in conf:
				teams[t].append(name)


	# Fun w/ genetics
	
	'''
	Note to TA (If you actually bother looking at the code - doubtful):
	Technically speaking all these values I hardcode are hyperparameters.
	I did some tuning based on the dataset given to us (On the "hardest" case) to
	get these values.
	'''
	mu = 50
	lam = 50

	# Init population of genotypes
	genes = genGenes(mu + lam, gCount, numTeams) 

	# Sort by fitness
	unfitness = evaluate(genes,teams)

	count = 0
	reset = 0
	while unfitness != 0:

		# When to call it quits
		if reset == 20:
			break

		# Fresh restart - Because my genetic functionality isn't the best..
		if count == 200:
			genes = genGenes(mu + lam, gCount, numTeams)
			unfitness = evaluate(genes,teams)
			count = 0
			reset += 1

		reproduce(genes, mu, teams, gCount, numTeams)

		# Sort by fitness
		unfitness = evaluate(genes,teams)

		count += 1

	# Output to file
	# First gene in genes
	groups = {}
	
	for i in range(0,len(genes[0])): # Loop through teams
		
		if int(genes[0][i]) not in groups: # If group of team not in dict
			groups[int(genes[0][i])] = []

		groups[int(genes[0][i])].append(teams[i][0])

	toOut = "Yes\n"
	for i in range(0,gCount):
		if i in groups:
			toOut += (",".join(groups[i]) + "\n")
		else:
			toOut += "None\n"

	toOut = toOut[:-1]

	with open("output.txt", "w") as fp:
		if reset != 20:
			fp.write(toOut)
		else:
			fp.write("No")


if __name__ == "__main__":
	main()

