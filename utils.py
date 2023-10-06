import yaml

def read_config():
    with open('config.yaml', encoding='utf8') as fp:
        config = yaml.safe_load(fp)
    return config

def save_config(config):
    with open('config.yaml', 'w', encoding='utf8') as fp:
        yaml.dump(config, fp, allow_unicode=True)