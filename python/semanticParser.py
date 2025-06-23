class Parser:
    def __init__(self, seedFile):
        self.fp = open(seedFile)

    def parseData(self, dataFolder, outputFolder, outputSemanticType: str):
        if outputSemanticType == "cyper":
            return self.parseCypher(dataFolder, outputFolder)
        elif outputSemanticType == "dtgraph":
            return self.parseDgraph(dataFolder, outputFolder)
        else:
            return False

    def parseCypher(self, dataFolder, outputFolder):
        # TODO
        return True

    def parseDgraph(dataFolder, outputFolder):
        # TODO
        return False

    def close(self):
        self.fp.close()
