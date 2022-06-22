# Reservations

The following routes are exposed by the service:

- `add?app_id&start&duration`: add a new reservation for the given apartment_id, starting from a specific date *(the format is `YYYYMMDD`)* and for the specified number of days. An error is returned whether the apartment is already booked for the period;
- `delete?id`: delete the reservation with corresponding id;
- `reservations`: show the list of saved reservations (optionally, one could specify `size` and `page`).

The service listens for `apartments` events, and also publishes `added` and `deleted` events in the `reservations` rabbit queue.