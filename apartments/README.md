# Apartments

The following routes are exposed by the service:

- `add?name&size`: add a new apartment with defined name and size (square meters);
- `delete?name`: delete the apartment with corresponding name;
- `apartments`: show the list of saved apartments (optionally, one could specify `size` and `page`).

`added` and `deleted` events are published in the `apartments` rabbit queue.