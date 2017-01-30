#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import Levenshtein

class Matcher:

	def __init__(self, source, target):
		# Source and target should be given according to this schema:
		# {elements: [ordered list of column names], constraints: [ordered list of column types], data: [ordered list of sample data for each element]}


		self.source = source
		self.target = target

	def _elementLinguisticMatcher(self):
		# Perform Levenshtein distance on elements and compare, return grade for each pair
		pairMap = {}
		for sourceElement in self.source['elements']:
			pairMap[sourceElement] = []
			for targetElement in self.target['elements']:			
				biggestLength = max(len(sourceElement), len(targetElement))
				editDistance = self._levenshteinDistance(sourceElement, targetElement)
				similarityPercentage = (biggestLength - editDistance) / float(biggestLength)
				pairMap[sourceElement].append(similarityPercentage)

		return pairMap


	def _levenshteinDistance(self, str1, str2):
		return Levenshtein.distance(str1, str2)

		
	# Too slow, using the built-in dynamic programming solution
	# Recursive, not very efficient levenshtein algorithm, there is also a dynamic programming solution
	#def _levenshteinDistance(self, str1, str2):
		# If either string is empty, the cost to edit them to match them is 0
	#	if len(str1) == 0 or len(str2) == 0:
	#		return 0
	#
	#	if str1[-1].lower() == str2[-1].lower():
	#		cost = 0
	#	else:
	#		cost = 1
	#	
	#	opt1 = self._levenshteinDistance(str1[:-1], str2) 
	#	opt2 = self._levenshteinDistance(str1, str2[:-1])		
	#	opt3 = self._levenshteinDistance(str1[:-1], str2[:-1])	
	#
	#	return min(opt1 + 1, opt2 + 1, opt3 + int(cost))
			


	def _elementConstraintMatcher(self):
		# Compare the type strings and find closest matches. Could also compare the integers, but then one wouldn't get a ratio approximation, but rather a 1 or 0 if the type match perfectly. With the strings, one does not need perfect matches, e.g. (BLOB, MEDIUMBLOB)
		# Perform Levenshtein distance on constraints and compare, return grade for each pair
		pairMap = {}
		sourceIndex = 0
		for sourceElement in self.source['elements']:
			targetIndex = 0
			pairMap[sourceElement] = []
			for targetElement in self.target['elements']:
				biggestLength = max(len(self.source['constraints'][sourceIndex]), len(self.target['constraints'][targetIndex]))
				editDistance = self._levenshteinDistance(self.source['constraints'][sourceIndex], self.target['constraints'][targetIndex])
				similarityPercentage = (biggestLength - editDistance) / float(biggestLength)
				pairMap[sourceElement].append(similarityPercentage)

				targetIndex += 1

			sourceIndex += 1

		return pairMap


	def _instanceLinguisticMatcher(self):
		# Compare the data sample and return grade
		# Comparison criteria:
		# 1. String length (easy solution)
		pairMap = {}
		sourceIndex = 0
		for sourceElement in self.source['elements']:
			targetIndex = 0
			pairMap[sourceElement] = []
			for targetElement in self.target['elements']:
				
				sourceData =  self.source['data'][sourceIndex]
				targetData = self.target['data'][targetIndex]
				if not isinstance(sourceData, basestring):
					sourceData = str(sourceData)
				else:
					sourceData.encode('utf-8')

				if not isinstance(targetData, basestring):
					targetData = str(targetData)
				else:
					targetData.encode('utf-8')

				biggestLength = max(len(sourceData), len(targetData))
				lengthDistance = biggestLength - min(len(sourceData), len(targetData))
				similarityPercentage = (biggestLength - lengthDistance) / float(biggestLength)
				pairMap[sourceElement].append(similarityPercentage)

				targetIndex += 1

			sourceIndex += 1

		return pairMap
		


	def matchSchemas(self, threshold=0):
		matchedElements = []

		elementLinguisticComparisons = self._elementLinguisticMatcher()
		elementConstraintComparisons = self._elementConstraintMatcher()
		instanceLinguisticComparisons = self._instanceLinguisticMatcher()

		# Save similarity percentages
		similarities = []

		for sourceElement in self.source['elements']:
			maxSimilarity = 0.0
			maxSimilarTarget = ''
			targetIndex = 0
			for targetElement in self.target['elements']:
				overallSimilarityPercentage = elementLinguisticComparisons[sourceElement][targetIndex]*elementConstraintComparisons[sourceElement][targetIndex]*instanceLinguisticComparisons[sourceElement][targetIndex]
				if overallSimilarityPercentage > maxSimilarity:
					maxSimilarity = overallSimilarityPercentage
					maxSimilarTarget = targetElement
					
				targetIndex += 1

			similarities.append(maxSimilarity)
			matchedElements.append((sourceElement, maxSimilarTarget))
			print "Match source element [" + sourceElement + "] to target element [" + maxSimilarTarget + "] based on similarity percentage " + str(maxSimilarity)


		if threshold > 0:
			thresholdMatchedElements = []
			print ""
			print "Threshold is set. Matching elements with similarity percentage > " + str(threshold)
			print ""
			i = 0
			for matchTuple in matchedElements:
				if similarities[i] > threshold:
					thresholdMatchedElements.append(matchTuple)
					print "Match source element [" + matchTuple[0] + "] to target element [" + matchTuple[1] + "] based on similarity percentage " + str(similarities[i]) 

				i += 1
				
			return thresholdMatchedElements
		else:
			return matchedElements


	def matchSchemasByElementAndConstraintLinguistic(self):
		matchedElements = []
		elementLinguisticComparisons = self._elementLinguisticMatcher()
		elementConstraintComparisons = self._elementConstraintMatcher()

		for sourceElement in self.source['elements']:
			maxSimilarity = 0.0
			maxSimilarTarget = ''
			targetIndex = 0
			for targetElement in self.target['elements']:
				overallSimilarityPercentage = elementLinguisticComparisons[sourceElement][targetIndex]*elementConstraintComparisons[sourceElement][targetIndex]
				if overallSimilarityPercentage > maxSimilarity:					
						maxSimilarity = overallSimilarityPercentage
						maxSimilarTarget = targetElement
						
				targetIndex += 1

			matchedElements.append((sourceElement, maxSimilarTarget))
			
				
			print "Match source element [" + sourceElement + "] to target element [" + maxSimilarTarget + "] based on similarity percentage " + str(maxSimilarity)
		

		return matchedElements

		
