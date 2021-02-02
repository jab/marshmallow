from marshmallow import Schema, fields
import simplejson
import sys
from time import sleep
from types import SimpleNamespace


def gen_foos():
    print("* generator called")
    yield from ({"foo": i} for i in range(5))
    print("* sleeping (1 second pause here)")
    sleep(1)
    yield {"foo": 5}
    print("* generator done")


print("********* simplejson.dump (with iterable_as_array=True) *********** ")
simplejson.dump(gen_foos(), sys.stdout, iterable_as_array=True)

# Result: Streaming works:
# * generator called
# [{"foo": 0}, {"foo": 1}, {"foo": 2}, {"foo": 3}, {"foo": 4}* sleeping (1 second pause here)
# , {"foo": 5}* generator done
# ]


print()
print()
print()
print("************** marshmallow_streaming_workaround **************")


def marshmallow_streaming_workaround(obj, schema):
    schema.many = False
    yield "["
    it = iter(obj)
    i = next(it, None)
    while i is not None:
        yield schema.dumps(i)
        i = next(it, None)
        if i is not None:
            yield ","
    yield "]"
    schema.many = True


class Foo(Schema):
    foo = fields.Integer()


for chunk in marshmallow_streaming_workaround(gen_foos(), Foo(many=True)):
    sys.stdout.write(chunk)

# Result: Streaming works:
#  [* generator called
#  {"foo": 0},{"foo": 1},{"foo": 2},{"foo": 3},{"foo": 4}* sleeping (1 second pause here)
#  ,{"foo": 5}* generator done
#  ]


print()
print()
print()
print("************** patched marshmallow + (wrapped)simplejson **************")


def dumps(obj, **kw):
    simplejson.dump(obj, sys.stdout, **kw)


class Foo(Schema):
    foo = fields.Integer()

    class Meta:
        render_module = SimpleNamespace(dumps=dumps)


Foo(many=True).dumps(gen_foos(), iterable_as_array=True)
print()

# Result: Streaming does not work:
#  * generator called
#  * sleeping (1 second pause here)
#  * generator done
#  [{"foo": 0}, {"foo": 1}, {"foo": 2}, {"foo": 3}, {"foo": 4}, {"foo": 5}]
