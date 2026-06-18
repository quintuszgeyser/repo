"""
BC-4000 field mapping diagnostic.

Sends PLU 9999 with marker=777 at each CSV field index one at a time.
After each send, reads SLP-V DB directly to see which column changed.
Requires SLP-V to have received PLU 9999 at least once before starting.

Usage:
  1. First run: python field_mapper.py --init
     This inserts a baseline PLU 9999 into SLP-V DB so we have a row to diff against.
  2. Then run:  python field_mapper.py
     This probes all field indices and prints the mapping.
"""
import struct, sys, time, pyodbc, argparse

sys.path.insert(0, '.')
from bc4000_client import send_chunk, ProtocolError

SCALE_IP   = '10.0.0.103'
SCALE_PORT = 7061
TIMEOUT    = 10
TEST_PLU   = 9999
MARKER     = 777
SLPV_DB    = r'C:\Program Files (x86)\Ishida\SLP-V\SlpNet.mdb'
MSG_NO     = 1001

WATCH_COLS = [
    'Plu_No','SalesMode','DateFlag','BestBeforeFlag','TimeFlag',
    'OpenPrice','ExpTimeFlag','ForcedTare','PackQuant','Tare','ShelfLife',
    'ExpTime','PackTime','Posflag','PosFlagSelect','ItfCodeType','ItfFlag',
    'ItemCode','PosCode','UnitPrice','FixedPrice','DescText','BarCodeNum',
    'MarkFlag','DeptCode','GroupCode','ExMessage1','ExMessage2',
    'LabelFormatNo1','LabelFormatNo2','BestBefore','TaxRate',
]


def build_baseline() -> list:
    desc = '\x0d\x0aTEST PRODUCT\x0d\x01PER KG'
    f = ['0'] * 85
    f[0]  = str(TEST_PLU)
    f[1]  = str(TEST_PLU)
    f[49] = f'"{desc}"'
    f[50] = '0'
    f[51] = '1234'
    f[52] = '1234'
    f[67] = '21'
    f[69] = '20'
    f[70] = f'"{TEST_PLU}"'
    return f


def send_plu(fields: list) -> bool:
    csv = ','.join(fields) + ','
    try:
        r = send_chunk(SCALE_IP, SCALE_PORT, TIMEOUT, MSG_NO, [csv.encode('utf-8')])
        return r['errors'] == 0
    except ProtocolError as e:
        print(f'    ProtocolError: {e}')
        return False


def slpv_conn():
    return pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={SLPV_DB};')


def read_slpv() -> dict:
    conn = slpv_conn()
    cursor = conn.cursor()
    cols = ', '.join(WATCH_COLS)
    cursor.execute(f'SELECT {cols} FROM [Plus] WHERE Plu_No = ?', (TEST_PLU,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    return dict(zip(WATCH_COLS, row))


def insert_baseline_to_slpv():
    """Insert a minimal PLU 9999 row into SLP-V DB so we have a diff baseline."""
    conn = slpv_conn()
    cursor = conn.cursor()
    # Check if exists
    cursor.execute('SELECT COUNT(*) FROM [Plus] WHERE Plu_No = ?', (TEST_PLU,))
    if cursor.fetchone()[0] > 0:
        cursor.execute('DELETE FROM [Plus] WHERE Plu_No = ?', (TEST_PLU,))
    cursor.execute(
        'INSERT INTO [Plus] (Plu_No, UnitPrice, PosCode) VALUES (?, ?, ?)',
        (TEST_PLU, 1234, '0')
    )
    conn.commit()
    conn.close()
    print(f'  Inserted baseline PLU {TEST_PLU} into SLP-V DB.')


def diff(before: dict, after: dict) -> dict:
    ignore = {'DescText', 'Plu_No'}
    return {
        k: (before.get(k), after.get(k))
        for k in after
        if after.get(k) != before.get(k) and k not in ignore
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help='Insert baseline PLU into SLP-V DB')
    args = parser.parse_args()

    if args.init:
        print('Initialising SLP-V baseline row...')
        insert_baseline_to_slpv()
        print('Done. Now run: python field_mapper.py')
        return

    print(f'BC-4000 field mapper  PLU={TEST_PLU}  marker={MARKER}')
    print(f'Scale: {SCALE_IP}:{SCALE_PORT}')
    print()

    # Confirm SLP-V row exists
    base_row = read_slpv()
    if not base_row:
        print(f'PLU {TEST_PLU} not in SLP-V DB. Run: python field_mapper.py --init first.')
        return

    # Send fresh baseline to scale and update SLP-V row
    print('Sending baseline to scale...')
    baseline = build_baseline()
    print(f'  Field count: {len(baseline)}')
    if not send_plu(baseline):
        print('  FAILED — scale rejected baseline. Check connection.')
        return
    time.sleep(0.5)

    # Read current SLP-V state as baseline
    base_row = read_slpv()
    print('  SLP-V baseline (non-zero):')
    for k, v in base_row.items():
        if v not in (0, None, '', '0', False):
            print(f'    {k}: {repr(v)}')
    print()

    # Probe each field
    results = []
    skip = {0, 1, 49, 50, 51, 52}  # structural fields we know
    print(f'Probing {len(baseline)} field indices...')

    for idx in range(len(baseline)):
        if idx in skip:
            continue

        fields = baseline[:]
        fields[idx] = str(MARKER)
        ok = send_plu(fields)
        time.sleep(0.4)

        if not ok:
            results.append((idx, 'SEND_FAILED', '-', '-'))
            print(f'  [{idx:02d}] SEND_FAILED')
            # Reset
            send_plu(baseline)
            time.sleep(0.3)
            continue

        row = read_slpv()
        changes = diff(base_row, row)

        if changes:
            for col, (old, new) in changes.items():
                results.append((idx, col, old, new))
                print(f'  [{idx:02d}]  {col}: {old!r} -> {new!r}   *** MAPPING ***')
        # Reset
        send_plu(baseline)
        time.sleep(0.3)

    # Summary
    print()
    print('=' * 65)
    print('CONFIRMED FIELD MAPPINGS:')
    print(f'  {"CSV idx":>7}  {"SLP-V column":<22}  {"old":>8}  {"new":>8}')
    print('-' * 65)
    for idx, col, old, new in results:
        if col and col != 'SEND_FAILED':
            print(f'  {idx:>7}  {col:<22}  {str(old):>8}  {str(new):>8}')
    print()
    failed = [i for i, c, _, _ in results if c == 'SEND_FAILED']
    unmapped = [i for i, c, _, _ in results if not c]
    if failed: print(f'Send failures at indices: {failed}')
    if unmapped: print(f'No SLP-V change detected at: {unmapped}')


if __name__ == '__main__':
    main()
