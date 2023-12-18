class Flattener:
    def __init__(self):
        self.flat_list = []

    def flatten(self, nested_list):
        def flatten_recursively(nested_list):
            for element in nested_list:
                if isinstance(element, list):
                    flatten_recursively(element)
                else:
                    self.flat_list.append(element)
        
        flatten_recursively(nested_list)
        return self.flat_list
