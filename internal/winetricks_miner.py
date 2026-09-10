"""The pig"""

import io
import json
import re
from pathlib import Path
from subprocess import Popen, PIPE

if __name__ == '__main__':
    cmd = (
        Path(__file__).parent.parent.joinpath('winetricks').as_posix(),
        'dlls',
        'list',
    )
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    dll_verbs = set()
    for line in io.TextIOWrapper(proc.stdout, encoding='utf-8'):
        verb = line.strip().split()[0]
        dll_verbs.add(verb)

    # pprint(dll_verbs)

    dlloverrides = {}
    generic_pat = re.compile(
        r'w_override_dlls (native|builtin|disabled|native,builtin) ([\w \-]+)[ ;]*\n'
    )
    variable_pat = re.compile(
        r'w_override_dlls (native|builtin|disabled|native,builtin) \$\{[a-z]+}[ ;]*\n'
    )
    dxvk_pat = re.compile(
        r'helper_dxvk(?:_nvapi)? \"\$\{[a-z0-9]+}\" \".*\" \"([\w,]+)\"\n'
    )
    d3dx9_xx_pat = re.compile(r'helper_d3dx9_xx ([0-9]+)\n')
    for verb in dll_verbs:
        cmd = f'source {Path(__file__).parent.parent.joinpath("winetricks").as_posix()} list -q && type load_{verb}'
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        out, err = out.decode(encoding='utf-8'), err.decode('utf-8')

        verb_overrides = {}

        generic_matches = tuple(generic_pat.finditer(out))
        for match in generic_matches:
            override, dlls = match.groups()
            for dll in dlls.split():
                verb_overrides[dll] = override

        variable_matches = tuple(variable_pat.finditer(out))
        for match in variable_matches:
            override = match.groups()[0]
            verb_overrides[verb] = override

        dxvk_matches = tuple(dxvk_pat.finditer(out))
        for match in dxvk_matches:
            dlls = match.groups()[0]
            for dll in dlls.split(','):
                verb_overrides[dll] = 'native'

        d3dx9_xx_matches = tuple(d3dx9_xx_pat.finditer(out))
        for match in d3dx9_xx_matches:
            suffix = match.groups()[0]
            dll = f'd3dx9_{suffix}'
            verb_overrides[dll] = 'native'

        if not verb_overrides:
            continue

        dlloverrides[verb] = verb_overrides

    with open('dlloverrides.json', 'w', encoding='utf-8') as ov_fd:
        ov_fd.write(json.dumps(dlloverrides, indent=2))
