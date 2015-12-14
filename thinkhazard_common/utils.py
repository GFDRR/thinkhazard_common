from models import HazardCategoryAdministrativeDivisionAssociation


def associate_admindiv_hazardcategory(admindiv, hazardcategory, source):
    a = HazardCategoryAdministrativeDivisionAssociation(source=source)
    a.hazardcategory = hazardcategory
    a.administrativedivision = admindiv
    admindiv.hazardcategories.append(a)
