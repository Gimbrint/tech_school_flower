import logging
import random

class list:
    def get_random_item(self, items : list, probabilities : list=None):
        # No probabilities given, so make it evenly distributed
        if probabilities == None:
            probabilities = self.get_default_probabilities(self=self, items=items)

        # Number of items and probabilities
        itemLength = items.__len__()
        probLength = probabilities.__len__()

        # There must be the same items of probabilities as the number of items
        if probLength < itemLength or probLength > itemLength:
            logging.error(" Number of probabilities not the same as number of items")
            return None

        # Generate a random number
        randomValue = random.random()

        # Current weight (all previous weights + current probability)
        currentWeight = 0

        # Go through each items
        for i in range(0, itemLength, 1):
            currentWeight += probabilities[i]

            if randomValue < currentWeight:
                # We found our item!
                return items[i]

    # Generates equal probabilities if none are specified
    def get_default_probabilities(self, items : list) -> list:
        length = items.__len__()
        probabilities = [None] * length # Why this? Why not just use list(<length>)

        for i in range(0, length, 1):
            probabilities[i] = 1 / length

        return probabilities