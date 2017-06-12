#!/usr/bin/env python
from cloudify import ctx


def delete():

    ctx.instance.runtime_properties['existing_resource_string'] = None


if __name__ == '__main__':

    resources = ctx.instance.runtime_properties.get('existing_resource_string',
                                                    '')
    ctx.logger.debug('Deleting existing resource string: {0}'
                     .format(resources))
    delete()
    ctx.logger.debug('Existing resource string was successfully deleted')
