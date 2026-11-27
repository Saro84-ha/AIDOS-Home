import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'aidos'/'app'))
import server

class SettingsTests(unittest.TestCase):
    def test_defaults(self):
        c=server.clean_settings({})
        self.assertFalse(c['notifications']['enabled'])
        self.assertEqual(len(c['pages']),7)
    def test_notification_service_restricted(self):
        c=server.clean_settings({'notifications':{'enabled':True,'service':'lock.unlock'}})
        self.assertEqual(c['notifications']['service'],'persistent_notification.create')
    def test_cards(self):
        c=server.clean_settings({'cards':[{'id':'one','page':'home','entity_id':'light.kitchen','type':'light','notify':True}]})
        self.assertEqual(c['cards'][0]['entity_id'],'light.kitchen')
        self.assertTrue(c['cards'][0]['notify'])
    def test_bad_card_is_ignored(self):
        c=server.clean_settings({'cards':[{'id':'one','page':'home','entity_id':'invalid/entity'}]})
        self.assertEqual(c['cards'],[])
    def test_io(self):
        with tempfile.TemporaryDirectory() as d:
            old=server.DATA;server.DATA=Path(d)
            try:
                c=server.read_settings();c['title']='Casa Uno'
                server.write_settings(c)
                self.assertEqual(server.read_settings()['title'],'Casa Uno')
            finally:server.DATA=old

if __name__=='__main__':unittest.main()
