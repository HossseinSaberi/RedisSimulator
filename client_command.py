import argparse
import inspect
from exceptions import IllegalArgumentError, InvalidSetError
from redis_simulator import RedisSimulator


class CommandLineProcessor:
    def __init__(self, rs: RedisSimulator):
        self.rs = rs
        self.rs.load_state()
        self.parser = argparse.ArgumentParser(description='Redis Simulator',exit_on_error=False)
        self.command_line_initialize()

    def process_command_line(self) -> None:
        while True:
            try:
                user_input = input("->  ")
                args, argv = self.parser.parse_known_args(user_input.split())
                if argv:
                    raise IllegalArgumentError(f"Illegal Argument: {' , '.join(argv)} \nUse -h or --help to more information!")
                self.call_crud_functions(args)

            except IllegalArgumentError as e :
                print(f"Error : {e}")
            except argparse.ArgumentError as e :
                print(f"Error : {e.message}")
            except Exception as e:
                print(f"{e}")

    def call_crud_functions(self, args):
        command_mapping = {
                    'SET': self.rs.set_data,
                    'GET': self.rs.get_data,
                    'DEL': self.rs.delete_data,
                    'TTL': self.rs.ttl_data,
                    'ALL': self.rs.all_data
                }
        args = self.clean_data(args)
        if args.command in command_mapping:
            func = command_mapping[args.command]
            params = inspect.signature(func).parameters
            func_args = {k: getattr(args, k) for k in params.keys() if k in vars(args)}
            result = func(**func_args)
            print(result)
        else:
            raise IllegalArgumentError('Unknown command')

    def command_line_initialize(self) -> None:
        subparser = self.parser.add_subparsers(dest='command')
        self.set_parser(subparser)
        self.get_parser(subparser)
        self.del_parser(subparser)
        self.ttl_parser(subparser)
        self.all_parser(subparser)

    def set_parser(self, subparsers: argparse._SubParsersAction) -> None:
        set_parser = subparsers.add_parser('SET', help='Set a key-value pair with an optional time-to-live')
        set_parser.add_argument('key', help='Key for the set operation')
        set_parser.add_argument('value', help='Value for the set operation, Use Comma Separation to set iterator')
        set_parser.add_argument('--ttl', help='Time-to-live for the key')
        set_parser.add_argument('--set', default=False, help='Set it True to want send Set')

    def get_parser(self, subparsers: argparse._SubParsersAction) -> None:
        get_parser = subparsers.add_parser('GET', help='Get the value for a key')
        get_parser.add_argument('key', help='Key for the get operation')

    def del_parser(self, subparsers: argparse._SubParsersAction) -> None:
        del_parser = subparsers.add_parser('DEL', help='Delete a key')
        del_parser.add_argument('key', help='Key to delete')

    def ttl_parser(self, subparsers: argparse._SubParsersAction) -> None:
        ttl_parser = subparsers.add_parser('TTL', help='Time To Live')
        ttl_parser.add_argument('key', help='Time to live of key')

    def all_parser(self, subparsers: argparse._SubParsersAction) -> None:
        subparsers.add_parser('ALL', help='ALL DATA')

    @staticmethod
    def clean_data(args: argparse.Namespace) -> argparse.Namespace:
        try:
            if args.command == 'SET':
                values = args.value.split(',')
                if len(values) > 1:
                    if args.set in ['True', 'true']:
                        args.value = set(values)
                    elif args.set in [False,'False','false']:
                        args.value = values
                    else:
                        args.value = values
                        raise InvalidSetError('Warning : Wrong Type for --set , --set must be boolean , --set ignored!')
                else:
                    args.value = values[0]

        except InvalidSetError as e:
            print(e)
        return args


if __name__ == '__main__':
    rs = RedisSimulator()
    kv_store = CommandLineProcessor(rs)
    kv_store.process_command_line()
