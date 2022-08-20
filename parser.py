from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import dateutil


@dataclass(frozen=True)
class PlaceTime:
    airport: str
    timestamp: datetime
    localTime: str


@dataclass(frozen=True)
class Fare:
    segmentId: int
    productName: str
    bookingClass: str
    cabinName: str
    availableSeats: int

    @staticmethod
    def fromJson(json, productName):
        return Fare(
            segmentId=json['segmentId'],
            productName=productName,
            bookingClass=json['bookingClass'],
            cabinName=json['cabinName'],
            availableSeats=json['avlSeats']
        )

    def allFaresFromCabinsJson(cabin):
        fares = defaultdict(list)
        for container in cabin.values():
            assert len(container) == 1
            container = next(iter(container.values()))

            product = container['products']
            assert len(product) == 1
            product = next(iter(product.values()))

            for fareJson in product['fares']:
                fare = Fare.fromJson(fareJson, product['productName'])
                fares[fare.segmentId].append(fare)

        return fares


@dataclass(frozen=True)
class Segment:
    origin: PlaceTime
    destination: PlaceTime
    aircraft: str
    carrier: str
    flightNumber: str
    fares: list  # TODO: Make typed

    @property
    def duration(self):
        return self.destination.timestamp - self.origin.timestamp

    @property
    def biz_seats(self):
        s = 0
        for f in self.fares:
            if f.productName == 'BUSINESS':
                s += f.availableSeats
        return s

    @staticmethod
    def fromJson(json, fares):
        return Segment(
            origin=PlaceTime(
                airport=json['departureAirport']['code'],
                timestamp=dateutil.parser.isoparse(
                    json['departureDateTimeInGmt']),
                localTime=json['departureDateTimeInLocal']
            ),
            destination=PlaceTime(
                airport=json['arrivalAirport']['code'],
                timestamp=dateutil.parser.isoparse(
                    json['arrivalDateTimeInGmt']),
                localTime=json['arrivalDateTimeInLocal']
            ),
            aircraft=json['airCraft']['code'],
            carrier=json['operatingCarrier']['code'],
            flightNumber=json['flightNumber'],
            fares=fares[str(json['id'])]
        )


@dataclass(frozen=True)
class Flight:
    origin: PlaceTime
    destination: PlaceTime
    segments: list  # TODO: Make list typed?
    businessSeats: int
    economySeats: int

    @property
    def duration(self):
        return self.destination.timestamp - self.origin.timestamp

    @staticmethod
    def fromJson(json):
        fares = Fare.allFaresFromCabinsJson(json['cabins'])
        segments = [Segment.fromJson(s, fares) for s in json['segments']]

        economy_seats = 0
        if 'ECONOMY' in json['lowestFares']:
            economy_seats = json['lowestFares']['ECONOMY']['avlSeats']
        business_seats = 0
        if 'BUSINESS' in json['lowestFares']:
            business_seats = json['lowestFares']['BUSINESS']['avlSeats']

        return Flight(
            origin=PlaceTime(
                airport=json['origin']['code'],
                timestamp=dateutil.parser.isoparse(json['startTimeInGmt']),
                localTime=json['startTimeInLocal']
            ),
            destination=PlaceTime(
                airport=json['destination']['code'],
                timestamp=dateutil.parser.isoparse(json['endTimeInGmt']),
                localTime=json['endTimeInLocal']
            ),
            segments=segments,
            businessSeats=business_seats,
            economySeats=economy_seats
        )


def parse_flights(query_results):
    flights = list()
    for route, res in query_results.items():
        json = res.response.json()
        if 'outboundFlights' not in json:
            continue
        flights.extend(Flight.fromJson(f)
                       for f in json['outboundFlights'].values())
    return flights
