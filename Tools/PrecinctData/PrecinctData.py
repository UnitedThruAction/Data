"""Main class to load, process and export Precinct Data."""

from Database import Database
from VTD import VTD
from ElectionResult import ElectionResult

class PrecinctData(object):

    def __init__(self):
        pass

    @staticmethod
    def download_data():
        # TODO: Add download steps
        pass

    @staticmethod
    def load_data():
        Database.main()
        VTD.main()
        ElectionResult.main()

    @staticmethod
    def main():
        PrecinctData.download_data()
        PrecinctData.load_data()

if __name__ == "__main__":
    PrecinctData.main()
