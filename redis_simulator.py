import time
import pickle
from exceptions import KeyNotFound
from typing import Optional, Union


class BaseDataStore:

    def __init__(self) -> None:
        self.key_value_pairs = {}

    def is_expired(self, entry: dict) -> bool:
        return entry['ttl'] is not None and time.time() > entry['ttl']
    
    def has_expired(self, entry: dict) -> bool:
        return entry['ttl'] is not None

    def save_state(self, filename: str = 'redis_state.pkl') -> None:
        with open(filename, 'wb') as file:
            pickle.dump(self.key_value_pairs, file)

    def load_state(self, filename: str = 'redis_state.pkl') -> None:
        try:
            with open(filename, 'rb') as file:
                self.key_value_pairs = pickle.load(file)
        except FileNotFoundError:
            pass

class RedisSimulator(BaseDataStore):

    def __init__(self):
        super().__init__()

    def set_data(self, key: str, value: str, ttl: Optional[int] = None) -> str:
        time_to_live = ttl
        expire_time = time.time() + ttl if ttl else None
        self.key_value_pairs[key] = {'value':value, 'ttl':expire_time, 'tl':time_to_live}
        self.save_state()
        return 'OK!'

    def get_data(self, key: str, res_key: Optional[str] = 'value', just_value: Optional[bool] = True) -> Union[str, None]:
        try:
            key_detail = self.key_value_pairs[key]
            if self.is_expired(key_detail):
                del self.key_value_pairs[key]
                raise KeyError
            result = key_detail[res_key] if just_value else key_detail
            return result
        except KeyError as e:
            return None

    def delete_data(self, key: str) -> int:
        try:
            del self.key_value_pairs[key]
            self.save_state()
            return 1
        except KeyError as e:
            return 0
        
    def ttl_data(self, key: str) -> int:
        key_detail = self.get_data(key,just_value=False)
        if key_detail:
            if self.has_expired(key_detail):
                return key_detail['tl']
            return -1
        return -2

