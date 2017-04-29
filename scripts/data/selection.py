
class _WhereBuild:
    def __init__(self):
        self._values = {}
        self._ops = {}
        self._style = {}

    def add(self, name, value, op='=', stylise=None):
        self._values[name] = value
        self._ops[name] = op
        if stylise:
            self._style[name] = stylise

    def format(self):
        if not self._values:
            return (), ''

        conds = []
        formats = []

        for key, value in self._values.items():
            style = self._style[key] if key in self._style else "%s"
            conds.append("%s %s %s" % (key, self._ops[key], style))
            formats.append(value)

        if len(conds):
            return (tuple(formats), "WHERE %s " % ' AND '.join(conds))
        else:
            return (), ""

def get_api_results(flags):
    where = _WhereBuild()
    if 'file_extension' in flags and flags['file_extension']:
        where.add('file_extension', flags['file_extension'])

    if 'script_hash' in flags and flags['script_hash']:
        where.add('script_hash', flags['script_hash'], stylise=" decode(%s, 'hex' ) ")

    return _results_api_view(where)

def get_results(flags, api=False):
    where = _WhereBuild()
    if 'file_extension' in flags and flags['file_extension']:
        where.add('file_extension', flags['file_extension'])

    if api:
        table = 'results_api_latest_O2'
        avg_f = _results_api_avg_latest_o2
    else:
        avg_f = _results_readable_avg
        if 'O' in flags and int(flags['O']) == 2:
            table = 'results_latest_O2'
        else:
            table = 'results_readable'

    if 'avg' in flags:
        return avg_f(table, where)
    else:
        return _select_all_from(table, where)

def get_scripts(flags, id=None):
    where = _WhereBuild()
    if id != None:
        where.add('id', id, stylise=" decode(%s, 'hex' ) ")
    with_repr = flags['with_repr'] if 'with_repr' in flags else False
    return (_scripts_with_repr if with_repr else _scripts_without_repr)(where)

def get_package(cur, count, offset, id=None):
    where = _WhereBuild()
    if id != None:
        where.add('id', id)
    return _select_all_from('package', where)(cur, count, offset)

def get_filetypes(cur, **kwargs):
    return cur.mogrify(" SELECT * from thesis.unique_filetypes")

############################################################

def _scripts_without_repr(where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            " SELECT id, tags, last_modified FROM thesis.benchmark_script ",
            where.format(),
            " ORDER BY last_modified DESC",
        ])
    return impl

def _scripts_with_repr(where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            " SELECT id, tags, last_modified, repr FROM thesis.benchmark_script ",
            where.format(),
            " ORDER BY last_modified ",
        ])
    return impl

def _select_all_from(table, where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            (" SELECT * from thesis.%s " % table),
            where.format(),
        ])
    return impl

def _results_api_view(where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            """
                SELECT
                    package_id,
                    ghc_version,
                    file_extension,
                    average_time,
                    SUM(file_size) as file_size,
                    script_hash
                FROM thesis.results_hashed
            """,
            where.format(),
            """
                GROUP BY
                    package_id,
                    ghc_version,
                    file_extension,
                    average_time,
                    script_hash
            """,
        ])
    return impl

def _results_api_avg_latest_o2(table, where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            ("""
                SELECT
                    package_id,
                    ghc_version,
                    file_extension,
                    average_time,
                    SUM(file_size) as file_size,
                    script_hash
                FROM thesis.%s
            """ % table),
            where.format(),
            """
                GROUP BY
                    package_id,
                    ghc_version,
                    file_extension,
                    average_time,
                    script_hash
            """,
        ])
    return impl

def _results_readable_avg(table, where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            ("""
                SELECT
                    package_name,
                    ghc_version,
                    file_extension,
                    average_time,
                    SUM(file_size) as file_size,
                    script_hash,
                    script_tags,
                    script_age
                FROM thesis.%s
            """ % table),
            where.format(),
            """
                GROUP BY
                    package_name,
                    ghc_version,
                    file_extension,
                    average_time,
                    script_hash,
                    script_tags,
                    script_age
            """,
        ])
    return impl

############################################################

def format_query(cursor, count, offset, chunks):
    query = ""
    formats = tuple()
    for item in chunks:
        if isinstance(item, str):
            query += item
        elif isinstance(item, tuple):
            v, s = item
            formats += v
            query += s
        else:
            raise Exception('unknown chunk')
    if offset != None:
        query += " OFFSET %s "
        formats += (offset,)
    if count != None:
        query += " LIMIT %s "
        formats += (count,)
    return cursor.mogrify(query, formats)

