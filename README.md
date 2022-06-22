# Contemporary Software Development project

## Description

The project consists of a simulated apartment booking system, built following a **microservices**-based architecture.

The following services are established *(follow the links for more information)*:

- [apartments](apartments/README.md);
- [reservations](reservations/README.md);
- [search](search/README.md);
- [gateway](gateway/README.md): API gateway.

All of them are standalone Docker images implemented using **Python** (*flask* in particular). Data is persisted in service-specific **sqlite** databases, so to follow the CQRS technique. Communication within services is instead ensured thanks to RabbitMQ *(message queue)* and Consul *(service registry)*.