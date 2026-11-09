import os
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch, mock_open

from . import fix
from . import util


class TestProtonfixes(unittest.TestCase):
    def setUp(self):
        self.env = {
            'STORE': '',
            'SteamAppId': '',
            'SteamGameId': '',
            'STEAM_COMPAT_DATA_PATH': '',
            'UMU_ID': '',
            'DEBUG': '',
        }
        self.game_id = '1293820'
        self.pfx = Path(tempfile.mkdtemp())
        self.db = Path(tempfile.mktemp())
        self.db_data = (
            "TITLE,STORE,CODENAME,UMU_ID,COMMON ACRONYM (Optional),NOTE (Optional)\n"
            "Age of Wonders,gog,1207658883,umu-61500,aow,\n"
            "Age of Wonders,humble,ageofwonders,umu-61500,aow,\n"
            "Red Dead Redemption 2,none,none,umu-1174180,rdr2,Standalone Rockstar installer"
        )
        self.db.write_text(self.db_data, encoding="utf-8")

    def tearDown(self):
        for key in self.env:
            if key in os.environ:
                os.environ.pop(key)
        if self.pfx.is_dir():
            if self.pfx.joinpath('steamapps').is_dir():
                self.pfx.joinpath('steamapps', 'appmanifest_1628350.acf').unlink(
                    missing_ok=True
                )
                self.pfx.joinpath('steamapps').rmdir()
            self.pfx.joinpath('game_title').unlink(missing_ok=True)
            self.pfx.rmdir()
        Path(self.db).unlink(missing_ok=True)


    def testModuleName(self):
        """Pass a non-numeric game id

        Expects a string that refers to a module in gamefixes-umu
        """
        game_id = 'umu-default'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, 'protonfixes.gamefixes-umu.umu-default')

    def testModuleNameNum(self):
        """Pass a numeric game id

        In this case, it's assumed the game is from Steam when the game id is
        numeric
        Expects a string that refers to a module in gamefixes-steam
        """
        game_id = '1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameNoneAndNumeric(self):
        """Pass a numeric gameid and set STORE

        In this case, when the game id is numeric, we always refer to a
        module in the gamefixes-steam.
        """
        game_id = '1091500'
        os.environ['STORE'] = 'none'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameStoreAndNumeric(self):
        """Pass a numeric gameid and set STORE

        In this case, when the game id is numeric, we always refer to a
        module in gamefixes-steam
        When passed a valid store, that value should not be used
        """
        game_id = '1091500'
        os.environ['STORE'] = 'gog'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameStore(self):
        """Pass a non-numeric game id and setting valid STORE

        For non-numeric game ids, the umu database should always be referenced
        Expects a string that refers to a module in gamefixes-$STORE
        """
        os.environ['STORE'] = 'GOG'
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-gog.{game_id}')

    def testModuleNameNoStore(self):
        """Pass a non-numeric game id and setting an invalid STORE

        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = 'foo'
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameStoreEmpty(self):
        """Pass a non-numeric game id and setting an empty store

        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = ''
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameEmpty(self):
        """Pass empty strings for the game id and store"""
        os.environ['STORE'] = ''
        game_id = ''
        result = fix.get_module_name(game_id)
        # TODO Handle the empty string case in fix.py
        # While umu enforces setting a gameid, it would still be a good idea
        # to handle this case
        self.assertEqual(result, 'protonfixes.gamefixes-umu.')

    def testModuleNameDefault(self):
        """Pass a gameid and default=True"""
        game_id = '1091500'
        result = fix.get_module_name(game_id, default=True)
        self.assertEqual(result, 'protonfixes.gamefixes-steam.default')

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
        self.assertEqual(result, 'localfixes.default')

    def testGetGameSteamAppId(self):
        """Only set the SteamAppId

        Protonfixes depends on being supplied an app id when applying fixes
        to games.

        This appid is typically set by a client application, but the user can
        set it in some cases (e.g., umu-launcher).

        If the app id is numeric, then protonfixes will refer to the
        gamefixes-steam folder. Otherwise, the STORE environment variable will
        be used to determine which fix will be applied.
        """
        os.environ['SteamAppId'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('SteamAppId'), 'SteamAppId was unset')

    def testGetGameUmuId(self):
        """Only set the UMU_ID"""
        os.environ['UMU_ID'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('UMU_ID'), 'UMU_ID was unset')

    def testGetGameSteamGameId(self):
        """Only set the SteamGameId"""
        os.environ['SteamGameId'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('SteamGameId'), 'SteamGameId was unset')

    def testGetGameCompatPath(self):
        """Only set the STEAM_COMPAT_DATA_PATH"""
        os.environ['STEAM_COMPAT_DATA_PATH'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(
            os.environ.get('STEAM_COMPAT_DATA_PATH'), 'STEAM_COMPAT_DATA_PATH was unset'
        )

    def testGetGameNone(self):
        """Set no environment variables

        Expect None to be returned
        """
        func = fix.get_game_id.__wrapped__  # Do not reference the cache
        self.assertTrue(
            'STEAM_COMPAT_DATA_PATH' not in os.environ, 'STEAM_COMPAT_DATA_PATH is set'
        )
        self.assertTrue('SteamGameId' not in os.environ, 'SteamGameId is set')
        self.assertTrue('UMU_ID' not in os.environ, 'UMU_ID is set')
        self.assertTrue('SteamAppId' not in os.environ, 'SteamAppId is set')
        with self.assertRaises(SystemExit):
            func()

    def testGetStoreNameZoom(self):
        """Pass zoomplatform as store name

        The get_store_name function returns a string associated with a
        supported store in the umu database.

        The string will be used to display a message in the console to let the
        user know which fix will be applied.
        """
        store = 'zoomplatform'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameAmazon(self):
        """Pass amazon as store name"""
        store = 'amazon'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameEA(self):
        """Pass ea as store name"""
        store = 'ea'
        result = fix.get_store_name(store)
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameEGS(self):
        """Pass egs as store name"""
        store = 'egs'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameGOG(self):
        """Pass gog as store name"""
        store = 'gog'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameHumble(self):
        """Pass humble as store name"""
        store = 'humble'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameItchio(self):
        """Pass itchio as store name"""
        store = 'itchio'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameSteam(self):
        """Pass steam as store name"""
        store = 'steam'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameUbisoft(self):
        """Pass ubisoft as store name"""
        store = 'ubisoft'
        result = fix.get_store_name(store)
        self.assertIsInstance(result, str, 'Expected a str')
        self.assertTrue(result, 'Expected a value')

    def testGetStoreNameEmpty(self):
        """Pass an empty string as store name"""
        store = ''
        result = fix.get_store_name(store)
        self.assertFalse(result, 'Expected None')

    def testGetStoreNameFoo(self):
        """Pass a store that is not supported in umu"""
        store = 'jastusa'
        result = fix.get_store_name(store)
        self.assertFalse(result, 'Expected None')

    def testGetGameNameDB(self):
        """Set UMU_ID and access umu database"""
        os.environ['UMU_ID'] = 'umu-35140'
        os.environ['STORE'] = 'gog'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()

        # Mock CSV content
        csv_content = """Batman: Arkham Asylum Game of the Year Edition,gog,1482504285,umu-35140,,"""

        with patch('builtins.open', mock_open(read_data=csv_content)):
            func = fix.get_game_name.__wrapped__  # Do not reference the cache
            result = func()
            self.assertEqual(result, 'Batman: Arkham Asylum Game of the Year Edition')

    def testGetGameNameDBFileNotFound(self):
        """Set UMU_ID and simulate FileNotFoundError for the CSV file"""
        os.environ['UMU_ID'] = 'umu-35140'
        os.environ['STORE'] = 'gog'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()

        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = FileNotFoundError
            with patch('protonfixes.fix.log') as mocked_log:  # Mock the logger separately
                func = fix.get_game_name.__wrapped__  # Do not reference the cache
                result = func()
                self.assertEqual(result, 'UNKNOWN')
                mocked_log.warn.assert_called_with(f"Game title not found in CSV")

    def testGetGameNameDbOS(self):
        """Set UMU_ID and simulate OSError when accessing the CSV file"""
        os.environ['UMU_ID'] = 'umu-35140'
        os.environ['STORE'] = 'gog'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()

        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = OSError
            with patch('protonfixes.fix.log') as mocked_log:  # Mock the logger separately
                func = fix.get_game_name.__wrapped__  # Do not reference the cache
                result = func()
                self.assertEqual(result, 'UNKNOWN')
                mocked_log.warn.assert_called_with("Game title not found in CSV")

    def testGetGameNameDbIndex(self):
        """Set UMU_ID and simulate IndexError with malformed CSV data"""
        os.environ['UMU_ID'] = 'umu-35140'
        os.environ['STORE'] = 'gog'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()

        # Mock CSV content with missing columns
        csv_content = """Batman: Arkham Asylum Game of the Year Edition,gog"""

        with patch('builtins.open', mock_open(read_data=csv_content)):
            func = fix.get_game_name.__wrapped__  # Do not reference the cache
            result = func()
            self.assertEqual(result, 'UNKNOWN')

    def testGetGameNameDbUnicode(self):
        """Set UMU_ID and simulate UnicodeDecodeError when reading the CSV file"""
        os.environ['UMU_ID'] = 'umu-35140'
        os.environ['STORE'] = 'gog'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()

        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, '')
            with patch('protonfixes.fix.log') as mocked_log:  # Mock the logger separately
                func = fix.get_game_name.__wrapped__  # Do not reference the cache
                result = func()
                self.assertEqual(result, 'UNKNOWN')
                mocked_log.warn.assert_called_with("Game title not found in CSV")

    def testGetGameNameNoManifest(self):
        """Do not set UMU_ID and try to get the title from the steam app library"""
        os.environ['SteamAppId'] = '1628350'
        os.environ['WINEPREFIX'] = self.pfx.as_posix()
        os.environ['PWD'] = os.environ['WINEPREFIX']
        steamapps = self.pfx.joinpath('steamapps')
        os.makedirs(steamapps, exist_ok=True)
        func = fix.get_game_name.__wrapped__  # Do not reference the cache
        result = func()
        self.assertEqual(result, 'UNKNOWN')

    def testGetTitleNameNoStore(self):
        """Pass a valid game id with a database entry but with no store

        Expects a string that refers to the game's title when STORE is falsey
        or unset when reading the CSV file
        """
        os.environ['WINEPREFIX'] = self.pfx.as_posix()
        os.environ['STORE'] = ''
        os.environ["UMU_ID"] = 'umu-1174180'
        result = fix.get_game_title(self.db.as_posix())
        self.assertEqual(result, 'Red Dead Redemption 2')

        # STORE is unset
        os.environ.pop('STORE')
        result = fix.get_game_title(self.db.as_posix())
        self.assertEqual(result, 'Red Dead Redemption 2')

    def testGetTitleNameNoEntry(self):
        """Pass a game id with no database entry

        Expects the string 'UNKNOWN' when STORE is falsey, unset or valid
        when reading the CSV file
        """
        os.environ['WINEPREFIX'] = self.pfx.as_posix()
        os.environ['STORE'] = ''
        os.environ["UMU_ID"] = 'umu-default'
        result = fix.get_game_title(self.db.as_posix())
        self.assertEqual(result, 'UNKNOWN')

        # STORE is unset
        os.environ.pop('STORE')
        result = fix.get_game_title(self.db.as_posix())
        self.assertEqual(result, 'UNKNOWN')

        # STORE is valid
        os.environ['STORE'] = 'gog'
        result = fix.get_game_title(self.db.as_posix())
        self.assertEqual(result, 'UNKNOWN')


class TestSteamVdf(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.client_dir = self.base_dir / 'steam_client'
        self.client_dir.mkdir(parents=True, exist_ok=True)
        self.current_prefix = self.base_dir / 'current_pfx'
        self.current_prefix.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_vdf_basic(self):
        """Verifies parsing of standard KeyValues hierarchy."""
        text = '"root"\n{\n\t"key1"\t"value1"\n\t"sub"\n\t{\n\t\t"key2"\t"value2"\n\t}\n}'
        data = util.parse_vdf(text)
        expected = {'root': {'key1': 'value1', 'sub': {'key2': 'value2'}}}
        self.assertEqual(data, expected)

    def test_parse_vdf_whitespace_crlf_and_comments(self):
        """Verifies handling of irregular tabs, spaces, CRLF line endings, and comments."""
        text = (
            '// Top comment\r\n'
            '"libraryfolders"\r\n'
            '{\r\n'
            '  // Space indentation\r\n'
            '  "0"\r\n'
            '  {\r\n'
            '\t\t"path"\t"/home/user/.steam/steam"\r\n'
            '    "label"   "" // trailing comment\r\n'
            '    "totalsize" 12345678\r\n'
            '  }\r\n'
            '}\r\n'
        )
        data = util.parse_vdf(text)
        self.assertIn('libraryfolders', data)
        self.assertEqual(data['libraryfolders']['0']['path'], '/home/user/.steam/steam')
        self.assertEqual(data['libraryfolders']['0']['totalsize'], '12345678')

    def test_parse_vdf_escapes(self):
        """Verifies unescaping of backslashes and quotes without corrupting \\t or \\n in paths."""
        text = '"entry"\n{\n\t"winpath"\t"C:\\\\tools\\\\new_folder"\n\t"msg"\t"hello \\"world\\""\n}'
        data = util.parse_vdf(text)
        self.assertEqual(data['entry']['winpath'], 'C:\\tools\\new_folder')
        self.assertEqual(data['entry']['msg'], 'hello "world"')

    def test_parse_vdf_utf8_bom(self):
        """Verifies parsing text containing UTF-8 BOM."""
        text = '\ufeff"libraryfolders"\n{\n\t"0"\n\t{\n\t\t"path"\t\t"/home/user/.steam"\n\t}\n}'
        data = util.parse_vdf(text)
        self.assertIn('libraryfolders', data)
        self.assertEqual(data['libraryfolders']['0']['path'], '/home/user/.steam')

    def test_parse_vdf_users_section(self):
        """Verifies parsing of loginusers user sections."""
        text = '"users"\n{\n\t"12345"\n\t{\n\t\t"AccountName"\t\t"gamer"\n\t}\n}'
        data = util.parse_vdf(text)
        self.assertEqual(data, {'users': {'12345': {'AccountName': 'gamer'}}})

    def test_import_saves_folder_invalid_appid(self):
        """Verifies that invalid or non-zero ending AppIDs return False."""
        self.assertFalse(util.import_saves_folder(0, 'Saved Games'))
        self.assertFalse(util.import_saves_folder(-10, 'Saved Games'))
        self.assertFalse(util.import_saves_folder(12345, 'Saved Games'))

    def test_import_saves_folder_missing_client_env_or_file(self):
        """Verifies graceful False when environment variable or VDF file is missing."""
        with patch.dict(os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': ''}):
            self.assertFalse(util.import_saves_folder(123450, 'Saved Games'))

        with patch.dict(os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}):
            self.assertFalse(util.import_saves_folder(123450, 'Saved Games'))

    def test_import_saves_folder_success(self):
        """Verifies successful symlink creation from another game prefix across parsed library folders."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        library_path = self.base_dir / 'library1'
        library_vdf.write_text(
            f'"libraryfolders"\r\n{{\r\n  "0"\r\n  {{\r\n\t"path"\t"{library_path}"\r\n  }}\r\n}}\r\n',
            encoding='utf-8',
        )

        source_pfx_user = (
            library_path
            / 'steamapps'
            / 'compatdata'
            / '123450'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
        )
        source_saves = source_pfx_user / 'Saved Games' / 'MyGame'
        source_saves.mkdir(parents=True, exist_ok=True)
        (source_saves / 'save1.dat').write_text('save_data', encoding='utf-8')

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            result = util.import_saves_folder(123450, 'Saved Games/MyGame')
            self.assertTrue(result)

            goal = (
                self.current_prefix
                / 'pfx'
                / 'drive_c'
                / 'users'
                / 'steamuser'
                / 'Saved Games'
                / 'MyGame'
            )
            self.assertTrue(goal.is_symlink())
            self.assertEqual(goal.resolve(), source_saves.resolve())

    def test_import_saves_folder_demo_mode(self):
        """Verifies demo mode copying files without overwriting existing files."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        library_path = self.base_dir / 'library_demo'
        library_vdf.write_text(
            f'"libraryfolders"\n{{\n\t"0"\n\t{{\n\t\t"path"\t\t"{library_path}"\n\t}}\n}}\n',
            encoding='utf-8',
        )

        source_pfx_user = (
            library_path
            / 'steamapps'
            / 'compatdata'
            / '234560'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
        )
        source_saves = source_pfx_user / 'Saved Games'
        source_saves.mkdir(parents=True, exist_ok=True)
        (source_saves / 'demo_save.dat').write_text('demo_data', encoding='utf-8')
        (source_saves / 'common.dat').write_text('demo_common', encoding='utf-8')

        goal = (
            self.current_prefix
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
            / 'Saved Games'
        )
        goal.mkdir(parents=True, exist_ok=True)
        (goal / 'common.dat').write_text('existing_full_game_common', encoding='utf-8')

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            result = util.import_saves_folder(234560, 'Saved Games', is_demo=True)
            self.assertTrue(result)
            self.assertTrue((goal / 'demo_save.dat').is_file())
            # Existing full game file must be preserved
            self.assertEqual((goal / 'common.dat').read_text(encoding='utf-8'), 'existing_full_game_common')

    def test_import_saves_folder_relink_moved_prefix(self):
        """Verifies replacing a broken symlink when target was moved or re-pathed."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        library_path = self.base_dir / 'library_relink'
        library_vdf.write_text(
            f'"libraryfolders"\n{{\n\t"0"\n\t{{\n\t\t"path"\t\t"{library_path}"\n\t}}\n}}\n',
            encoding='utf-8',
        )

        source_pfx_user = (
            library_path
            / 'steamapps'
            / 'compatdata'
            / '345670'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
        )
        source_saves = source_pfx_user / 'Saved Games'
        source_saves.mkdir(parents=True, exist_ok=True)

        goal = (
            self.current_prefix
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
            / 'Saved Games'
        )
        goal.parent.mkdir(parents=True, exist_ok=True)
        deleted_target = self.base_dir / 'deleted_location'
        # Create a broken symlink pointing to a deleted path
        goal.symlink_to(deleted_target, True)
        self.assertTrue(goal.is_symlink())
        self.assertFalse(goal.resolve().exists())

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            result = util.import_saves_folder(345670, 'Saved Games')
            self.assertTrue(result)
            self.assertTrue(goal.is_symlink())
            self.assertEqual(goal.resolve(), source_saves.resolve())
            # Ensure broken target location was not modified or turned into a symlink
            self.assertFalse(deleted_target.exists())

    def test_import_saves_folder_legacy_format_and_casing(self):
        """Verifies handling of legacy LibraryFolders format where entries map to paths directly."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        library_path = self.base_dir / 'library_legacy'
        library_vdf.write_text(
            f'"LibraryFolders"\n{{\n\t"TimeNextStatsReport"\t"123456"\n\t"1"\t"{library_path}"\n}}\n',
            encoding='utf-8',
        )

        source_pfx_user = (
            library_path
            / 'steamapps'
            / 'compatdata'
            / '456780'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
        )
        source_saves = source_pfx_user / 'Saved Games' / 'LegacyGame'
        source_saves.mkdir(parents=True, exist_ok=True)
        (source_saves / 'legacy_save.dat').write_text('legacy_data', encoding='utf-8')

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            result = util.import_saves_folder(456780, 'Saved Games/LegacyGame')
            self.assertTrue(result)

            goal = (
                self.current_prefix
                / 'pfx'
                / 'drive_c'
                / 'users'
                / 'steamuser'
                / 'Saved Games'
                / 'LegacyGame'
            )
            self.assertTrue(goal.is_symlink())
            self.assertEqual(goal.resolve(), source_saves.resolve())

    def test_import_saves_folder_multi_library_empty_prefix_skipped(self):
        """Verifies that an empty compatdata prefix on one library is skipped to find the valid saves on another library."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        lib0 = self.base_dir / 'library_empty_pfx'
        lib1 = self.base_dir / 'library_valid_pfx'
        library_vdf.write_text(
            f'"libraryfolders"\n{{\n\t"0"\n\t{{\n\t\t"path"\t\t"{lib0}"\n\t}}\n\t"1"\n\t{{\n\t\t"path"\t\t"{lib1}"\n\t}}\n}}\n',
            encoding='utf-8',
        )

        # lib0 has compatdata folder for app 567890 but without the requested relative save folder
        (lib0 / 'steamapps' / 'compatdata' / '567890' / 'pfx' / 'drive_c' / 'users' / 'steamuser').mkdir(parents=True, exist_ok=True)

        # lib1 has the actual save folder
        source_saves = (
            lib1
            / 'steamapps'
            / 'compatdata'
            / '567890'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
            / 'Saved Games'
            / 'GameB'
        )
        source_saves.mkdir(parents=True, exist_ok=True)
        (source_saves / 'save.dat').write_text('save_data', encoding='utf-8')

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            result = util.import_saves_folder(567890, 'Saved Games/GameB')
            self.assertTrue(result)

            goal = (
                self.current_prefix
                / 'pfx'
                / 'drive_c'
                / 'users'
                / 'steamuser'
                / 'Saved Games'
                / 'GameB'
            )
            self.assertTrue(goal.is_symlink())
            self.assertEqual(goal.resolve(), source_saves.resolve())

    def test_import_saves_folder_windows_backslashes_and_leading_slash(self):
        """Verifies normalization of Windows backslashes and leading slashes in relative_path."""
        steamapps = self.client_dir / 'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        library_vdf = steamapps / 'libraryfolders.vdf'
        library_path = self.base_dir / 'library_winpath'
        library_vdf.write_text(
            f'"libraryfolders"\n{{\n\t"0"\n\t{{\n\t\t"path"\t\t"{library_path}"\n\t}}\n}}\n',
            encoding='utf-8',
        )

        source_saves = (
            library_path
            / 'steamapps'
            / 'compatdata'
            / '678910'
            / 'pfx'
            / 'drive_c'
            / 'users'
            / 'steamuser'
            / 'AppData'
            / 'Local'
            / 'MyGame'
        )
        source_saves.mkdir(parents=True, exist_ok=True)
        (source_saves / 'save.dat').write_text('win_data', encoding='utf-8')

        with patch.dict(
            os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        ), patch.object(util, 'protonprefix', return_value=str(self.current_prefix / 'pfx')):
            # Pass Windows-style backslashes and a leading slash
            result = util.import_saves_folder(678910, r'/AppData\Local\MyGame')
            self.assertTrue(result)

            goal = (
                self.current_prefix
                / 'pfx'
                / 'drive_c'
                / 'users'
                / 'steamuser'
                / 'AppData'
                / 'Local'
                / 'MyGame'
            )
            self.assertTrue(goal.is_symlink())
            self.assertEqual(goal.resolve(), source_saves.resolve())

    def test_import_saves_folder_empty_relative_path(self):
        """Verifies that empty relative_path returns False."""
        self.assertFalse(util.import_saves_folder(123450, ''))
        self.assertFalse(util.import_saves_folder(123450, '/'))
        self.assertFalse(util.import_saves_folder(123450, '\\'))

    def test_get_steam_account_id_matching_steam_user(self):
        """Verifies matching account ID using SteamUser environment variable."""
        config_dir = self.client_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        loginusers_vdf = config_dir / 'loginusers.vdf'
        loginusers_vdf.write_text(
            '"users"\r\n'
            '{\r\n'
            '  "76561198000000001"\r\n'
            '  {\r\n'
            '\t\t"AccountName"\t\t"alpha"\r\n'
            '  }\r\n'
            '  "76561198000000002"\r\n'
            '  {\r\n'
            '    "AccountName"    "beta"\r\n'
            '  }\r\n'
            '}\r\n',
            encoding='utf-8',
        )

        with patch.dict(
            os.environ,
            {
                'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir),
                'SteamUser': 'Beta',
            },
        ):
            account_id = util.get_steam_account_id()
            self.assertEqual(account_id, '76561198000000002')

    def test_get_steam_account_id_fallback_mostrecent(self):
        """Verifies falling back to user marked as most recent when SteamUser is not set."""
        config_dir = self.client_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        loginusers_vdf = config_dir / 'loginusers.vdf'
        loginusers_vdf.write_text(
            '"users"\n'
            '{\n'
            '\t"76561198000000001"\n'
            '\t{\n'
            '\t\t"AccountName"\t\t"alpha"\n'
            '\t\t"mostrecent"\t\t"0"\n'
            '\t}\n'
            '\t"76561198000000002"\n'
            '\t{\n'
            '\t\t"AccountName"\t\t"beta"\n'
            '\t\t"mostrecent"\t\t"1"\n'
            '\t}\n'
            '}\n',
            encoding='utf-8',
        )

        env = {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}
        if 'SteamUser' in os.environ:
            env_to_pop = 'SteamUser'
        else:
            env_to_pop = None

        with patch.dict(os.environ, env):
            if env_to_pop:
                os.environ.pop('SteamUser', None)
            account_id = util.get_steam_account_id()
            self.assertEqual(account_id, '76561198000000002')

    def test_get_steam_account_id_fallback_single_user(self):
        """Verifies falling back to sole user in loginusers.vdf when SteamUser is unset."""
        config_dir = self.client_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        loginusers_vdf = config_dir / 'loginusers.vdf'
        loginusers_vdf.write_text(
            '"users"\n{\n\t"76561198000000099"\n\t{\n\t\t"AccountName"\t\t"only_user"\n\t}\n}\n',
            encoding='utf-8',
        )

        with patch.dict(os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}):
            os.environ.pop('SteamUser', None)
            account_id = util.get_steam_account_id()
            self.assertEqual(account_id, '76561198000000099')

    def test_get_steam_account_id_steam_base_folder(self):
        """Verifies account ID resolution when using STEAM_BASE_FOLDER."""
        config_dir = self.client_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        loginusers_vdf = config_dir / 'loginusers.vdf'
        loginusers_vdf.write_text(
            '"users"\n{\n\t"76561198000000077"\n\t{\n\t\t"AccountName"\t\t"base_user"\n\t}\n}\n',
            encoding='utf-8',
        )

        with patch.dict(
            os.environ,
            {
                'STEAM_COMPAT_CLIENT_INSTALL_PATH': '',
                'STEAM_BASE_FOLDER': str(self.client_dir),
                'SteamUser': 'base_user',
            },
        ):
            account_id = util.get_steam_account_id()
            self.assertEqual(account_id, '76561198000000077')

    def test_get_steam_account_id_case_variations(self):
        """Verifies account resolution with mixed-case fields and autologin flag."""
        config_dir = self.client_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        loginusers_vdf = config_dir / 'loginusers.vdf'
        loginusers_vdf.write_text(
            '"Users"\n'
            '{\n'
            '\t"76561198000000088"\n'
            '\t{\n'
            '\t\t"accountname"\t\t"case_user"\n'
            '\t\t"autologin"\t\t"1"\n'
            '\t}\n'
            '}\n',
            encoding='utf-8',
        )

        with patch.dict(os.environ, {'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir)}):
            os.environ.pop('SteamUser', None)
            account_id = util.get_steam_account_id()
            self.assertEqual(account_id, '76561198000000088')

    def test_get_steam_account_id_missing_env_or_file(self):
        """Verifies graceful None return when environment or file is missing."""
        with patch.dict(
            os.environ,
            {'STEAM_COMPAT_CLIENT_INSTALL_PATH': '', 'STEAM_BASE_FOLDER': ''},
        ):
            self.assertIsNone(util.get_steam_account_id())

        with patch.dict(
            os.environ,
            {
                'STEAM_COMPAT_CLIENT_INSTALL_PATH': str(self.client_dir),
                'STEAM_BASE_FOLDER': '',
            },
        ):
            self.assertIsNone(util.get_steam_account_id())


if __name__ == '__main__':
    unittest.main()
