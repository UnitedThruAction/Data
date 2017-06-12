"""Main class to load, process and export Precinct Data."""

from Database import Database
from Cousub import Cousub
from VTD import VTD
from ElectionResult import ElectionResult
from ElectionDistrict import ElectionDistrict

class PrecinctData(object):

    def __init__(self):
        pass

    @staticmethod
    def download_data():
        pass

    @staticmethod
    def load_data():
        Database.main()
        Cousub.main()
        VTD.main()
        ElectionResult.main()
        ElectionDistrict.main()

    @staticmethod
    def output_data():
        pass

    @staticmethod
    def main():
        PrecinctData.download_data()
        PrecinctData.load_data()
        PrecinctData.output_data()

if __name__ == "__main__":
    PrecinctData.main()
