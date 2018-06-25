# A quick little implementation of a bitfield for a django model

There is a discus project on github that already implements this feature
but its unmaintained now and only had declared support for django 1.4

I am using a much simpler bitfield technique in current projects, but it had
significant limitations (which are not an issue in their context)

I wanted a good exercise to understand how to use the `contribute_to_class` method
when implementing custom fields in Django/class attributes in Python. Specifically
I wanted to figure out how to be able to create the functionality of putting methods on
a field (e.g. `mymodel.myfield.do_something`, where myfield still holds a value)

So rather than pick up the existing project to modernize it, which actually doesn't
cover the specific goal I wanted to learn, I worked on the very simple code and implementation
I already had, and significantly improved it.
