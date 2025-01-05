from django.db import connections
from django.db.utils import ProgrammingError


class MaterializedView(object):
    table_name = None
    source_table = None
    source_table_name = None
    indexed_fields = []
    excluded_fields = []
    rename_fields = {}

    def __init__(self):
        self.cursor = connections['public'].cursor()
        self.private_cursor = connections['default'].cursor()

    def _get_source_table_name(self):
        return "public.{}".format(self.source_table._meta.db_table) if self.source_table else self.source_table_name

    def _rename_columns(self, columns):
        renamed_columns = []
        for column in columns:
            if column in self.rename_fields:
                renamed_columns.append(f"{column} as {self.rename_fields[column]}")
            else:
                renamed_columns.append(column)
        return renamed_columns

    def _get_columns_for_table(self, source_table_name):
        # Source: http://stackoverflow.com/questions/19127561/how-to-introspect-materialized-views
        columns_query = """
            SELECT attname
            FROM pg_attribute
            WHERE attrelid = '{table_name}'::regclass
            AND attnum > 0
            AND NOT attisdropped;
        """.format(table_name=source_table_name)

        self.private_cursor.execute(columns_query)
        return [column[0] for column in self.private_cursor.fetchall()]

    def _get_columns(self):
        source_table_name = self._get_source_table_name()
        if source_table_name is None:
            raise NotImplementedError("If you want to automatically retrieve columns, specify a source table")
        columns = [column for column in self._get_columns_for_table(source_table_name) if column not in self.excluded_fields]
        return self._rename_columns(columns)

    def _create_indexes(self):
        create_string = ''
        for indexed_field in self.indexed_fields:
            create_string += 'CREATE INDEX {table_name}_{indexed_field}x ON public_access.{table_name} ({indexed_field});'.format(indexed_field=indexed_field, table_name=self.table_name)
        return create_string

    def get_query(self):
        raise NotImplementedError("Need to implement query for materialized view")

    def refresh_readonly_privileges(self):
        self.private_cursor.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public_access TO public_access_user;")

    def create(self):
        query = self.get_query()

        create_view_query = """
            CREATE MATERIALIZED VIEW public_access.{table_name}
            AS {query};
            {create_indexes}
        """.format(table_name=self.table_name, query=query, create_indexes=self._create_indexes())
        self.private_cursor.execute(create_view_query)
        self.refresh_readonly_privileges()

    def refresh(self):
        self.private_cursor.execute("REFRESH MATERIALIZED VIEW public_access.{}".format(self.table_name));

    def delete(self):
        self.private_cursor.execute("DROP MATERIALIZED VIEW public_access.{}".format(self.table_name));
        self.refresh_readonly_privileges()

class BasicView(MaterializedView):

    @property
    def table_name(self):
        return self._get_source_table_name().replace('public.', '')

    def get_query(self):
        return """
            SELECT {columns}
            FROM {table_name} tn
        """.format(table_name=self._get_source_table_name(), columns=",".join(["tn.{}".format(column) for column in self._get_columns()]))

class AggMaterializedView(MaterializedView):

    def determine_agg(self, column):
        return 'SUM({column})'.format(column=column)

    def _get_columns_for_table(self, source_table_name):
        # Source: http://stackoverflow.com/questions/19127561/how-to-introspect-materialized-views
        columns_query = """
            SELECT attname
            FROM pg_attribute
            WHERE attrelid = '{table_name}'::regclass
            AND attnum > 0
            AND NOT attisdropped  -- no dead columns
            AND attname NOT LIKE '%_id';  -- here's the difference
        """.format(table_name=source_table_name)

        self.private_cursor.execute(columns_query)
        return [column[0] for column in self.private_cursor.fetchall()]

    def _get_agg_headers(self, columns, table='', agg_prefix='agg_'):
        agg_headers = ''
        for column in columns:
            if table:
                column_name = "{table}.{name}".format(name=column, table=table)
            else:
                column_name = column
            agg_calculation = self.determine_agg(column)
            if agg_calculation:
                agg_headers += '{agg} as {agg_prefix}{column}, '.format(column=column, agg=self.determine_agg(column_name), agg_prefix=agg_prefix)

        if agg_headers:
            agg_headers = agg_headers[:-2]  # get rid of extra comma
        return agg_headers

    def get_header(self, column):
        return column

    def _get_headers(self, columns, table='', agg_prefix='agg_', prefix=''):
        headers = ''
        for column in columns:
            column_name = ''
            if table:
                column_name += table + '.'
            if agg_prefix:
                column_name += agg_prefix
            column_name += column
            headers += '{header} as {column}, '.format(header=self.get_header(column_name), column="{prefix}{column}".format(prefix=prefix, column=column))

        if headers:
            headers = headers[:-2]  # get rid of extra comma
        return headers
