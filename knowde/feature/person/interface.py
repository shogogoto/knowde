"""person interface."""
from knowde._feature._shared.api.api_param import NullPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_bodyfunc
from knowde.feature.person.domain.person import Person
from knowde.feature.person.dto import PersonAddParam
from knowde.feature.person.repo.repo import add_person

person_router = Endpoint.Person.create_router()
cf = ClientFactory(router=person_router, rettype=Person)
add_client = cf.post(NullPath(), to_bodyfunc(add_person, PersonAddParam))
