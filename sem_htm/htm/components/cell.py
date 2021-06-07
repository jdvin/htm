class Cell:
    '''
    Cells sit within columns. 
    An activated cell represents a temporal contex of its parent column.
    '''

    def __init__(self):
        self.segments = []
