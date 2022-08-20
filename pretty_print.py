def format_duration(duration):
    total_minutes = int(duration.total_seconds()) // 60
    return f'{total_minutes//60:d}:{total_minutes%60:02d}'


def print_flight(flight):
    f = flight
    print(
        f'{f.origin.timestamp.isoformat()[:10]} {f.origin.airport} ({f.origin.localTime})->{f.destination.airport} ({f.destination.localTime})', end=' ')
    print(f'duration={format_duration(f.duration)} biz={f.businessSeats}')
    print('           ', end='')
    for s in f.segments:
        print(f'{s.origin.airport}-{s.destination.airport} ({s.carrier}{s.flightNumber}, {s.aircraft}, {format_duration(s.duration)}), ', end='')
    print()


def print_flights(flights):
    for f in sorted(flights, key=lambda f: f.origin.timestamp):
        print_flight(f)
