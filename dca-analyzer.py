import csv
import json 
from argparse import ArgumentParser

class Position:

    def __init__(self):
        self.shares = 0
        self.totalInvested = 0
        self.lastPrice = 0

    def dca(self, shares, pricePerShare):
        self.shares = self.shares + int(shares)
        self.totalInvested = self.totalInvested + (int(shares) * pricePerShare)
        self.lastPrice = pricePerShare
    
    def getCostBasis(self):
        if self.shares == 0:
            return 0
        
        return self.totalInvested / self.shares 

    def getReturnPct(self):
        if self.getCostBasis() == 0: 
            return 0

        return (self.lastPrice - self.getCostBasis()) / self.getCostBasis() * 100
    
    def getPositionValue(self):
        return self.lastPrice * self.shares
    
    def __repr__(self):
        d = {
            "shares": self.shares,
            "totalInvested": str.format("{:.2f}", self.totalInvested),
            "positionValue": str.format("{:.2f}",self.getPositionValue()),
            "lastPrice": str.format("{:.2f}",self.lastPrice),
            "costBasis": str.format("{:.2f}",self.getCostBasis()),
            "return%": str.format("{:.2f}",self.getReturnPct())
        }
        return json.dumps(d)

def loadData(fileLoc):
    results = None
    with open(fileLoc, "r") as d:
        reader = csv.DictReader(d)
        results = [dict(r) for r in reader if r['Adj Close'] != "null"] 
    return results

if __name__ == '__main__':
    argp = ArgumentParser()
    argp.add_argument("--file", type=str, required=True, help="Yahoo finance CSV of historic stock data")
    argp.add_argument("--dca-amount", type=int, default=100, help="Amount to dollar-cost average each period")
    argp.add_argument("--start-date", type=str, default="1900-01-01", help="starting date of investing timeline")
    argp.add_argument("--end-date", type=str, default="2900-01-01", help="starting date of investing timeline")
    argp.add_argument("--skip", type=int, default=None, help="number of periods to skip between investment periods")
    args = argp.parse_args()

    data = sorted(loadData(args.file), key=lambda r: r['Date'])
    position = Position()

    cashPos = 0
    dcaAmt = int(args.dca_amount)
    isNegative = False 

    for d in data:
        isDateAfterInvestmentStart = d['Date'] >= args.start_date
        isDateAfterInvestmentEnd = d['Date'] >= args.end_date
        if isDateAfterInvestmentEnd:
            break 
        if isDateAfterInvestmentStart:
            sharePrice = float(d['Adj Close']) 
            shares = ( dcaAmt + cashPos) // sharePrice
            isEnoughCashToInvest = shares > 0
            if not isEnoughCashToInvest:
                cashPos = cashPos + dcaAmt
                continue
            cashPos = max(0, cashPos - (shares * sharePrice))

            position.dca( shares , float(d['Adj Close'])) 
            positionTurnedNegative = not isNegative and position.getReturnPct() < 0
            positionTurnedPositive = isNegative and position.getReturnPct() > 0
            if positionTurnedNegative:
                isNegative = True 
                print(f"Position went negative on {d['Date']}")
            elif positionTurnedPositive:
                isNegative = False 
                print(f"Position went positive on {d['Date']}")
            print(f"{d['Date']} {position}")

    print(f"{d['Date']} {cashPos} {position}")
