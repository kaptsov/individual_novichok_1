from bs4 import BeautifulSoup
import datetime
import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    parser.add_argument('request', nargs='+')
    return parser


def parse_date(timestamp):
    return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H%M')


def get_total_flight_time(departure_ts, arrival_ts):
    return (arrival_ts - departure_ts).total_seconds() // 60


def get_flight_data(trip):
    source = trip.find('source').text
    destination = trip.find('destination').text
    flight_number = trip.find('flightnumber').text
    carrier = trip.find('carrier').text
    departure_str = parse_date(trip.find('departuretimestamp').text)
    arrival_str = parse_date(trip.find('arrivaltimestamp').text)
    return {
        'Carrier': carrier,
        'FlightNumber': flight_number,
        'Source': source,
        'Destination': destination,
        'DepartureTimeStr': departure_str,
        'ArrivalTimeStr': arrival_str
    }


def get_price(flight):
    return float(flight.find('pricing').find(chargetype='TotalAmount').text)


def get_flights(request):

    onward_trip = request.find('onwardpriceditinerary')
    backward_trip = request.find('returnpriceditinerary')

    if not onward_trip:
        return

    onward_flight = onward_trip.find_all('flight')
    onward_data = [
        get_flight_data(onward) for onward in onward_flight
        ]
    backward_data = [
        get_flight_data(backward) for backward in backward_trip
        ] if backward_trip else list()
    source = onward_data[0]['Source']
    dest = onward_data[-1]['Destination']
    onward_time = onward_data[-1][
        'ArrivalTimeStr'
        ] - onward_data[0]['DepartureTimeStr']
    backward_time = (
        backward_data[-1]['ArrivalTimeStamp'] -
        backward_data[0]['DepartureTimeStamp']
        ) if backward_data else datetime.timedelta(0)
    return {
        'onward': onward_data,
        'backward': backward_data,
        'source': source,
        'dest': dest,
        'price': get_price(request),
        'onward_time': onward_time.total_seconds(),
        'backward_time': backward_time.total_seconds(),
        'total_time':
            onward_time.total_seconds() +
            backward_time.total_seconds(),
    }


def get_best(flights):

    if not flights:
        return dict()

    sorted_by_time = sorted(flights, key=lambda item: item['total_time'])
    sorted_by_price = sorted(flights, key=lambda item: item['price'])

    return {
        'fastest': sorted_by_time[0],
        'slowest': sorted_by_time[-1],
        'cheapest': sorted_by_price[0],
        'expensievest': sorted_by_price[-1],
        'the_best': sorted(
            flights, key=lambda item: item['total_time'] /
            sorted_by_time[0]['total_time'] * item['price']
            )[0],
    }


if __name__ == '__main__':

    parser = create_parser()
    namespace = parser.parse_args()

    with open(str(namespace.filename[0]), 'r') as fd:
        xml_file = fd.read()
    soup = BeautifulSoup(xml_file, 'lxml')

    flight_collection = list()
    for request in soup.find_all('flights'):
        if not get_flights(request):
            continue
        flight_collection.append(get_flights(request))

    print(f'The {namespace.request[0]} flight option is:')
    print(get_best(flight_collection)[namespace.request[0]])
