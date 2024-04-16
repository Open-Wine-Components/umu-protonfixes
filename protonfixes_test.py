import unittest
import fix
import os

class TestProtonfixes(unittest.TestCase):
    def setUp(self):
        self.env = {
            'STORE': ''
        }

    def tearDown(self):
        for key, val in self.env.items():
            if key in os.environ:
                os.environ.pop(key)

    def testModuleName(self):
        """Pass a non-numeric game id
        
        Expects a string that refers to a module in gamefixes-umu
        """
        game_id = 'umu-default'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.umu-default')

    def testModuleNameNum(self):
        """Pass a numeric game id
        
        In this case, it's assumed the game is from Steam when the game id is
        numeric
        Expects a string that refers to a module in gamefixes-steam
        """
        game_id = '1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameStore(self):
        """Pass a non-numeric game id and setting valid STORE
        
        For non-numeric game ids, the umu database should always be referenced
        Expects a string that refers to a module in gamefixes-$STORE
        """
        os.environ['STORE'] = 'GOG'
        store = os.environ['STORE']
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-gog.{game_id}')

    def testModuleNameNoStore(self):
        """Pass a non-numeric game id and setting an invalid STORE
        
        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = 'foo'
        store = os.environ['STORE']
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameStoreEmpty(self):
        """Pass a non-numeric game id and setting an empty store
        
        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = ''
        store = os.environ['STORE']
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameEmpty(self):
        """Pass empty strings for the game id and store"""
        os.environ['STORE'] = ''
        store = os.environ['STORE']
        game_id = ''
        result = fix.get_module_name(game_id)
        # TODO Handle the empty string case in fix.py
        # While umu enforces setting a gameid, it would still be a good idea
        # to handle this case
        self.assertEqual(result, f'protonfixes.gamefixes-umu.')

    def testModuleNameDefault(self):
        """Pass a gameid and default=True"""
        game_id = '1091500'
        result = fix.get_module_name(game_id, default=True)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.default')

    def testModuleNameLocal(self):
        """Pass a gameid and local=True"""
        game_id = '1091500'
        result = fix.get_module_name(game_id, local=True)
        self.assertEqual(result, f'localfixes.{game_id}')

    def testModuleNameLocalDefault(self):
        """Pass a gameid and set local=True,default=True
        
        In this case, the game id will be completely ignored
        """
        game_id = '1091500'
        result = fix.get_module_name(game_id, local=True, default=True)
        self.assertEqual(result, f'localfixes.default')

if __name__ == '__main__':
    unittest.main()
