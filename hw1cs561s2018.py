
def main():
	# Read data
	with open("input.txt") as fp:
		lines = fp.readlines()

	# Process data so can plug and play
	if lines[0][:-1] == "Star":
		player = 0 

	else:
		player = 1

	algo = lines[1][:-1]

	maxDepth = int(lines[2][:-1])


	# Tuple coordinates of pieces
	tilePos = [[],[]] #0-Star,1-Circle

	# Can take away some of this , dont need grids
	for lIndex in range(3,len(lines)-1):
		splitted = lines[lIndex][:-1].split(",")
	
		for cIndex in range(0,len(splitted)):
			if "S" in splitted[cIndex]:
				for t in range(0,int(splitted[cIndex][1:])):
					tilePos[0].append((lIndex-3,cIndex)) 
			elif "C" in splitted[cIndex]: 
				for t in range(0,int(splitted[cIndex][1:])):
					tilePos[1].append((lIndex-3,cIndex))


	weights = map(int, lines[len(lines)-1].split(","))

	# Predictions
	if algo == "MINIMAX":
		nextMove, mUtility, fUtility, numNodes = minimax(tilePos,player,player,weights,maxDepth,0,None)

	else:
		inf = 10000000000
		nextMove, mUtility, numNodes, fUtility, beta = abPruning(tilePos,player,player,weights,maxDepth,0,None,-inf,inf)

	if nextMove == ((-1,-1),(-1,-1)):
		nextMoveT = "pass"
	else:
		nextMoveT = chr(72-nextMove[0][0]) + str(nextMove[0][1]+1) + "-" + chr(72-nextMove[1][0]) + str(nextMove[1][1]+1)
	
	# Output
	with open("output.txt","w") as fp:
		fp.write(nextMoveT + "\n")
		fp.write(str(mUtility) + "\n")
		fp.write(str(fUtility) + "\n")
		fp.write(str(numNodes))


# Last row properties in every case(So basically check if empty unless last row)
# Are pieces where I want to go?
def listMoves(player, tilePos):
	lom = [] # Tuple of tuples: (toKick, toReplace)

	for pos in tilePos[player]:
		up = pos[0] - 1
		down = pos[0] + 1
		right = pos[1] + 1
		left = pos[1] - 1
			
		upJmp = pos[0] - 2
		downJmp = pos[0] + 2 
		rightJmp = pos[1] + 2
		leftJmp = pos[1] - 2


		s1 = (up >= 0 and right <= 7) # Moving up and right
		s2 = (up >= 0 and left >= 0) # Moving up and left
		s3 = (upJmp >= 0 and rightJmp <= 7 and (up,right) in tilePos[1]) # Right over opponent's piece
		s4 = (upJmp >= 0 and leftJmp >= 0 and (up,left) in tilePos[1]) # Left over opponent's piece

		# Empty check for up and right
		s5 = (((up, right) not in (tilePos[0] + tilePos[1]) and up != 0) or ((up,right) not in tilePos[1] and up == 0)) 
		# Empty check for up and left
		s6 = (((up, left) not in (tilePos[0] + tilePos[1]) and up != 0) or ((up,left) not in tilePos[1] and up == 0)) 
		# Empty check for right over opponent's pieces
		s7 = (((upJmp, rightJmp) not in (tilePos[0] + tilePos[1]) and upJmp != 0) or ((upJmp,rightJmp) not in tilePos[1] and upJmp == 0))
		# Empty check for left over opponenet's pieces
		s8 = (((upJmp, leftJmp) not in (tilePos[0] + tilePos[1]) and upJmp != 0) or ((upJmp,leftJmp) not in tilePos[1] and upJmp == 0))

		c1 = (down <= 7 and right <= 7) # Moving down and right
		c2 = (down <= 7 and left >= 0) # Moving down and left
		c3 = (downJmp <= 7 and rightJmp <= 7 and (down, right) in tilePos[0]) # Right over opponent's piece
		c4 = (downJmp <= 7 and leftJmp >= 0 and (down, left) in tilePos[0]) # Left over opponent's piece

		# Empty check for down and right
		c5 = (((down, right) not in (tilePos[0] + tilePos[1]) and down != 7) or ((down,right) not in tilePos[0] and down == 7)) 
		# Empty check for down and left
		c6 = (((down, left) not in (tilePos[0] + tilePos[1]) and down != 7) or ((down,left) not in tilePos[0] and down == 7)) 
		# Empty check for right over opponent's pieces
		c7 = (((downJmp, rightJmp) not in (tilePos[0] + tilePos[1]) and downJmp != 7) or ((downJmp,rightJmp) not in tilePos[0] and downJmp == 7))
		# Empty check for left over opponenet's pieces
		c8 = (((downJmp, leftJmp) not in (tilePos[0] + tilePos[1]) and downJmp != 7) or ((downJmp,leftJmp) not in tilePos[0] and downJmp == 7))

		# Star
		if player == 0:
			if s1 and s5: # Moving up and right
				lom.append((pos,(up,right)))
			if s2 and s6: # Moving up and left
				lom.append((pos,(up,left)))
			if s3 and s7: # Right over opponent's piece
			 	lom.append((pos,(upJmp,rightJmp),(up,right)))
			if s4 and s8: # Left over opponent's piece
				lom.append((pos,(upJmp,leftJmp),(up,left)))

		# Circle
		if player == 1:
			if c1 and c5: # Moving down and right
				lom.append((pos,(down,right)))
			if c2 and c6: # Moving down and left
				lom.append((pos,(down,left)))
			if c3 and c7: # Right over opponent's piece
			 	lom.append((pos,(downJmp,rightJmp),(down,right)))
			if c4 and c8: # Left over opponent's piece
				lom.append((pos,(downJmp,leftJmp),(down,left)))


	return lom 


# Calculate the utility 
def calcUtility(tilePos, weights, player):
	starSum = 0
	for pos in tilePos[0]:
		starSum += weights[7-pos[0]]
	
	circleSum = 0
	for pos in tilePos[1]:
		circleSum += weights[pos[0]]

	if player == 0:
		return starSum - circleSum
	
	else:
		return circleSum - starSum


# Given a playing board compute the different moves from that state
'''
	def minimax(
		tilePos - Where tiles from each player are
		rPlayer - Who are we doing these calculations for => Uses MAX f(n)
		cPlayer - Could be root or could be opponent => Uses MIN f(n) when opponent
		weights - weight values for pos
		maxDepth - How deep should the recursion tree go
		layer - What the current layer is
		action - What action brought to this state
	)

	returns mUtility, fUtility, nextMove, numNodes
'''

def minimax(tilePos,rPlayer,cPlayer,weights,maxDepth,layer,action):
	
	mUtility = calcUtility(tilePos,weights,rPlayer)  

	# Base Case: Reached max depth or player out of pieces
	if layer == maxDepth or len(tilePos[cPlayer]) == 0:
		#print "Leaf " + str(action) + " " + str(mUtility)
		return action, mUtility, mUtility,  1


	lom = listMoves(cPlayer,tilePos)

	if len(lom) == 0:
		# Base case - neither player can make valid move => pass and then pass => ends
		if action == ((-1,-1),(-1,-1)):
			#print "Leaf " + str(action) + " " + str(mUtility)
			return ((-1,-1),(-1,-1)), mUtility, mUtility, 2 
		else: 
			lom.append(((-1,-1),(-1,-1)))


	# Follow expansion order: 
	# Sort based on init positions, Sort based on final positions
	# Sort based on row/col ascending
	lom.sort(key=lambda x: (x[0],x[1]))

	prop = []

	#print "Action Step: " + str(action)
	for each in lom:
		# Do action
		if abs(each[0][0] - each[1][0]) == 2: 
			toRemember = 0
			while each[2] in tilePos[int(cPlayer==0)]: 
				tilePos[int(cPlayer==0)].remove(each[2]) # Kill enemy piece
				toRemember += 1 # Remember who killed

		if each != ((-1,-1),(-1,-1)):
			tilePos[cPlayer].remove(each[0])
			tilePos[cPlayer].append(each[1])
		
		# Generate new state
		mUtility = calcUtility(tilePos,weights,rPlayer) 
		#if cPlayer == rPlayer:
			#print "MAX Step: " + str(each) + " " + str(mUtility)
		#else:
			#print "MIN Step: " + str(each) + " " + str(mUtility) 
		_,_,fUtility,numNodes = minimax(tilePos,rPlayer,int(cPlayer==0),weights,maxDepth,layer+1,each)
		
		prop.append((each,mUtility,fUtility,numNodes))

		# Undo action
		if abs(each[0][0] - each[1][0]) == 2:
			for i in range(0,toRemember):
				tilePos[int(cPlayer==0)].append(each[2]) # Revive enemy piece

		if each != ((-1,-1),(-1,-1)):
			tilePos[cPlayer].append(each[0])
			tilePos[cPlayer].remove(each[1])

	numNodes = sum([val[3] for val in prop])

	# rPlayer == cPlayer : Try and maximize
	if rPlayer == cPlayer:
		# Sort prop on fUtility decreasing & order
		nextMove,mUtility,fUtility,_ = sorted(prop, key=lambda x:(x[2], -x[0][0][0], -x[0][0][1], -x[0][1][0], -x[0][1][1]), reverse=True)[0]

		return nextMove, mUtility, fUtility, (numNodes + 1)

	# cPlayer != rPlayer : Try and minimize 
	else:
		# Sort prop on fUtility decreasing & order
		nextMove,mUtility,fUtility,_ = sorted(prop, key=lambda x:(x[2], x[0][0], x[0][1]))[0]
		
		return nextMove, mUtility, fUtility, (numNodes + 1)

# Given a playing board compute the different moves from that state
'''
	def abPruning(
		tilePos - Where tiles from each player are
		rPlayer - Who are we doing these calculations for => Uses MAX f(n)
		cPlayer - Could be root or could be opponent => Uses MIN f(n) when opponent
		weights - weight values for pos
		maxDepth - How deep should the recursion tree go
		layer - What the current layer is
		action - What action brought to this state
		alpha - Highest utility choice so far for any point along the path for MAX
			  - When MIN hits a node lower than alpha -> stop
		beta - Highest utility choice so far for any point along the path for MIN
			 - When MAX hits a node higher than beta -> stop
	)

	returns nextMove, mUtility, numNodes, alpha, beta
'''

def abPruning(tilePos,rPlayer,cPlayer,weights,maxDepth,layer,action,alpha,beta):
	
	mUtility = calcUtility(tilePos,weights,rPlayer)  

	# Base Case: Reached max depth or player out of pieces
	if layer == maxDepth or len(tilePos[cPlayer]) == 0:
		if rPlayer != cPlayer: # MIN root updates BETA 
			#print "MIN Leaf " + str(layer) + " " + str(mUtility)
			return action, mUtility, 1, alpha, mUtility
		else: # MAX root updates ALPHA
			#print "MAX Leaf " + str(layer) + " " + str(mUtility)
			return action, mUtility, 1, mUtility, beta


	lom = listMoves(cPlayer,tilePos)

	if len(lom) == 0:
		# Base case - neither player can make valid move => pass and then pass => ends
		if action == ((-1,-1),(-1,-1)):
			if rPlayer != cPlayer: # MIN root updates BETA 
				return ((-1,-1),(-1,-1)), mUtility, 2, alpha, mUtility
			else: # MAX root updates ALPHA
				return ((-1,-1),(-1,-1)), mUtility, 2, mUtility, beta
		else: 
			lom.append(((-1,-1),(-1,-1)))


	# Follow expansion order: 
	# Sort based on init positions, Sort based on final positions
	# Sort based on row/col ascending
	lom.sort(key=lambda x: (x[0],x[1]))

	numNodes = 0

	for each in lom:
		# Do action
		if abs(each[0][0] - each[1][0]) == 2: 
			toRemember = 0
			while each[2] in tilePos[int(cPlayer==0)]: 
				tilePos[int(cPlayer==0)].remove(each[2]) # Kill enemy piece
				toRemember += 1 # Remember who killed

		if each != ((-1,-1),(-1,-1)):
			tilePos[cPlayer].remove(each[0])
			tilePos[cPlayer].append(each[1])

		# Generate new state
		if cPlayer == rPlayer:
			mUtilityP = calcUtility(tilePos,weights,rPlayer)
			#print str(each) + " " + str(layer) + " " + str(alpha) + " " + str(beta)
			_, _, numNodesP, _, alphaP = abPruning(tilePos,rPlayer,int(cPlayer==0),weights,maxDepth,layer+1,each,alpha,beta)
			numNodes += numNodesP
		else:
			mUtilityP = calcUtility(tilePos,weights,rPlayer)
			#print str(each) + " " + str(layer) + " " + str(alpha) + " " + str(beta)
			_, _, numNodesP, betaP, _ = abPruning(tilePos,rPlayer,int(cPlayer==0),weights,maxDepth,layer+1,each,alpha,beta)
			numNodes += numNodesP

		# Undo action
		if abs(each[0][0] - each[1][0]) == 2:
			for i in range(0,toRemember):
				tilePos[int(cPlayer==0)].append(each[2]) # Revive enemy piece

		if each != ((-1,-1),(-1,-1)):
			tilePos[cPlayer].append(each[0])
			tilePos[cPlayer].remove(each[1])

		if cPlayer == rPlayer:
			if beta <= alphaP: # If MAX hits a value >= than beta 
				alpha = alphaP
				#print "broke MAX"
				break
			elif alphaP > alpha:
				mUtility = mUtilityP
				alpha = alphaP
				action = each
			

		else:
			if alpha >= betaP: # If MIN hits a value <= alpha 
				beta = betaP
				#print "broke MIN"
				break
			elif betaP < beta:
				mUtility = mUtilityP
				beta = betaP
				action = each

	return action, mUtility, (numNodes + 1), alpha, beta 

if __name__ == "__main__":
	main()

