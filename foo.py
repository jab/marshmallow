from marshmallow import Schema, fields
import simplejson
import sys
from time import sleep
from types import SimpleNamespace


def gen():
    print("* generator called")
    yield from range(5)
    print("* sleeping (1 second pause here)")
    sleep(1)
    yield 5
    print("* generator done")


print("********* simplejson iterencode (with iterable_as_array=True) *********** ")
for chunk in simplejson.JSONEncoder(iterable_as_array=True).iterencode(gen()):
    print(chunk)

# Result: Streaming works:
# * generator called
# [0
# , 1
# , 2
# , 3
# , 4
# * sleeping (1 second pause here)
# , 5
# * generator done
# ]


print()
print()
print()
print("************** patched marshmallow with iterencode **************")


def iterencode(obj, **kw):
    kw.setdefault("iterable_as_array", True)
    return simplejson.JSONEncoder(**kw).iterencode(obj)


class Foo(Schema):
    ints = fields.List(fields.Integer())

    class Meta:
        render_module = SimpleNamespace(iterencode=iterencode)


for chunk in Foo().iterencode({"ints": gen()}):
    print(chunk)

# Result: Streaming works:
# {
# "ints"
# : 
# * generator called
# [0
# , 1
# , 2
# , 3
# , 4
# * sleeping (1 second pause here)
# , 5
# * generator done
# ]
# }
