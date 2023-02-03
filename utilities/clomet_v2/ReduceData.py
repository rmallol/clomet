from numpy import average

from utilities.clomet_v2.ManageErrors import ManageErrors

class ReduceData:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

class Binning(ReduceData):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Applies binning technique.
    """
    def applyBinning(self, A, axis, data):
        # TODO check what happens with empty spaces
        total = 0
        generalkey = ""
        for key, value in A.items():
            generalkey = key
            total = len(value[axis])
            break

        if (generalkey == ""):
            #addErrorReport("No keys available in A")
            print("ERROR: no keys available in A")
            self.errormanager.addError("ERROR: no keys available in A")
            return False

        goal = 1000
        batch = int(total/goal)
        batchremainder = total % goal

        for key, value in A.items():
            a = []
            b = []
            batchadd = 0
            left = 0
            while ( left < len(A[key][axis]) ):
                if (batchadd < (batchremainder-1)):
                    right = left + batch + 1
                    batchadd = batchadd + 1
                else:
                    right = left + batch

                if ( len(A[key][axis]) > int(right) ):
                    a.append(average(A[key][axis][int(left):int(right)]))
                    b.append(average(A[key][data][int(left):int(right)]))
                left = right
            a = self.reduceDecimals(a)
            A[key]['BinningX'] = a
            A[key]['Binning'] = b

        return A

    """
    Reduces decimals for readability.
    """
    def reduceDecimals(self, A):

        axis = []

        for i in range(len(A)):
            axis.append( round(A[i], 4) )

        return axis

