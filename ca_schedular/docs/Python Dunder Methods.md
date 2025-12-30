# Python Dunder Methods Reference

## 1. Object Creation & Destruction

### Constructor Allocation  
**Method:** `__new__(cls, *args, **kwargs)`  
**When Called:** Before `__init__`; allocates the new instance.  
```python
class C:
    def __new__(cls, *args, **kwargs):
        print("Allocating instance")
        return super().__new__(cls)

    def __init__(self, x):
        print("Initializing instance")
        self.x = x

c = C(10)
# Output:
# Allocating instance
# Initializing instance
```

### Initializer  
**Method:** `__init__(self, *args, **kwargs)`  
**When Called:** After `__new__`; initializes the instance.  
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(p.x, p.y)  # 3 4
```

### Destructor  
**Method:** `__del__(self)`  
**When Called:** Just before the object is garbage‑collected.  
```python
class C:
    def __del__(self):
        print(f"{self!r} is being deleted")

c = C()
del c  # Triggers __del__
```

## 2. String & Byte Representations

### Official Representation  
**Method:** `__repr__(self)`  
**When Called:** By `repr(obj)` and in the REPL.  
```python
class User:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"User(name={self.name!r})"

u = User("Alice")
print(repr(u))  # User(name='Alice')
```

### Informal String  
**Method:** `__str__(self)`  
**When Called:** By `str(obj)` and `print(obj)`.  
```python
class User:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"User: {self.name}"

u = User("Bob")
print(u)  # User: Bob
```

### Bytes Conversion  
**Method:** `__bytes__(self)`  
**When Called:** By `bytes(obj)`.  
```python
class Msg:
    def __init__(self, text):
        self.text = text
    def __bytes__(self):
        return self.text.encode('utf-8')

m = Msg("hello")
print(bytes(m))  # b'hello'
```

### Custom Formatting  
**Method:** `__format__(self, spec)`  
**When Called:** By `format(obj, spec)` and f-strings.  
```python
class Celsius:
    def __init__(self, temp):
        self.temp = temp
    def __format__(self, spec):
        if spec.endswith('f'):
            return f"{self.temp * 9/5 + 32:.1f}°F"
        return f"{self.temp:.1f}°C"

c = Celsius(20)
print(f"{c:.1f}")    # 20.0°C
print(f"{c:.1f f}")  # 68.0°F
```

## 3. Comparison & Hashing

```python
class Number:
    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        if not isinstance(other, Number):
            return NotImplemented
        return self.val == other.val

    def __lt__(self, other):
        if not isinstance(other, Number):
            return NotImplemented
        return self.val < other.val

    def __hash__(self):
        return hash(self.val)

    def __repr__(self):
        return f"Number({self.val})"

a, b = Number(3), Number(5)
print(a == Number(3))  # True
print(a < b)           # True
print({a, b})          # {Number(3), Number(5)}
```

## 4. Truthiness

**Method:** `__bool__(self)`  
**When Called:** By `bool(obj)` or in conditional contexts (`if obj:`).  
```python
class Bag:
    def __init__(self, items):
        self.items = items
    def __bool__(self):
        return bool(self.items)

b1 = Bag([])
b2 = Bag([1,2])
print(bool(b1), bool(b2))  # False True
```

## 5. Attribute Access

```python
class Proxy:
    def __init__(self, target):
        super().__setattr__('_target', target)

    def __getattr__(self, name):
        return getattr(self._target, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(self._target, name, value)

    def __delattr__(self, name):
        if name.startswith('_'):
            super().__delattr__(name)
        else:
            delattr(self._target, name)
```

## 6. Item & Sequence Protocols

```python
class MyList:
    def __init__(self, data):
        self.data = list(data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        self.data[idx] = value

    def __delitem__(self, idx):
        del self.data[idx]

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, item):
        return item in self.data

    def __reversed__(self):
        return reversed(self.data)

m = MyList([1,2,3])
print(len(m), m[1], 2 in m)  # 3 2 True
for x in reversed(m):
    print(x)
```

## 7. Callable Objects & Context Managers

### Callable Instances  
**Method:** `__call__(self, *args, **kwargs)`  
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, x):
        return x * self.factor

dbl = Multiplier(2)
print(dbl(5))  # 10
```

### Context Managers  
**Methods:** `__enter__(self)` and `__exit__(self, exc_type, exc, tb)`  
```python
class ManagedFile:
    def __init__(self, fname):
        self.fname = fname

    def __enter__(self):
        self.file = open(self.fname, 'w')
        return self.file

    def __exit__(self, exc_type, exc, tb):
        self.file.close()

with ManagedFile('out.txt') as f:
    f.write("Hello")
```

## 8. Arithmetic & In-Place Operators

```python
class Vec:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return Vec(self.x + other, self.y + other)
        return NotImplemented

    def __iadd__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self):
        return f"Vec({self.x}, {self.y})"

v1 = Vec(1,2)
v2 = Vec(3,4)
print(v1 + v2)  # Vec(4, 6)
v1 += v2
print(v1)       # Vec(4, 6)
```

## 9. Module Execution Guard

```python
# mymodule.py
def main():
    print("Running as script")

if __name__ == "__main__":
    main()
```
