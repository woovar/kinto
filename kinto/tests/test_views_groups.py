from .support import (BaseWebTest, unittest, MINIMALIST_BUCKET,
                      MINIMALIST_GROUP)


class GroupViewTest(BaseWebTest, unittest.TestCase):

    collection_url = '/buckets/beers/groups'
    record_url = '/buckets/beers/groups/moderators'

    def setUp(self):
        super(GroupViewTest, self).setUp()
        self.app.put_json('/buckets/beers', {'data': MINIMALIST_BUCKET},
                          headers=self.headers)
        resp = self.app.put_json(self.record_url,
                                 {'data': MINIMALIST_GROUP},
                                 headers=self.headers)
        self.record = resp.json['data']

    def test_collection_endpoint_lists_them_all(self):
        resp = self.app.get(self.collection_url, headers=self.headers)
        records = resp.json['data']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['members'], ['fxa:user'])

    def test_groups_can_be_posted_without_id(self):
        resp = self.app.post_json(self.collection_url,
                                  {'data': MINIMALIST_GROUP},
                                  headers=self.headers,
                                  status=201)
        self.assertIn('id', resp.json['data'])
        self.assertEqual(resp.json['data']['members'], ['fxa:user'])

    def test_groups_can_be_put_with_simple_name(self):
        self.assertEqual(self.record['id'], 'moderators')

    def test_groups_name_should_be_simple(self):
        self.app.put_json('/buckets/beers/groups/__moderator__',
                          {'data': MINIMALIST_GROUP},
                          headers=self.headers,
                          status=400)

    def test_unknown_bucket_raises_403(self):
        other_bucket = self.collection_url.replace('beers', 'sodas')
        self.app.get(other_bucket, headers=self.headers, status=403)

    def test_groups_are_isolated_by_bucket(self):
        other_bucket = self.record_url.replace('beers', 'sodas')
        self.app.put_json('/buckets/sodas',
                          MINIMALIST_BUCKET,
                          headers=self.headers)
        self.app.get(other_bucket, headers=self.headers, status=404)


class GroupDeletionTest(BaseWebTest, unittest.TestCase):

    group_url = '/buckets/beers/groups/moderators'

    def setUp(self):
        super(GroupDeletionTest, self).setUp()
        self.add_permission('/buckets', 'bucket:create')
        self.add_permission('/buckets/beers', 'write')
        self.app.put_json('/buckets/beers', {'data': MINIMALIST_BUCKET},
                          headers=self.headers, status=201)

    def test_groups_can_be_deleted(self):
        self.app.put_json(self.group_url, {'data': MINIMALIST_GROUP},
                          headers=self.headers)
        self.app.delete(self.group_url, headers=self.headers)
        self.app.get(self.group_url, headers=self.headers,
                     status=404)

    def test_principal_is_removed_from_users_when_group_deleted(self):
        self.add_permission('/buckets/beers/groups', 'group:create')
        self.app.put_json(self.group_url, {'data': MINIMALIST_GROUP},
                          headers=self.headers, status=201)
        self.assertIn(self.group_url,
                      self.permission.user_principals('fxa:user'))

        self.add_permission('/buckets/beers/groups/moderators', 'write')
        self.app.delete(self.group_url, headers=self.headers, status=200)
        self.assertNotIn(self.group_url,
                         self.permission.user_principals('fxa:user'))


class InvalidGroupTest(BaseWebTest, unittest.TestCase):

    group_url = '/buckets/beers/groups/moderators'

    def setUp(self):
        super(InvalidGroupTest, self).setUp()
        self.app.put_json('/buckets/beers', {'data': MINIMALIST_BUCKET},
                          headers=self.headers)

    def test_groups_must_have_members_attribute(self):
        invalid = {}
        self.app.put_json(self.record_url,
                          invalid,
                          headers=self.headers,
                          status=400)


class GroupPrincipalsTest(BaseWebTest, unittest.TestCase):

    def test_principal_is_added_to_user_when_added_to_members(self):
        pass

    def test_principal_is_removed_from_user_when_removed_from_members(self):
        pass
