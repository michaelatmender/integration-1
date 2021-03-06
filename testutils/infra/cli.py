# Copyright 2018 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import testutils.infra.docker as docker

class CliUseradm:
    def __init__(self, docker_prefix=None):
        filt = ['mender-useradm']
        if docker_prefix is not None:
            filt.append(docker_prefix)

        self.cid = docker.getid(filt)

        # is it an open useradm, or useradm-enterprise?
        for path in ['/usr/bin/useradm', '/usr/bin/useradm-enterprise']:
            try:
                docker.execute(self.cid, [path, '--version'])
                self.path=path
            except:
                continue

        if self.path is None:
            raise RuntimeError('no runnable binary found in mender-useradm')


    def create_user(self, username, password, tenant_id=''):
        cmd = [self.path,
               'create-user',
               '--username', username,
               '--password', password]

        if tenant_id != '':
            cmd += ['--tenant-id', tenant_id]

        uid=docker.execute(self.cid, cmd)
        return uid


    def migrate(self, tenant_id=None):
        cmd = [self.path,
               'migrate']

        if tenant_id is not None:
            cmd.extend(['--tenant', tenant_id])

        docker.execute(self.cid, cmd)


class CliTenantadm:
    def __init__(self, docker_prefix=None):
        filt = ['mender-tenantadm']
        if docker_prefix is not None:
            filt.append(docker_prefix)

        self.cid = docker.getid(filt)

    def create_tenant(self, name):
        cmd = ['/usr/bin/tenantadm',
               'create-tenant',
               '--name', name]

        tid = docker.execute(self.cid, cmd)
        return tid

    def create_org(self, name, username, pwd):
        cmd = ['/usr/bin/tenantadm',
               'create-org',
               '--name', name,
               '--username', username,
               '--password', pwd]

        tid = docker.execute(self.cid, cmd)
        return tid

    def get_tenant(self, tid):
        cmd = ['/usr/bin/tenantadm',
               'get-tenant',
               '--id', tid]

        tenant = docker.execute(self.cid, cmd)
        return tenant

    def migrate(self):
        cmd = ['usr/bin/tenantadm',
               'migrate']

        docker.execute(self.cid, cmd)

class CliDeviceauth:
    def __init__(self, docker_prefix=None):
        filt = ['mender-device-auth']
        if docker_prefix is not None:
            filt.append(docker_prefix)

        self.cid = docker.getid(filt)

    def migrate(self, tenant_id=None):
        cmd = ['usr/bin/deviceauth',
               'migrate']

        if tenant_id is not None:
            cmd.extend(['--tenant', tenant_id])

        docker.execute(self.cid, cmd)

    def add_default_tenant_token(self, tenant_token):
        """
        Stops the container, adds the default_tenant_token to the config file
        at '/etc/deviceauth/config.yaml, and starts the container back up.

        :param tenant_token - 'the default tenant token to set'
        """

        # Append the default_tenant_token in the config ('/etc/deviceauth/config.yaml')
        cmd = ['/bin/sed', '-i', '$adefault_tenant_token: {}'.format(tenant_token), '/etc/deviceauth/config.yaml']
        docker.execute(self.cid, cmd)

        # Restart the container, so that it is picked up by the device-auth service on startup
        docker.cmd(self.cid, 'stop')
        docker.cmd(self.cid, 'start')
