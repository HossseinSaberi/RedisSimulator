from exceptions import InvalidSetError

class CleanDataValueMixin:
    def handle_set_command(self, args):
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