from ..models import (DBSession, Base,
                      AdminLevelType, HazardLevel,
                      HazardType, HazardCategory)


def initdb(engine, drop_all=False):
    if not schema_exists(engine, 'datamart'):
        engine.execute("CREATE SCHEMA datamart;")

    if drop_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    DBSession.configure(bind=engine)
    populate_datamart(engine)
    DBSession.flush()


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


def populate_datamart(engine):
    # AdminLevelType
    for i in [
        (u'COU', u'Country', u'Administrative division of level 0'),
        (u'PRO', u'Province', u'Administrative division of level 1'),
        (u'REG', u'Region', u'Administrative division of level 2'),
    ]:
        r = AdminLevelType()
        r.mnemonic, r.title, r.description = i
        DBSession.add(r)

    # HazardLevel
    for i in [
        (u'HIG', u'High', 1),
        (u'MED', u'Medium', 2),
        (u'LOW', u'Low', 3),
        (u'VLO', u'Very low', 4),
    ]:
        r = HazardLevel()
        r.mnemonic, r.title, r.order = i
        DBSession.add(r)

    # HazardType
    for i in [
        (u'FL', u'River flood', 1),
        (u'EQ', u'Earthquake', 2),
        (u'DG', u'Drought', 3),
        (u'VA', u'Volcanic ash', 7),
        (u'CY', u'Cyclone', 4),
        (u'TS', u'Tsunami', 6),
        (u'SS', u'Coastal flood', 5),
        (u'LS', u'Landslide', 8),
    ]:
        r = HazardType()
        r.mnemonic, r.title, r.order = i
        DBSession.add(r)

    # HazardCategory
    hazardlevels = DBSession.query(HazardLevel)
    for hazardtype in DBSession.query(HazardType):
        for hazardlevel in hazardlevels:
            r = HazardCategory()
            r.hazardtype = hazardtype
            r.hazardlevel = hazardlevel
            r.general_recommendation = u'General recommendation for {} {}'\
                .format(hazardtype.mnemonic, hazardlevel.mnemonic)
            DBSession.add(r)
