import code

class Row:
    """Class containing a guess code and answer code"""

    def __init__(self,guess,result=None):
        print 'ha', guess, result
        self.__guess = guess
        self.__result = result

    def setGuess(self,guess):
        self.__guess = guess

    def setResult(self,result):
        self.__result = result

    def getGuess(self):
        return self.__guess

    def getResult(self):
        return self.__result

