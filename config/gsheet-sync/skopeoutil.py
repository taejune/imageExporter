
import subprocess
import re

class SkopeoUtil:
    CHECKCMD = 'skopeo inspect docker://{IMAGE}'
    CHECKCMD_WITH_CRED = 'skopeo inspect --creds={CRED} docker://{IMAGE}'
    COPYCMD = 'skopeo copy --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'
    COPYCMD_WITH_CRED = 'skopeo copy --src-creds={CRED} --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'

    def __init__(self, registries):
        self.registries = registries

    def check_image(self, name):
        print('Check if exist image:', name, '...')
        for reg in self.registries.values():
            if re.compile(reg['regex']).search(name) != None:
                try:
                    if len(reg['credential']) > 0:
                        subprocess.run(self.CHECKCMD_WITH_CRED.format(IMAGE=name, CRED=reg['credential']), check=True, shell=True, capture_output=True).check_returncode()
                    else:
                        subprocess.run(self.CHECKCMD.format(IMAGE=name), check=True, shell=True, capture_output=True).check_returncode()
                    return (name, True)
                except subprocess.SubprocessError as e:
                    print(e.stderr)
                    return (name, False)
        try:
            subprocess.run(self.CHECKCMD_WITH_CRED.format(IMAGE=name, CRED=self.registries['docker.io']['credential']), check=True, shell=True, capture_output=True).check_returncode()
            return (name, True)
        except subprocess.SubprocessError as e:
            print(e.stderr)
            return (name, False)

    def copy_image(self, name, copy_to):
        print('Copying image:', name, '...')
        for reg in self.registries.values():
            if re.compile(reg['regex']).search(name) != None:
                try:
                    if len(reg['credential']) > 0:
                        subprocess.run(self.COPYCMD_WITH_CRED.format(IMAGE=name, CRED=reg['credential'], DEST=copy_to), check=True, shell=True, capture_output=True).check_returncode()
                    else:
                        subprocess.run(self.COPYCMD.format(IMAGE=name, DEST=copy_to), check=True, shell=True, capture_output=True).check_returncode()
                    return (name, True)
                except subprocess.SubprocessError as e:
                    print(e.stderr)
                    return (name, False)
        try:
            subprocess.run(self.COPYCMD_WITH_CRED.format(IMAGE=name, CRED=self.registries['docker.io']['credential'], DEST=copy_to), check=True, shell=True, capture_output=True).check_returncode()
            return (name, True)
        except subprocess.SubprocessError as e:
            print(e.stderr)
            return (name, False)
