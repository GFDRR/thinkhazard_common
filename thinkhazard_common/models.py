from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    )

from sqlalchemy.schema import MetaData

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from geoalchemy2 import Geometry

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(metadata=MetaData(schema='datamart'))


adminleveltype_cache = {}


class AdminLevelType(Base):
    __tablename__ = 'enum_adminleveltype'

    id = Column(Integer, primary_key=True)
    mnemonic = Column(Unicode)
    title = Column(Unicode, nullable=False)
    description = Column(Unicode)

    @classmethod
    def get(cls, mnemonic):
        if mnemonic in adminleveltype_cache:
            return adminleveltype_cache[mnemonic]
        with DBSession.no_autoflush:
            adminleveltype = DBSession.query(cls) \
                .filter(cls.mnemonic == mnemonic) \
                .one_or_none()
            adminleveltype_cache[adminleveltype.mnemonic] = adminleveltype
            return adminleveltype


level_weights = {
    None: 0,
    u'VLO': 1,
    u'LOW': 2,
    u'MED': 3,
    u'HIG': 4
}


hazardlevel_cache = {}


class HazardLevel(Base):
    __tablename__ = 'enum_hazardlevel'

    id = Column(Integer, primary_key=True)
    mnemonic = Column(Unicode)
    title = Column(Unicode, nullable=False)
    order = Column(Integer)

    def __cmp__(self, other):
        if other is None:
            return 1
        return cmp(level_weights[self.mnemonic],
                   level_weights[other.mnemonic])

    @classmethod
    def get(cls, mnemonic):
        if mnemonic in hazardlevel_cache:
            return hazardlevel_cache[mnemonic]
        with DBSession.no_autoflush:
            hazardlevel = DBSession.query(cls) \
                .filter(cls.mnemonic == mnemonic) \
                .one_or_none()
            hazardlevel_cache[hazardlevel.mnemonic] = hazardlevel
            return hazardlevel


hazardtype_cache = {}


class HazardType(Base):
    __tablename__ = 'enum_hazardtype'

    id = Column(Integer, primary_key=True)
    mnemonic = Column(Unicode)
    title = Column(Unicode, nullable=False)
    order = Column(Integer)

    @classmethod
    def get(cls, mnemonic):
        if mnemonic in hazardtype_cache:
            return hazardtype_cache[mnemonic]
        with DBSession.no_autoflush:
            hazardtype = DBSession.query(cls) \
                .filter(cls.mnemonic == mnemonic) \
                .one_or_none()
            hazardtype_cache[hazardtype.mnemonic] = hazardtype
            return hazardtype


class HazardCategoryAdministrativeDivisionAssociation(Base):
    __tablename__ = 'rel_hazardcategory_administrativedivision'

    id = Column(Integer, primary_key=True)
    administrativedivision_id = Column(Integer,
                                       ForeignKey('administrativedivision.id'),
                                       nullable=False, index=True)
    hazardcategory_id = Column(Integer,
                               ForeignKey('hazardcategory.id'),
                               nullable=False, index=True)
    source = Column(Unicode, nullable=False)
    administrativedivision = relationship('AdministrativeDivision',
                                          back_populates='hazardcategories')
    hazardcategory = relationship('HazardCategory',
                                  back_populates='administrativedivisions')


class HazardCategoryTechnicalRecommendationAssociation(Base):
    __tablename__ = 'rel_hazardcategory_technicalrecommendation'
    id = Column(Integer, primary_key=True)
    hazardcategory_id = Column(Integer, ForeignKey('hazardcategory.id'),
                               nullable=False, index=True)
    technicalrecommendation_id = Column(
        Integer, ForeignKey('technicalrecommendation.id'),
        nullable=False, index=True)
    order = Column(Integer, nullable=False)

    hazardcategory = relationship('HazardCategory')


class HazardCategoryFurtherResourceAssociation(Base):
    __tablename__ = 'rel_hazardcategory_furtherresource'
    id = Column(Integer, primary_key=True)
    hazardcategory_id = Column(Integer, ForeignKey('hazardcategory.id'),
                               nullable=False, index=True)
    furtherresource_id = Column(Integer,
                                ForeignKey('furtherresource.id'),
                                nullable=False, index=True)
    order = Column(Integer, nullable=False)
    administrativedivision_id = Column(
        Integer, ForeignKey('administrativedivision.id'))

    hazardcategory = relationship('HazardCategory')
    administrativedivision = relationship('AdministrativeDivision')


class AdministrativeDivision(Base):
    __tablename__ = 'administrativedivision'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, index=True, unique=True, nullable=False)
    leveltype_id = Column(Integer, ForeignKey(AdminLevelType.id),
                          nullable=False, index=True)
    name = Column(Unicode, nullable=False)
    parent_code = Column(Integer, ForeignKey(
        'administrativedivision.code', use_alter=True,
        name='administrativedivision_parent_code_fkey'))
    geom = Column(Geometry('MULTIPOLYGON', 4326))

    leveltype = relationship(AdminLevelType)
    parent = relationship('AdministrativeDivision', uselist=False,
                          remote_side=code)
    hazardcategories = relationship(
        'HazardCategoryAdministrativeDivisionAssociation',
        back_populates='administrativedivision')

    def __json__(self, request):
        if self.leveltype_id == 1:
            return {'code': self.code,
                    'admin0': self.name}
        if self.leveltype_id == 2:
            return {'code': self.code,
                    'admin0': self.parent.name,
                    'admin1': self.name}
        if self.leveltype_id == 3:
            return {'code': self.code,
                    'admin0': self.parent.parent.name,
                    'admin1': self.parent.name,
                    'admin2': self.name}


class HazardCategory(Base):
    __tablename__ = 'hazardcategory'

    id = Column(Integer, primary_key=True)
    hazardtype_id = Column(Integer, ForeignKey(HazardType.id), nullable=False)
    hazardlevel_id = Column(Integer, ForeignKey(HazardLevel.id),
                            nullable=False)
    general_recommendation = Column(Unicode, nullable=False)

    hazardtype = relationship(HazardType)
    hazardlevel = relationship(HazardLevel)
    administrativedivisions = relationship(
        'HazardCategoryAdministrativeDivisionAssociation',
        back_populates='hazardcategory')


class ClimateChangeRecommendation(Base):
    __tablename__ = 'climatechangerecommendation'
    id = Column(Integer, primary_key=True)
    text = Column(Unicode, nullable=False)
    administrativedivision_id = Column(
        Integer, ForeignKey(AdministrativeDivision.id), nullable=False)
    hazardtype_id = Column(Integer, ForeignKey(HazardType.id), nullable=False)

    administrativedivision = relationship(AdministrativeDivision)
    hazardtype = relationship(HazardType)


class TechnicalRecommendation(Base):
    __tablename__ = 'technicalrecommendation'
    id = Column(Integer, primary_key=True)
    text = Column(Unicode, nullable=False)

    hazardcategory_associations = relationship(
        'HazardCategoryTechnicalRecommendationAssociation',
        order_by='HazardCategoryTechnicalRecommendationAssociation.order',
        lazy='joined')


class FurtherResource(Base):
    __tablename__ = 'furtherresource'
    id = Column(Integer, primary_key=True)
    text = Column(Unicode, nullable=False)
    url = Column(Unicode, nullable=False)

    hazardcategory_associations = relationship(
        'HazardCategoryFurtherResourceAssociation',
        order_by='HazardCategoryFurtherResourceAssociation.order',
        lazy='joined')
