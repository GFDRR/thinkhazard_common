from ..models import Base


def initdb(engine, drop_all=False):
    if not schema_exists(engine, 'datamart'):
        engine.execute("CREATE SCHEMA datamart;")
    if drop_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def schema_exists(engine, schema_name):
    connection = engine.connect()
    sql = '''
SELECT count(*) AS count
FROM information_schema.schemata
WHERE schema_name = '{}';
'''.format(schema_name)
    result = connection.execute(sql)
    row = result.first()
    return row[0] == 1
