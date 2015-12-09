from statsmodels import api as sm
from random import randint

c1 = 100
c2 = 1000
datalist = []
ecdf = sm.distributions


def generateData():
    for i in range(1000):
        data = randint(0, 9)
        datalist.append(datalist[-1] + data)


def calculateEcdf(datalist):
    ecdf = sm.distributions.ECDF(datalist)


def cacheUtility(vm, size):
    return(ecdf(size))


def optimize():
    # This is where the magic needs to happen
    pass


def state():
    s = 0
    i = 0
    state = [c1, c2]
    for v in state:
        s += cacheUtility(i, v)
        i += 1
    return s


def main():
    generateData()
    calculateEcdf(datalist)
    optimize()


if __name__ == "__main__":
    main()
