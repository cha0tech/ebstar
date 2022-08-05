#!/usr/bin/python3 -u

import click
import datetime
import itertools
import random
import time

from apiclient import ApiClient
from datatypes import Route
from storage import Storage


def parse_datestr(datestr):
    return datetime.date(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))


def date_range(start_date, end_date):
    start_date = parse_datestr(start_date)
    end_date = parse_datestr(end_date)
    date = start_date

    dates = []
    while date <= end_date:
        dates.append(date.isoformat().replace('-', ''))
        date += datetime.timedelta(days=1)
    return dates


def route_combinations(froms, tos, dates, and_back=True):
    for route in itertools.product(froms, tos, dates):
        yield Route(*route)
    if and_back:
        for route in itertools.product(tos, froms, dates):
            yield Route(*route)


@click.command()
@click.option('--origins')
@click.option('--destinations')
@click.option('--start', 'start_date')
@click.option('--end', 'end_date')
def main(origins, destinations, start_date, end_date):
    origins = origins.split(',')
    destinations = destinations.split(',')
    dates = date_range(start_date, end_date)

    storage = Storage('flights.db')
    client = ApiClient('headers.txt', 'cookie.txt')
    client.check_status()

    routes = route_combinations(origins, destinations, dates)
    routes = list(routes)
    random.shuffle(routes)
    while len(routes) > 0:
        route = routes[-1]
        if storage.has_valid(route):
            routes.pop()
            continue

        print(f'{route} ({len(routes)} routes left)', end=' ')
        try:
            res = client.send_request(route)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

        if res.is_valid:
            storage.add(res)
            routes.pop()
            print(f'{int(res.response.elapsed.total_seconds()*1000)} ms ✓')
        elif res.is_cookie_expired:
            client.wait_for_new_cookie()
            client.check_status()
        else:
            print('✗')
            print(res.response.status_code, res.application_errors)
            routes.pop()
            time.sleep(10)


if __name__ == '__main__':
    main()
