import argparse
import inspect
from exceptions import IllegalArgumentError
from redis_simulator import RedisSimulator

class CommandLineProccessor:
    
    def  __init__(self, rs: RedisSimulator):
        self.rs = rs
        self.command_line_initialize()


    def process_command_line(self) -> None:
        self.rs.load_state() 
        args = self.parser.parse_args()
        command_mapping = {
            'SET' : self.rs.set_data,
            'GET' : self.rs.get_data,
            'DEL' : self.rs.delete_data,
            'TTL' : self.rs.ttl_data
        }

        if args.command in command_mapping:
            func = command_mapping[args.command]
            params = inspect.signature(func).parameters
            func_args = {k: getattr(args, k) for k in params.keys() if k in vars(args)}
            result = func(**func_args)
            print(result)
        else:
            raise IllegalArgumentError('Unknown command')


    def command_line_initialize(self) -> None:
        self.parser = argparse.ArgumentParser(description='Redis Simulator')
        subparser = self.parser.add_subparsers(dest='command')
        self.set_parser(subparser)
        self.get_parser(subparser)
        self.del_parser(subparser)
        self.ttl_parser(subparser)
       

    def set_parser(self, subparsers: argparse._SubParsersAction) -> None:

        set_parser = subparsers.add_parser('SET', help='Set a key-value pair with an optional time-to-live')
        set_parser.add_argument('key', help='Key for the set operation')
        set_parser.add_argument('value', help='Value for the set operation')
        set_parser.add_argument('--ttl', type=int, help='Time-to-live for the key')


    def get_parser(self, subparsers: argparse._SubParsersAction) -> None:

        get_parser = subparsers.add_parser('GET', help='Get the value for a key')
        get_parser.add_argument('key', help='Key for the get operation')


    def del_parser(self, subparsers: argparse._SubParsersAction) -> None:

        del_parser = subparsers.add_parser('DEL', help='Delete a key')
        del_parser.add_argument('key', help='Key to delete')

    def ttl_parser(self, subparsers: argparse._SubParsersAction) -> None:

        ttl_parser = subparsers.add_parser('TTL', help='Time To Live')
        ttl_parser.add_argument('key', help='Time to live of key')


if __name__ == '__main__':
    rs = RedisSimulator()
    kv_store = CommandLineProccessor(rs)
    kv_store.process_command_line()