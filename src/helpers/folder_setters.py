import os

class FolderSetters:
    @staticmethod
    def setFolders(dir_path:str, py_env:str):
        try:
            fs = {}
            match py_env:
                case 'dev':
                    fs['config_filename'] = "development.toml"
                    fs['config_folder'] = os.path.join(dir_path, "..","config")
                    fs['log_folder'] = os.path.join(dir_path, "..","logging")
                    fs['graphs_folder'] = os.path.join(dir_path, "..","..", "graphs")
                case 'test':
                    fs['config_filename'] = "development.toml"
                    fs['config_folder'] = os.path.join(dir_path, "config")
                    fs['log_folder'] = os.path.join(dir_path, "logging")
                    fs['graphs_folder'] = os.path.join(dir_path, "..", "graphs")
                case 'prod':
                    fs['config_filename'] = "production.toml"
                    fs['config_folder'] = os.path.join(dir_path, 'config')
                    fs['log_folder'] = os.path.join(dir_path, "logging")
                    fs['graphs_folder'] = os.path.join(dir_path, "graphs")
                case _:
                    pass

            return fs
        except Exception as e:
            return False