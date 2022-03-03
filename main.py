from bs4 import BeautifulSoup
import datetime


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


def get_flights(soup):

    flight_collection = list()
    for index_request, request in enumerate(soup.find_all('flights')):

        onward_trip = request.find('onwardpriceditinerary')

        if onward_trip:
            flight = onward_trip.find_all('flight')

            data = [get_flight_data(onward) for onward in flight]
            source = data[0]['Source']
            dest = data[-1]['Destination']
            total_time = data[-1]['ArrivalTimeStr'] - data[0]['DepartureTimeStr']
            flight_collection.append({
                'onward': data,
                'source': source,
                'dest': dest,
                'total_time': total_time.total_seconds(),
            })

    return flight_collection

def get_best(flights):

    if not flights:
        return dict()

    sorted_by_time = sorted(flights, key = lambda item: item['total_time'])
    data = {
        'fast': sorted_by_time[0],
        'slow': sorted_by_time[-1]
    }
    return data


if __name__ == '__main__':

    with open('RS_ViaOW.xml', 'r') as fd:
        xml_file = fd.read()

    soup = BeautifulSoup(xml_file, 'lxml')
    print(get_best(get_flights(soup)))









