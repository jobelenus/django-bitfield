from django.db.models import BigIntegerField, QuerySet, F, Q


def create(x):
    return 2 ** (x - 1)


def _flag_sql(field, flags, join=Q.AND, has=True):
    """
    Creating annotations and filters for all flag lookup queries

    JOIN KWARG:
    "has_any_flags" will join Q() objects with "OR"
    "has_all_flags/has_no_flags" will join Q() with "AND"

    HAS KWARG
    When `has is True` you're asking that a record has the flag
    The math there is: `set_flags & testing_for_flag > 0`
    When `has is False`, you're doing the opposite, so you're testing
    for == 0

    Implementation: for each flag we are asking about we need to mask the
    instance flag fields, hence the `name` var and counter to create unique ones
    """
    operator = '__gt' if has else ''
    annotate_kwargs = {}
    filters = Q()
    i = 0
    for flag in flags:
        name = "flag_mask_%d" % i
        annotate_kwargs[name] = F(field).bitand(flag)
        filters.add(Q(**{"%s%s" % (name, operator): 0}), join)
        i += 1
    return annotate_kwargs, filters


class BitQueryset(QuerySet):
    """
    Contains all queryset operations for any model `flag` field
    """
    def has_any_flags(self, *flags):
        annotate_kwargs, filters = _flag_sql(self.model.flag_field, flags, join=Q.OR)
        return self.annotate(**annotate_kwargs).filter(filters)

    def has_all_flags(self, *flags):
        annotate_kwargs, filters = _flag_sql(self.model.flag_field, flags)
        return self.annotate(**annotate_kwargs).filter(filters)

    def has_no_flags(self, *flags):
        annotate_kwargs, filters = _flag_sql(self.model.flag_field, flags, has=False)
        return self.annotate(**annotate_kwargs).filter(filters)

    def add_flag(self, flag):
        kwargs = {
            self.model.flag_field: F(self.model.flag_field).bitor(flag)
        }
        return self.update(**kwargs)

    def remove_flag(self, flag):
        kwargs = {
            self.model.flag_field: F(self.model.flag_field).bitand(~flag)
        }
        return self.update(**kwargs)


class BitOperations(object):

    def __init__(self, field):
        self.field = field  # the BitField instance

    def __set__(self, obj, value):
        bits, descs = zip(*self.field.flags)
        if value not in bits:
            raise ValueError('{} is not a valid value'.format(value))
        obj.__dict__[self.field.name] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return None
        return obj.__dict__[self.field.name]

    def has_flag(self, flag):
        return True if getattr(self, self.field) & flag else False

    def add_flag(self, flag):
        setattr(self, self.field, getattr(self, self.field) | flag)

    def remove_flag(self, flag):
        setattr(self, self.field, getattr(self, self.field) & ~flag)

    def get_flags_display(self):
        bits, descs = zip(*self.field.flags)
        desc = []
        i = 0
        for bit in bits:
            if self.has_flag(bit):
                desc.append(descs[i])
            i += 1
        return ", ".join(desc)


class BitField(BigIntegerField):

    def __init__(self, *args, choices=tuple, **kwargs):
        super(BitField, self).__init__(*args, **kwargs)
        try:
            assert isinstance(choices, tuple)  # must follow the django choice field implementation
        except AssertionError:
            raise Exception('Please pass a tuple containing your flags and labels as `choices`')
        self.flags = choices

    def get_prep_value(self, value):
        if value is None:
            return None
        return int(value)

    def contribute_to_class(self, cls, name, **kwargs):
        super(BitField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, BitOperations(self))
