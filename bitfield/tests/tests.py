from django.test import TestCase
from .models import TestModel


class TestBitOperations(TestCase):

    def test_functionality(self):
        m = TestModel()
        m.flag.add_bit(TestModel.FLAG_TEST_ONE)
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_ONE))
        m.flag.add_bit(TestModel.FLAG_TEST_TWO)
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_ONE))
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_TWO))
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_ONE) and m.flag.has_bit(TestModel.FLAG_TEST_TWO))
        self.assertFalse(m.flag.has_bit(TestModel.FLAG_TEST_THREE))
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_ONE))
        self.assertTrue(m.flag.has_bit(TestModel.FLAG_TEST_ONE) or m.flag.has_bit(TestModel.FLAG_TEST_THREE))
        self.assertFalse(m.flag.has_bit(TestModel.FLAG_TEST_ONE) and m.flag.has_bit(TestModel.FLAG_TEST_THREE))
        m.flag.remove_bit(TestModel.FLAG_TEST_TWO)
        self.assertFalse(m.flag.has_bit(TestModel.FLAG_TEST_TWO))


class TestBitQueryset(TestCase):

    def test_functionality(self):
        m = TestModel.objects.create()
        qs = TestModel.objects.filter(id=m.id)
        qs.add_bit('flag', TestModel.FLAG_TEST_ONE)
        self.assertEqual(1, qs.has_any_bits('flag', TestModel.FLAG_TEST_ONE).count())
        self.assertEqual(1, qs.has_all_bits('flag', TestModel.FLAG_TEST_ONE).count())
        qs.add_bit('flag', TestModel.FLAG_TEST_TWO)
        self.assertEqual(1, qs.has_any_bits('flag', TestModel.FLAG_TEST_ONE).count())
        self.assertEqual(1, qs.has_any_bits('flag', TestModel.FLAG_TEST_TWO).count())
        self.assertEqual(1, qs.has_all_bits('flag', TestModel.FLAG_TEST_ONE, TestModel.FLAG_TEST_TWO).count())
        self.assertEqual(1, qs.has_any_bits('flag', TestModel.FLAG_TEST_ONE, TestModel.FLAG_TEST_THREE).count())
        self.assertEqual(0, qs.has_any_bits('flag', TestModel.FLAG_TEST_THREE).count())
        self.assertEqual(1, qs.has_no_bits('flag', TestModel.FLAG_TEST_THREE).count())
        self.assertEqual(0, qs.has_all_bits('flag', TestModel.FLAG_TEST_ONE, TestModel.FLAG_TEST_THREE).count())
        qs.remove_bit('flag', TestModel.FLAG_TEST_TWO)
        self.assertEqual(0, qs.has_any_bits('flag', TestModel.FLAG_TEST_TWO).count())
