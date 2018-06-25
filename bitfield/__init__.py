from django.db.models import BigIntegerField, QuerySet, F, Q


def create(x):
    return 2 ** (x - 1)


def _bit_sql(field, bits, join=Q.AND, has=True):
    """
    Creating annotations and filters for all bit lookup queries

    JOIN KWARG:
    "has_any_bits" will join Q() objects with "OR"
    "has_all_bits/has_no_bits" will join Q() with "AND"

    HAS KWARG
    When `has is True` you're asking that a record has the bit
    The math there is: `set_bits & testing_for_bit > 0`
    When `has is False`, you're doing the opposite, so you're testing
    for == 0

    Implementation: for each bit we are asking about we need to mask the
    instance bit fields, hence the `name` var and counter to create unique ones
    """
    operator = '__gt' if has else ''
    annotate_kwargs = {}
    filters = Q()
    i = 0
    for bit in bits:
        name = "bit_mask_%d" % i
        annotate_kwargs[name] = F(field).bitand(bit)
        filters.add(Q(**{"%s%s" % (name, operator): 0}), join)
        i += 1
    return annotate_kwargs, filters


class BitQueryset(QuerySet):
    """
    Contains all queryset operations for any model `bit` field
    """
    def has_any_bits(self, *bits):
        bits = list(bits)
        field_name = bits.pop(0)
        annotate_kwargs, filters = _bit_sql(field_name, bits, join=Q.OR)
        return self.annotate(**annotate_kwargs).filter(filters)

    def has_all_bits(self, *bits):
        bits = list(bits)
        field_name = bits.pop(0)
        annotate_kwargs, filters = _bit_sql(field_name, bits)
        return self.annotate(**annotate_kwargs).filter(filters)

    def has_no_bits(self, *bits):
        bits = list(bits)
        field_name = bits.pop(0)
        annotate_kwargs, filters = _bit_sql(field_name, bits, has=False)
        return self.annotate(**annotate_kwargs).filter(filters)

    def add_bit(self, field_name, bit):
        kwargs = {
            field_name: F(field_name).bitor(bit)
        }
        return self.update(**kwargs)

    def remove_bit(self, field_name, bit):
        kwargs = {
            field_name: F(field_name).bitand(~bit)
        }
        return self.update(**kwargs)


class BitWrapper(object):
    """
    Handles all the model field functions
    """

    def __init__(self, instance, name, field):
        self.value = instance.__dict__[name]
        self.name = name
        self.instance = instance
        self.field = field

    def to_python(self):
        return self.value

    def _validate_bit(self, bit):
        bits, descs = zip(*self.field.bits)
        bit = int(bit)
        if bit not in bits:
            raise ValueError('{} is not a valid value'.format(bit))

    def has_bit(self, bit):
        self._validate_bit(bit)
        return True if self.value & bit else False

    def add_bit(self, bit):
        self._validate_bit(bit)
        setattr(self.instance, self.name, self.value | bit)

    def remove_bit(self, bit):
        self._validate_bit(bit)
        setattr(self.instance, self.name, self.value & ~bit)

    def get_bit_display(self):
        bits, descs = zip(*self.field.bits)
        desc = []
        i = 0
        for bit in bits:
            if self.has_bit(bit):
                desc.append(descs[i])
            i += 1
        return ", ".join(desc)

    def __int__(self):
        return self.value

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.value)

    def __eq__(self, other):
        return True if int(other) == int(self) else False

    def __and__(self, other):
        return self.value & other

    def __or__(self, other):
        return self.value | other


class BitOperations(object):
    """
    Contribute_to_class wrapper object
    """

    def __init__(self, field):
        self.field = field  # the BitField instance

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value

    def __get__(self, instance, cls=None):
        if instance is None:  # unsure what case this handles
            return None
        return BitWrapper(instance, self.field.name, self.field)


class BitField(BigIntegerField):

    def __init__(self, *args, choices=None, **kwargs):
        super(BitField, self).__init__(*args, **kwargs)
        if choices:
            try:
                assert isinstance(choices, tuple)  # must follow the django choice field implementation
            except AssertionError:
                raise Exception('Please pass a tuple containing your bits and labels as `choices`')
            self.bits = choices
        else:
            self.bits = tuple()

    def get_prep_value(self, value):
        if value is None:
            return None
        return int(value)

    def contribute_to_class(self, cls, name, **kwargs):
        super(BitField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, BitOperations(self))

    @property
    def _val(self):
        return self.__dict__[self.name]

    def __and__(self, other):
        return self._val & other

    def __or__(self, other):
        return self._val | other
