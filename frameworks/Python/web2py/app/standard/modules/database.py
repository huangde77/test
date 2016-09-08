# -*- coding: utf-8 -*-
import os
from operator import itemgetter
from gluon.storage import Storage
from gluon.dal import DAL, Field, Row

DBHOST = os.environ.get('DBHOST', 'localhost')
DATABASE_URI = 'mysql://benchmarkdbuser:benchmarkdbpass@%s:3306/hello_world' % DBHOST

class Dal(object):
    def __init__(self, table=None, pool_size=8):
        self.db = DAL(DATABASE_URI, migrate_enabled=False, pool_size=pool_size)
        if table == 'World':
            self.db.define_table('World', Field('randomNumber', 'integer'))
        elif table == 'Fortune':
            self.db.define_table('Fortune', Field('message'))

    def get_world(self, wid):
        return self.db(self.db.World.id == wid).select(cacheable=True)[0].as_dict()

    def update_world(self, wid, randomNumber):
        self.db(self.db.World.id == wid).update(randomNumber=randomNumber)

    def get_fortunes(self, new_message):
        fortunes = self.db(self.db.Fortune).select(cacheable=True)
        fortunes.records.append(Row(new_message))
        return fortunes.sort(itemgetter('message'))

class RawDal(Dal):
    def __init__(self):
        super(RawDal, self).__init__()
        self.world_updates = []

    def get_world(self, wid):
        return self.db.executesql('SELECT * FROM World WHERE id = %s',
                                  placeholders=[wid], as_dict=True)[0]

    def update_world(self, wid, randomNumber):
        self.world_updates.extend([randomNumber, wid])

    def flush_world_updates(self):
        query = ';'.join('UPDATE World SET randomNumber=%s WHERE id=%s'
                         for _ in xrange(len(self.world_updates) / 2))
        self.db.executesql(query, placeholders=self.world_updates)

    def get_fortunes(self, new_message):
        fortunes = self.db.executesql('SELECT * FROM Fortune', as_dict=True)
        fortunes.append(new_message)
        return sorted(fortunes, key=itemgetter('message'))

def num_queries(queries):
    try:
        num = int(queries)
        return 1 if num < 1 else 500 if num > 500 else num
    except ValueError:
         return 1
