class dildo:
      def __init__(self, a):
            self.a = a

array = [dildo([1,0]), dildo([2,0])]
bray = array.copy()
print(array[0])
print(bray[0])

if array[0] == bray[0]:
      print(True)
else:
      print(False)


print(bray[0].a)
print(array[0].a)
del bray[0]
print(bray[0].a)
print(array[0].a)

# def transform(array):
#       array[1] = array[0]
