import random

def wallBetween(grid,point,action):
	sRow,sCol = point

	rAct = action[0]
	if action[0] != 0:
		rAct = rAct/abs(rAct)

	cAct = action[1]
	if action[1] != 0:
		cAct = cAct/abs(cAct)

	for i in range(1,max(abs(action[0]),abs(action[1]))+1):

		if grid[sRow+(i*rAct)][sCol+(i*cAct)][0] == "Wall":  
			return True

	return False

def exceedsBounds(grid,point,action):
	sRow,sCol = point
	nRows,nCols = len(grid),len(grid[0])
	
	mRow = sRow + action[0]
	mCol = sCol + action[1]
	if (mRow >= nRows or mRow < 0) or (mCol >= nCols or mCol < 0): 
		return True

	return False

# Input: action, grid, point
# Output: utility
def getWalkUnits(grid,point,action, pWalk, pRun):
	sRow,sCol = point

	pApp = pRun
	if max(abs(action[0]),abs(action[1])) == 1:
		pApp = pWalk

	# Action occurs
	# Probability: pApp
	# Next square
	uA = grid[sRow][sCol][1]

	if not (exceedsBounds(grid,point,action) or wallBetween(grid,point,action)):
		uA = grid[sRow+action[0]][sCol+action[1]][1]

	# 90 degree of action occurs
	# Probability: 0.5*(1-pApp)
	# Next square
	mod90 = (action[1],action[0])
	uMod90 = grid[sRow][sCol][1]  

	if not (exceedsBounds(grid,point,mod90) or wallBetween(grid,point,mod90)):
		uMod90 = grid[sRow+mod90[0]][sCol+mod90[1]][1]

	# -90 degree of action occurs
	# Probability: 0.5*(1-pApp)
	# Next square
	modN90 = (-mod90[0],-mod90[1])
	uModN90 = grid[sRow][sCol][1]

	if not (exceedsBounds(grid,point,modN90) or wallBetween(grid,point,modN90)):
		uModN90 = grid[sRow+modN90[0]][sCol+modN90[1]][1]

	return pApp*uA + 0.5*(1-pApp)*uMod90 + 0.5*(1-pApp)*uModN90


def getCalc(grid,point,pWalk,pRun,rWalk,rRun,dFactor):
	actions = [(1,0),(-1,0),(0,-1),(0,1),(2,0),(-2,0),(0,-2),(0,2)]
	
	maxAction = actions[0]
	maxUtility = rWalk + dFactor*getWalkUnits(grid,point,actions[0],pWalk,pRun)

	for a in actions[1:]:
		rs = rRun
		if max(abs(a[0]),abs(a[1])) == 1:
			rs = rWalk
		
		test = rs + dFactor*getWalkUnits(grid,point,a,pWalk,pRun)

		if test > maxUtility:
			maxUtility = test
			maxAction = a

	return maxAction, maxUtility

# Returns a dictionary: Key: str(Point tuple), Value: arr [row,col,action,prob]
def getNeighborsA(grid,point,action, pWalk, pRun):
	toReturnD = {}

	sRow,sCol = point

	pApp = pRun
	if max(abs(action[0]),abs(action[1])) == 1:
		pApp = pWalk

	# Action occurs - Probability: pApp - Next square

	# Success - Add different point
	if not (exceedsBounds(grid,point,action) or wallBetween(grid,point,action)):
		toAppend = [sRow+action[0],sCol+action[1],action,pApp]
		toReturnD[str((sRow+action[0],sCol+action[1]))] = toAppend

	# Failure - Add current point
	else:
		toAppend = [sRow,sCol,action,pApp]
		toReturnD[str((sRow,sCol))] = toAppend

	# 90 degree of action occurs - Probability: 0.5*(1-pApp) - Next square
	mod90 = (action[1],action[0])

	# Success - Add different point
	if not (exceedsBounds(grid,point,mod90) or wallBetween(grid,point,mod90)):
		toAppend = [sRow+mod90[0],sCol+mod90[1],action,0.5*(1-pApp)]
		toReturnD[str((sRow+mod90[0],sCol+mod90[1]))] = toAppend

	# Failure - Add current point
	else:
		toAppend = [sRow,sCol,action,0.5*(1-pApp)]
		if str((sRow,sCol)) in toReturnD:
			toReturnD[str((sRow,sCol))][3] += 0.5*(1-pApp)
		else: 
			toReturnD[str((sRow,sCol))] = toAppend 

	# -90 degree of action occurs - Probability: 0.5*(1-pApp) - Next square
	modN90 = (-mod90[0],-mod90[1])
	
	# Success - Add different point
	if not (exceedsBounds(grid,point,modN90) or wallBetween(grid,point,modN90)):
		toAppend = [sRow+modN90[0],sCol+modN90[1],action,0.5*(1-pApp)]
		toReturnD[str((sRow+modN90[0],sCol+modN90[1]))] = toAppend

	# Failure - Add current point
	else:
		toAppend = [sRow,sCol,action,0.5*(1-pApp)]
		if str((sRow,sCol)) in toReturnD:
			toReturnD[str((sRow,sCol))][3] += 0.5*(1-pApp)
		else: 
			toReturnD[str((sRow,sCol))] = toAppend 

	return toReturnD

# Returns list of dicts & list of tuples
def getNeighbors(grid,point,pWalk,pRun,rWalk,rRun,dFactor):
	actions = [(1,0),(-1,0),(0,-1),(0,1),(2,0),(-2,0),(0,-2),(0,2)]
	nActions = [] # With actions
	nGeneral = [] # All neighbors (Used for psweep - Doesn't include self or terminals)
	
	for a in actions:
		perAction = getNeighborsA(grid, point, a, pWalk, pRun)
		nActions.append(perAction)
		
		for e in perAction:
			r,c,_,_ = perAction[e]
			if (r,c) not in nGeneral and (r,c) != point and grid[r][c][0] != "Term":
				nGeneral.append((r,c))  


	return nActions,nGeneral


def main():
	# Load values from file
	with open("input.txt") as fp:
		lines = fp.read().splitlines()

	nRows,nCols = lines[0].split(",")
	nRows,nCols = int(nRows),int(nCols)
	
	nWalls = int(lines[1])
	
	pWalls = []
	for i in range(2, nWalls + 2):
		row,col = lines[i].split(",")
		pWalls.append((int(row)-1,int(col)-1))

	nTerms = int(lines[nWalls + 2])

	pTerms = []
	for i in range(nWalls + 3, len(lines)-3):
		row,col,reward = lines[i].split(",")
		pTerms.append((int(row)-1,int(col)-1,float(reward)))

	pWalk,pRun = lines[len(lines)-3].split(",")
	pWalk,pRun = float(pWalk),float(pRun) 

	rWalk,rRun = lines[len(lines)-2].split(",")
	rWalk,rRun = float(rWalk),float(rRun)

	dFactor = float(lines[len(lines)-1])

	# 3D array w/ innermost being properties of space
	# Properties of space:
	# 1. Type - Wall, Term, Open
	# 2. Utility
	# 3. Action

	grid = []

	# Init all as movable spaces
	for r in range(nRows):
		grid.append([])
		for c in range(nCols):
			grid[r].append(["Open",0,(1,0)])

	# Add walls
	for w in pWalls:
		row,col = w
		grid[row][col][0],grid[row][col][1],grid[row][col][2] = "Wall",None,"None"


	# Add terminals
	for t in pTerms:
		row,col,reward = t
		grid[row][col][0],grid[row][col][1],grid[row][col][2] = "Term",reward,"Exit" 


	# nbr is a 2d array
	# Each slot contains 2 arrays:
	#	1. Neighbors w/ actions/probabilities [r,c,a,p]
	#	2. Unique list of all tangent points
	# Calculate this for terminal points as well (But only care about 2nd slot)

	nGrid = []
	
	# Fill in nbr struct
	for r in range(nRows):
		nGrid.append([])
		for c in range(nCols):
			nActions,nGeneral = None,None
			if grid[r][c][0] != "Wall":
				nActions,nGeneral = getNeighbors(grid,(r,c),pWalk,pRun,rWalk,rRun,dFactor)
			nGrid[r].append([nActions,nGeneral])

	# Keep track of priorities, Initially all equal to 0.0
	pGrid = []
	for r in range(nRows):
		pGrid.append([])
		for c in range(nCols):
			pGrid[r].append(0.0)

	queue = []

	# Initially fill queue w/ elements close to terminal
	for t in pTerms:
		row,col,_ = t
		tangent = nGrid[row][col][1]
		for p in tangent:
			r,c = p
			if (r,c) not in queue:	# Terminals may share tangent points
				queue.append((r,c)) 

	random.shuffle(queue)

	K = len(queue)
	
	while len(queue) != 0:

		for i in range(K):
			if len(queue) == 0:
				break

			row,col = queue.pop()

			# Calculate new utility
			action, utility = getCalc(grid,(row,col),pWalk,pRun,rWalk,rRun,dFactor)

			pGrid[row][col] = 0.0 # Make priority 0
		
			# Calculate change in utility
			delta = grid[row][col][1] - utility

			# Apply changes
			grid[row][col][2],grid[row][col][1] = action,utility # Update utility & action
				
			# Loop through predecessors
			for tangent in nGrid[row][col][1]:
				r,c = tangent
							
				maxProb = 0.0

				for aDict in nGrid[r][c][0]:
					
					# Not every action will cause piece to move to current space
					if str((r,c)) in aDict and aDict[str((r,c))][3] > maxProb:
						maxProb = aDict[str((r,c))][3]

				if maxProb*delta > 0.0 and ((r,c)) not in queue:
					queue.append((r,c))

				pGrid[r][c] = max(pGrid[r][c],delta*maxProb)
			
		# Sort queue by priority - Have to correct as to update next K best elements
		queue.sort(key=lambda x: pGrid[x[0]][x[1]], reverse=True)

	# Push to output file (Flip axis - Go from bottom up)
	toOutput = ""

	for r in range(len(grid)-1,-1,-1):
		for c in range(len(grid[0])):
			
			# Term or wall
			if grid[r][c][0] != "Open":
				toOutput += (grid[r][c][2]+ ",")
			
			# Space
			else:
				action = grid[r][c][2]

				prefix = "Run"
				if max(abs(action[0]),abs(action[1])) == 1:
					prefix = "Walk"

				# Up or down
				if abs(action[0]) > abs(action[1]):
					direction = "Down," # Default up
					if action[0] > 0:
						direction = "Up,"

				# Left or right
				else:
					direction = "Left," # Default left
					if action[1] > 0:
						direction = "Right,"

				
				toOutput += (prefix + " " + direction) 

		toOutput = toOutput[:-1]
		toOutput += "\n"

	with open("output.txt","w") as fp:
		fp.write(toOutput)


if __name__ == "__main__":
	main()
