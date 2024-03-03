import time
import pickle
from exceptions import KeyNotFound, InvalidTTLError
from typing import Optional, Union
from threading import Lock


class BaseDataStore:
    key_value_pairs = {}

    def __init__(self) -> None:
        pass

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
        except (FileNotFoundError,EOFError):
            pass


class RedisSimulator(BaseDataStore):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RedisSimulator, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()
        self.lock = Lock()

    def set_data(self, key: str, value: Union[str, list, set], ttl: Optional[str] = None) -> str:
        with self.lock:
            try:
                time_to_live = ttl
                expire_time = time.time() + int(ttl) if ttl else None
                self.key_value_pairs[key] = {'value': value, 'ttl':expire_time, 'tl':time_to_live}
                self.save_state()
                return 'OK!'
            except ValueError as e:
                raise InvalidTTLError('Error: Wrong --ttl Type , --ttl must be numeric')

    def get_data(self, key: str, res_key: Optional[str] = 'value', just_value: Optional[bool] = True) -> Union[str, list, set, None]:
        with self.lock:
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
        key_detail = self.get_data(key, just_value=False)
        if key_detail:
            if self.has_expired(key_detail):
                return int(key_detail['tl'])
            return -1
        return -2
    
    def all_data(self) -> dict:
        with self.lock:
            filtered_dict = {key: data for key, data in self.key_value_pairs.items() if not self.is_expired(data)}
            return filtered_dict
    

