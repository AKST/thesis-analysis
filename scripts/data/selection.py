class _WhereBuild:
    def __init__(self):
        self._values = {}
        self._ops = {}

    def add(self, name, value, op='='):
        self._values[name] = value
        self._ops[name] = op

    def format(self):
        if not self._values:
            return (), ''

        conds = []
        formats = []

        for key, value in self._values.items():
            conds.append("%s %s %%s" % (key, self._ops[key]))
            formats.append(value)

        if len(conds):
            return (tuple(formats), "WHERE %s " % ' AND '.join(conds))
        else:
            return (), ""

def get_results(flags, api=False):
    where = _WhereBuild()
    if 'file_extension' in flags:
        where.add('file_extension', flags['file_extension'])

    if api:
        table = 'results_api_latest_O2'
        avg_f = _results_api_avg
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

############################################################

def scripts_with_repr(cur, count, offset):
    return cur.mogrify("""
        select id, tags, repr from thesis.benchmark_script
        OFFSET %s LIMIT %s
    """, (offset, count))

def scripts_without_repr(cur, count, offset):
    return cur.mogrify("""
        select id, tags from thesis.benchmark_script
        OFFSET %s LIMIT %s
    """, (offset, count))

def _select_all_from(table, where):
    def impl(cursor, count, offset):
        return format_query(cursor, count, offset, [
            (" SELECT * from thesis.%s " % table),
            where.format(),
        ])
    return impl

def _results_api_avg(table, where):
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

