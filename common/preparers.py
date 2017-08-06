class DefaultPreparer(object):
    model = None
    model_type = ''
    attributes = []
    relationships = {}

    def _prepare_single(self, instance):
        data = {}
        # Add mendatory Fields
        data['id'] = instance.id
        data['type'] = self.model_type

        attributes_data = {}
        for attribute in self.attributes:
            attributes_data[attribute] = getattr(instance, attribute)
        data['attributes'] = attributes_data

        if not hasattr(self, '_includes'):
            self._includes = {}

        relationships_data = {}
        for relation in self.relationships.keys():
            relation_type = relation
            relation_objects = getattr(instance, relation)
            if relation_objects:
                if type(relation_objects) == list:
                    relationship_data = []
                    for relation_instance in relation_objects:
                        relation_instance_data = {
                            'type': relation_type,
                            'id': relation_instance.id
                        }
                        relationship_data.append(relation_instance_data)
                        self._includes['%s,%d' %
                                       (relation_type, relation_instance.id)] = relation_instance
                else:
                    relationship_data = {}
                    relationship_data['id'] = relation_objects.id
                    relationship_data['type'] = relation_type
                    self._includes['%s,%d' %
                                   (relation_type, relation_objects.id)] = relation_objects
                relationships_data[relation_type] = relationship_data
        if relationships_data:
            data['relationships'] = relationships_data
        return data

    def prepare(self, instance, add_included=True):
        response = {}
        if type(instance) == list:
            data = []
            for i in instance:
                data.append(self._prepare_single(i))
        else:
            data = self._prepare_single(instance)

        if add_included and self._includes:
            included_data = []
            for include, instance in self._includes.items():
                include_type = include.split(',', 1)[0]
                include_data = self.relationships[include_type]().prepare(instance, False)
                included_data.append(include_data)
            response['included'] = included_data

        response['data'] = data
        return response
