class GeneratorInterface:
    def __init__(self, dc_loader, out_dir):
        self.dc_loader = dc_loader
        self.outDir = out_dir

    def start(self):
        raise NotImplementedError

    def generate_dc_interfaces(self):
        raise NotImplementedError

    def generate_remote_interfaces(self):
        raise NotImplementedError

    def generate_remotes(self):
        raise NotImplementedError

    def generate_struct_parsing(self):
        raise NotImplementedError

    def generate_object_init(self):
        raise NotImplementedError

    def generate_function_parsing(self):
        raise NotImplementedError

    def generate_mapping(self):
        raise NotImplementedError

    def copy_static_files(self):
        raise NotImplementedError
