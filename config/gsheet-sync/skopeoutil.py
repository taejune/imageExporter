import subprocess
import re

class SkopeoUtil:
    CHECK = 'skopeo inspect docker://{IMAGE}'
    CRED_CHECK = 'skopeo inspect --creds={CRED} docker://{IMAGE}'
    COPYCMD = 'skopeo copy --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'
    CRED_COPY = 'skopeo copy --src-creds={CRED} --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'

    def __init__(self, registries):
        self.registries = registries

    def check_image(self, name):
        cmd = self.CRED_CHECK.format(IMAGE=name, CRED=self.registries['docker.io']['cred'])
        for reg in self.registries.values():
            if reg['regex'].search(name) != None:
                if len(reg['cred']) > 0:
                    cmd = self.CRED_CHECK.format(IMAGE=name, CRED=reg['cred'])
                else:
                    cmd = self.CHECK.format(IMAGE=name)
                break
        try:
            print(cmd)
            subprocess.run(cmd, check=True, shell=True, capture_output=True).check_returncode()
            return (name, True, '')
        except subprocess.SubprocessError as e:
            return (name, False, str(e.stderr, 'utf-8'))

    def copy_image(self, name, copy_to):
        cmd = self.CRED_COPY.format(IMAGE=name, CRED=self.registries['docker.io']['cred'], DEST=copy_to)
        for reg in self.registries.values():
            if reg['regex'].search(name) != None:
                if len(reg['cred']) > 0:
                    cmd = self.CRED_COPY.format(IMAGE=name, CRED=reg['cred'], DEST=copy_to)
                else:
                    cmd = self.COPYCMD.format(IMAGE=name, DEST=copy_to)
                break
        try:
            print(cmd)
            subprocess.run(cmd, check=True, shell=True, capture_output=True).check_returncode()
            return (name, True, '')
        except subprocess.SubprocessError as e:
            return (name, False, str(e.stderr, 'utf-8'))