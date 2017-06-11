#!/usr/bin/env python
from cloudify import ctx


def create(dict):

    inputs = '-i use_external_resource=true '
    for key, value in dict.iteritems():
        inputs += ("%s %s=%s " % ('-i', key, value))
    ctx.logger.info('existing_resource_string: {0}'.format(inputs))
    ctx.instance.runtime_properties['existing_resource_string'] = inputs


def find_rels_by_node_type(node_instance, node_type):
    return [x for x in node_instance.relationships
            if node_type in x.target.node.type_hierarchy]


if __name__ == '__main__':

    if not ctx.node.properties.get('use_external_resource', False):
        dict = {}
        resources = \
            find_rels_by_node_type(ctx.instance, 'cloudify.nodes.Root')
        for resource in resources:
            resource_id = \
                resource.target.instance.runtime_properties[
                    'aws_resource_id']
            node_id = \
                resource.target.instance.id
            dictofvalues = node_id.split('_')
            node_id = dictofvalues[0]
            if node_id not in dict.keys():
                dict[node_id] = resource_id
        create(dict)
        ctx.logger.debug('Existing resources string was successfully created')

    else:
        ctx.logger.debug('existing_resource_string already exists')
