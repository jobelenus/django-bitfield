from django.db import models
import bitfield


class TestModel(models.Model):
    FLAG_TEST_ONE = bitfield.create(1)
    FLAG_TEST_TWO = bitfield.create(2)
    FLAG_TEST_THREE = bitfield.create(3)
    FLAGS = (
        (FLAG_TEST_ONE, "One"),
        (FLAG_TEST_TWO, "Two"),
        (FLAG_TEST_THREE, "Three"),
    )
    flag = bitfield.BitField(default=0, choices=FLAGS)

    objects = bitfield.BitQueryset.as_manager()
