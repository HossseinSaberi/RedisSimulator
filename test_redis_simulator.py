import unittest
import time
from redis_simulator import RedisSimulator
from exceptions import InvalidTTLError


class TestRedisSimulator(unittest.TestCase):
    def setUp(self):
        self.redis_simulator = RedisSimulator()

    def test_set_get(self):
        self.redis_simulator.set_data("key1", "value1")
        self.assertEqual(self.redis_simulator.get_data("key1"), "value1")

    def test_set_ttl_get(self):
        self.redis_simulator.set_data("key1", "value1", ttl=5)
        time.sleep(2)
        self.assertEqual(self.redis_simulator.get_data("key1"), "value1")
        time.sleep(4)
        self.assertIsNone(self.redis_simulator.get_data("key1"))

    def test_set_invalid_ttl(self):
        with self.assertRaises(InvalidTTLError):
            self.redis_simulator.set_data("key1", "value1", ttl="invalid_ttl")

    def test_get_nonexistent_key(self):
        self.redis_simulator.get_data("nonexistent_key")
        self.assertIsNone(self.redis_simulator.get_data("nonexistent_key"))

    def test_set_delete(self):
        self.redis_simulator.set_data("key1", "value1")
        self.redis_simulator.delete_data("key1")
        self.assertIsNone(self.redis_simulator.get_data("key1"))

    def test_ttl_data(self):
        self.redis_simulator.set_data("key1", "value1", ttl=6)
        time.sleep(2)
        data_ttl = self.redis_simulator.ttl_data("key1")
        self.assertEqual(data_ttl, 6)

        self.redis_simulator.set_data("key1", "value1")
        data_ttl = self.redis_simulator.ttl_data("key1")
        self.assertEqual(data_ttl, -1)

        self.redis_simulator.set_data("key1", "value1", ttl=1)
        time.sleep(2)
        data_ttl = self.redis_simulator.ttl_data("key1")
        self.assertEqual(data_ttl, -2)

    # def test_transaction_commit(self):
    #     self.redis_simulator.begin_transaction()
    #     self.redis_simulator.set("key5", "value5")
    #     self.redis_simulator.commit_transaction()
    #     self.assertEqual(self.redis_simulator.get("key5"), "value5")
    #
    # def test_transaction_rollback(self):
    #     self.redis_simulator.set("key6", "value6")
    #     self.redis_simulator.begin_transaction()
    #     self.redis_simulator.set("key6", "updated_value6")
    #     self.redis_simulator.rollback_transaction()
    #     self.assertEqual(self.redis_simulator.get("key6"), "value6")
    #
    # def test_nested_transactions(self):
    #     self.redis_simulator.begin_transaction()
    #     with self.assertRaises(TransactionError):
    #         self.redis_simulator.begin_transaction()

    def test_save_load_state(self):
        self.redis_simulator.set_data("key1", "value1")
        self.redis_simulator.save_state("test_state.pkl")

        new_redis_simulator = RedisSimulator()
        new_redis_simulator.load_state("test_state.pkl")
        self.assertEqual(new_redis_simulator.get_data("key1"), "value1")

    def test_singlton_instance_of_redis_simulator(self):
        instance_id = id(self.redis_simulator)
        new_redis_simulator = RedisSimulator()
        new_insance_id = id(new_redis_simulator)
        self.assertEqual(instance_id, new_insance_id)

    def test_get_data_just_value(self):
        self.redis_simulator.set_data("key1", "value1")
        data_dict = self.redis_simulator.get_data("key1", just_value=False)
        expected_dict = {'value': 'value1', 'ttl': None, 'tl': None}
        self.assertDictEqual(data_dict,expected_dict)

    def test_get_data_res_key(self):
        self.redis_simulator.set_data("key1", "value1", ttl=10)
        ttl_data = self.redis_simulator.get_data("key1", res_key='tl')
        self.assertEqual(ttl_data, 10)

    def test_is_expire(self):
        self.redis_simulator.set_data("key1", "value1", ttl=6)
        time.sleep(2)
        data_ttl = self.redis_simulator.get_data("key1", just_value=False)
        self.assertFalse(self.redis_simulator.is_expired(data_ttl))

    def test_has_expire(self):
        self.redis_simulator.set_data("key1", "value1", ttl=6)
        time.sleep(2)
        data_ttl = self.redis_simulator.get_data("key1", just_value=False)
        self.assertTrue(self.redis_simulator.has_expired(data_ttl))

    def tearDown(self):
        self.redis_simulator.delete_data("key1")


if __name__ == "__main__":
    unittest.main()
